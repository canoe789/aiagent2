#!/bin/bash
#
# HELIX System Health Check Script
# Purpose: Comprehensive system health monitoring
# Usage: ./scripts/check-system-health.sh [--format json|human] [--threshold-cpu 80] [--threshold-memory 80]
# Output: System health status with resource usage and service status
#

set -e

# Default values
FORMAT="human"
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80
DB_POOL_THRESHOLD=80

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --threshold-cpu)
            CPU_THRESHOLD="$2"
            shift 2
            ;;
        --threshold-memory)
            MEMORY_THRESHOLD="$2"
            shift 2
            ;;
        --threshold-db-pool)
            DB_POOL_THRESHOLD="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

if [ "$FORMAT" != "human" ]; then
    # Suppress stderr for JSON output
    exec 2>/dev/null
fi

echo "🏥 HELIX System Health Check" >&2
echo "===============================================" >&2
echo "CPU Threshold: ${CPU_THRESHOLD}%" >&2
echo "Memory Threshold: ${MEMORY_THRESHOLD}%" >&2
echo "DB Pool Threshold: ${DB_POOL_THRESHOLD}%" >&2
echo "===============================================" >&2

# Function to get system metrics
get_system_metrics() {
    # CPU usage
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    
    # Memory usage
    MEMORY_INFO=$(free | grep Mem)
    MEMORY_TOTAL=$(echo $MEMORY_INFO | awk '{print $2}')
    MEMORY_USED=$(echo $MEMORY_INFO | awk '{print $3}')
    MEMORY_USAGE=$((MEMORY_USED * 100 / MEMORY_TOTAL))
    
    # Disk usage for current directory
    DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    
    # Process count for HELIX
    HELIX_PROCESSES=$(ps aux | grep -E "(start_system|orchestrator|worker)" | grep -v grep | wc -l)
    
    echo "CPU_USAGE=$CPU_USAGE"
    echo "MEMORY_USAGE=$MEMORY_USAGE"
    echo "DISK_USAGE=$DISK_USAGE"
    echo "HELIX_PROCESSES=$HELIX_PROCESSES"
}

# Function to check database health
check_database_health() {
    if docker exec helix_postgres pg_isready -U helix_user > /dev/null 2>&1; then
        # Get database stats
        DB_STATS=$(docker exec helix_postgres psql -U helix_user -d helix -t -c "
        SELECT json_build_object(
            'status', 'healthy',
            'total_tasks', (SELECT COUNT(*) FROM tasks),
            'pending_tasks', (SELECT COUNT(*) FROM tasks WHERE status = 'PENDING'),
            'completed_tasks', (SELECT COUNT(*) FROM tasks WHERE status = 'COMPLETED'),
            'failed_tasks', (SELECT COUNT(*) FROM tasks WHERE status = 'FAILED'),
            'active_jobs', (SELECT COUNT(*) FROM jobs WHERE status = 'IN_PROGRESS'),
            'connection_count', (SELECT count(*) FROM pg_stat_activity WHERE state = 'active')
        );
        " 2>/dev/null | tr -d ' \n\t')
        echo "DB_STATUS=healthy"
        echo "DB_STATS=$DB_STATS"
    else
        echo "DB_STATUS=unhealthy"
        echo "DB_STATS={\"status\": \"unhealthy\", \"error\": \"Connection failed\"}"
    fi
}

# Function to check API health
check_api_health() {
    # Try to find API port from .env
    API_PORT=$(grep "^API_PORT=" .env 2>/dev/null | cut -d'=' -f2 || echo "8000")
    
    if curl -s -f "http://localhost:${API_PORT}/api/v1/health" > /dev/null 2>&1; then
        API_RESPONSE=$(curl -s "http://localhost:${API_PORT}/api/v1/health" 2>/dev/null)
        echo "API_STATUS=healthy"
        echo "API_PORT=$API_PORT"
        echo "API_RESPONSE=$API_RESPONSE"
    else
        echo "API_STATUS=unhealthy"
        echo "API_PORT=$API_PORT"
        echo "API_RESPONSE={\"status\": \"unhealthy\", \"error\": \"Connection failed\"}"
    fi
}

# Collect all metrics
echo "📊 Collecting system metrics..." >&2
eval $(get_system_metrics)

echo "🗄️  Checking database health..." >&2
eval $(check_database_health)

echo "🌐 Checking API health..." >&2
eval $(check_api_health)

# Determine overall status
OVERALL_STATUS="healthy"
ALERTS=()

if [ "${CPU_USAGE%.*}" -gt "$CPU_THRESHOLD" ]; then
    OVERALL_STATUS="warning"
    ALERTS+=("High CPU usage: ${CPU_USAGE}%")
fi

if [ "$MEMORY_USAGE" -gt "$MEMORY_THRESHOLD" ]; then
    OVERALL_STATUS="warning"  
    ALERTS+=("High memory usage: ${MEMORY_USAGE}%")
fi

if [ "$DB_STATUS" != "healthy" ]; then
    OVERALL_STATUS="critical"
    ALERTS+=("Database unhealthy")
fi

if [ "$API_STATUS" != "healthy" ]; then
    OVERALL_STATUS="critical"
    ALERTS+=("API unhealthy")
fi

if [ "$HELIX_PROCESSES" -eq 0 ]; then
    OVERALL_STATUS="critical"
    ALERTS+=("No HELIX processes running")
fi

# Output results
if [ "$FORMAT" = "json" ]; then
    # JSON output for programmatic use
    cat << EOF
{
    "timestamp": "$(date -Iseconds)",
    "overall_status": "$OVERALL_STATUS",
    "alerts": [$(printf '"%s",' "${ALERTS[@]}" | sed 's/,$//')],
    "system": {
        "cpu_usage": $CPU_USAGE,
        "memory_usage": $MEMORY_USAGE,
        "disk_usage": $DISK_USAGE,
        "helix_processes": $HELIX_PROCESSES
    },
    "database": $DB_STATS,
    "api": {
        "status": "$API_STATUS",
        "port": $API_PORT,
        "response": $API_RESPONSE
    },
    "thresholds": {
        "cpu": $CPU_THRESHOLD,
        "memory": $MEMORY_THRESHOLD,
        "db_pool": $DB_POOL_THRESHOLD
    }
}
EOF
else
    # Human-readable output
    echo >&2
    echo "📋 HELIX SYSTEM HEALTH REPORT" >&2
    echo "===============================================" >&2
    echo "🕒 Timestamp: $(date)" >&2
    echo "🎯 Overall Status: $OVERALL_STATUS" >&2
    echo >&2
    echo "💻 System Resources:" >&2
    echo "   CPU Usage: ${CPU_USAGE}%" >&2
    echo "   Memory Usage: ${MEMORY_USAGE}%" >&2
    echo "   Disk Usage: ${DISK_USAGE}%" >&2
    echo "   HELIX Processes: $HELIX_PROCESSES" >&2
    echo >&2
    echo "🗄️  Database Status: $DB_STATUS" >&2
    echo "🌐 API Status: $API_STATUS (Port: $API_PORT)" >&2
    echo >&2
    
    if [ ${#ALERTS[@]} -gt 0 ]; then
        echo "⚠️  Alerts:" >&2
        for alert in "${ALERTS[@]}"; do
            echo "   • $alert" >&2
        done
    else
        echo "✅ No alerts - system healthy" >&2
    fi
    echo "===============================================" >&2
fi