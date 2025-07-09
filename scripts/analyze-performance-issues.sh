#!/bin/bash
#
# HELIX Performance Issue Analyzer
# Purpose: Detect and analyze performance bottlenecks
# Usage: ./scripts/analyze-performance-issues.sh [--time-window 60] [--slow-query-threshold 2000]
# Output: Performance analysis with specific recommendations
#

set -e

# Default values
TIME_WINDOW=60      # minutes
SLOW_QUERY_THRESHOLD=2000  # milliseconds
MEMORY_LEAK_THRESHOLD=10   # % growth per hour

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --time-window)
            TIME_WINDOW="$2"
            shift 2
            ;;
        --slow-query-threshold)
            SLOW_QUERY_THRESHOLD="$2"
            shift 2
            ;;
        --memory-leak-threshold)
            MEMORY_LEAK_THRESHOLD="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

echo "🔍 HELIX Performance Analysis" >&2
echo "===============================================" >&2
echo "Time Window: ${TIME_WINDOW} minutes" >&2
echo "Slow Query Threshold: ${SLOW_QUERY_THRESHOLD}ms" >&2
echo "Memory Leak Threshold: ${MEMORY_LEAK_THRESHOLD}% per hour" >&2
echo "===============================================" >&2

# Function to analyze database performance
analyze_database_performance() {
    if ! docker exec helix_postgres pg_isready -U helix_user > /dev/null 2>&1; then
        echo '{"db_analysis": {"status": "unavailable", "error": "Database not accessible"}}'
        return
    fi

    # Analyze slow queries, table bloat, and connection issues
    DB_ANALYSIS=$(docker exec helix_postgres psql -U helix_user -d helix -t -c "
    WITH slow_queries AS (
        SELECT 
            query,
            calls,
            total_time,
            mean_time,
            rows
        FROM pg_stat_statements 
        WHERE mean_time > $SLOW_QUERY_THRESHOLD
        ORDER BY mean_time DESC 
        LIMIT 5
    ),
    table_stats AS (
        SELECT 
            schemaname,
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_rows,
            n_dead_tup as dead_rows,
            CASE 
                WHEN n_live_tup > 0 
                THEN round((n_dead_tup::float / n_live_tup::float) * 100, 2)
                ELSE 0 
            END as bloat_ratio
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
    ),
    connection_stats AS (
        SELECT 
            state,
            COUNT(*) as connection_count
        FROM pg_stat_activity 
        GROUP BY state
    ),
    lock_stats AS (
        SELECT 
            mode,
            COUNT(*) as lock_count
        FROM pg_locks l
        JOIN pg_stat_activity a ON l.pid = a.pid
        WHERE l.granted = false
        GROUP BY mode
    )
    SELECT json_build_object(
        'slow_queries', (SELECT json_agg(slow_queries) FROM slow_queries),
        'table_stats', (SELECT json_agg(table_stats) FROM table_stats),
        'connection_stats', (SELECT json_agg(connection_stats) FROM connection_stats),
        'lock_stats', (SELECT json_agg(lock_stats) FROM lock_stats),
        'analysis_time', NOW()
    );
    " 2>/dev/null | tr -d ' \n\t')

    echo "DB_ANALYSIS='$DB_ANALYSIS'"
}

# Function to analyze task processing performance
analyze_task_performance() {
    if ! docker exec helix_postgres pg_isready -U helix_user > /dev/null 2>&1; then
        echo '{"task_analysis": {"status": "unavailable"}}'
        return
    fi

    TASK_ANALYSIS=$(docker exec helix_postgres psql -U helix_user -d helix -t -c "
    WITH task_timing AS (
        SELECT 
            agent_id,
            AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_processing_time,
            COUNT(*) as task_count,
            COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_count,
            COUNT(CASE WHEN EXTRACT(EPOCH FROM (updated_at - created_at)) > 300 THEN 1 END) as slow_count
        FROM tasks 
        WHERE created_at >= NOW() - INTERVAL '${TIME_WINDOW} minutes'
        GROUP BY agent_id
    ),
    queue_depth AS (
        SELECT 
            agent_id,
            COUNT(*) as pending_tasks
        FROM tasks 
        WHERE status = 'PENDING'
        GROUP BY agent_id
    ),
    error_patterns AS (
        SELECT 
            error_log,
            COUNT(*) as error_count
        FROM tasks 
        WHERE status = 'FAILED' 
            AND error_log IS NOT NULL
            AND created_at >= NOW() - INTERVAL '${TIME_WINDOW} minutes'
        GROUP BY error_log
        ORDER BY error_count DESC
        LIMIT 5
    )
    SELECT json_build_object(
        'task_timing', (SELECT json_agg(task_timing) FROM task_timing),
        'queue_depth', (SELECT json_agg(queue_depth) FROM queue_depth),
        'error_patterns', (SELECT json_agg(error_patterns) FROM error_patterns)
    );
    " 2>/dev/null | tr -d ' \n\t')

    echo "TASK_ANALYSIS='$TASK_ANALYSIS'"
}

# Function to check for LIKE query performance issues
analyze_like_queries() {
    if ! docker exec helix_postgres pg_isready -U helix_user > /dev/null 2>&1; then
        echo '{"like_analysis": {"status": "unavailable"}}'
        return
    fi

    LIKE_ANALYSIS=$(docker exec helix_postgres psql -U helix_user -d helix -t -c "
    WITH like_queries AS (
        SELECT 
            query,
            calls,
            total_time,
            mean_time
        FROM pg_stat_statements 
        WHERE query LIKE '%LIKE%'
            AND query LIKE '%error_log%'
            AND mean_time > 100  -- queries taking more than 100ms
        ORDER BY mean_time DESC
    ),
    table_scans AS (
        SELECT 
            schemaname,
            tablename,
            seq_scan,
            seq_tup_read,
            idx_scan,
            idx_tup_fetch,
            CASE 
                WHEN idx_scan > 0 
                THEN round((seq_scan::float / (seq_scan + idx_scan)::float) * 100, 2)
                ELSE 100.0
            END as seq_scan_ratio
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
            AND tablename = 'tasks'
    )
    SELECT json_build_object(
        'problematic_like_queries', (SELECT json_agg(like_queries) FROM like_queries),
        'table_scan_ratio', (SELECT json_agg(table_scans) FROM table_scans)
    );
    " 2>/dev/null | tr -d ' \n\t')

    echo "LIKE_ANALYSIS='$LIKE_ANALYSIS'"
}

# Function to check system resource trends
analyze_resource_trends() {
    # Get process information for HELIX components
    HELIX_PIDS=$(ps aux | grep -E "(start_system|orchestrator|worker)" | grep -v grep | awk '{print $2}' | tr '\n' ' ')
    
    if [ -z "$HELIX_PIDS" ]; then
        echo "RESOURCE_ANALYSIS={\"status\": \"no_processes\", \"message\": \"No HELIX processes found\"}"
        return
    fi

    # Memory usage for HELIX processes
    MEMORY_USAGE=$(ps -o pid,rss,vsz,cmd -p $HELIX_PIDS 2>/dev/null | tail -n +2)
    TOTAL_RSS=$(echo "$MEMORY_USAGE" | awk '{sum += $2} END {print sum}')
    TOTAL_VSZ=$(echo "$MEMORY_USAGE" | awk '{sum += $3} END {print sum}')

    # CPU usage (approximation from load average)
    LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')

    RESOURCE_ANALYSIS=$(cat << EOF
{
    "total_memory_rss_kb": ${TOTAL_RSS:-0},
    "total_memory_vsz_kb": ${TOTAL_VSZ:-0},
    "load_average": "${LOAD_AVG:-0.0}",
    "process_count": $(echo "$HELIX_PIDS" | wc -w),
    "analysis_time": "$(date -Iseconds)"
}
EOF
)

    # Output as variable assignment without quotes around the JSON
    echo "RESOURCE_ANALYSIS='$RESOURCE_ANALYSIS'"
}

# Collect all analyses
echo "📊 Analyzing database performance..." >&2
eval $(analyze_database_performance)

echo "⚙️  Analyzing task processing..." >&2
eval $(analyze_task_performance)

echo "🔍 Analyzing LIKE query performance..." >&2
eval $(analyze_like_queries)

echo "💻 Analyzing resource trends..." >&2
eval $(analyze_resource_trends)

# Generate recommendations
generate_recommendations() {
    local recommendations=()
    
    # Check for slow LIKE queries
    if echo "$LIKE_ANALYSIS" | grep -q "problematic_like_queries"; then
        recommendations+=("HIGH: Replace LIKE queries on error_log with dedicated status columns")
        recommendations+=("MEDIUM: Add indexes for commonly queried columns")
    fi
    
    # Check for high failure rates
    if echo "$TASK_ANALYSIS" | grep -q "failed_count"; then
        recommendations+=("HIGH: Investigate recurring error patterns in task processing")
        recommendations+=("MEDIUM: Implement circuit breaker for failing agents")
    fi
    
    # Check for table bloat
    if echo "$DB_ANALYSIS" | grep -q "bloat_ratio"; then
        recommendations+=("MEDIUM: Consider VACUUM ANALYZE on tables with high bloat ratio")
    fi
    
    # Check for connection issues
    if echo "$DB_ANALYSIS" | grep -q "connection_stats"; then
        recommendations+=("LOW: Monitor database connection pool usage")
    fi
    
    # Output recommendations as JSON array
    printf '['
    for i in "${!recommendations[@]}"; do
        printf '"%s"' "${recommendations[$i]}"
        if [ $i -lt $((${#recommendations[@]} - 1)) ]; then
            printf ','
        fi
    done
    printf ']'
}

RECOMMENDATIONS=$(generate_recommendations)

# Output final analysis
cat << EOF
{
    "timestamp": "$(date -Iseconds)",
    "time_window_minutes": $TIME_WINDOW,
    "database_analysis": $DB_ANALYSIS,
    "task_analysis": $TASK_ANALYSIS,
    "like_query_analysis": $LIKE_ANALYSIS,
    "resource_analysis": $RESOURCE_ANALYSIS,
    "recommendations": $RECOMMENDATIONS
}
EOF

echo "✅ Performance analysis completed" >&2