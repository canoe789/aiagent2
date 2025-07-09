#!/bin/bash
#
# HELIX Zombie Task Detection Script
# Purpose: Detect tasks that are being processed repeatedly (zombie tasks)
# Usage: ./scripts/detect-zombie-tasks.sh [time_window_minutes] [threshold_count]
# Output: JSON format with detected zombie tasks
#

set -e

TIME_WINDOW=${1:-5}  # Default 5 minutes
THRESHOLD=${2:-3}    # Default 3 repetitions

echo "🔍 HELIX Zombie Task Detection" >&2
echo "===============================================" >&2
echo "Time window: ${TIME_WINDOW} minutes" >&2
echo "Threshold: ${THRESHOLD} repetitions" >&2
echo "===============================================" >&2

# Check if database is available
if ! docker exec helix_postgres pg_isready -U helix_user > /dev/null 2>&1; then
    echo "❌ ERROR: Database not available" >&2
    exit 1
fi

# SQL to detect zombie tasks
ZOMBIE_QUERY="
WITH task_processing_count AS (
    SELECT 
        t.id,
        t.agent_id,
        t.status,
        COUNT(*) as processing_count,
        MAX(t.updated_at) as last_updated,
        EXTRACT(EPOCH FROM (NOW() - MIN(t.updated_at))) / 60 as time_span_minutes
    FROM tasks t
    JOIN jobs j ON t.job_id = j.id
    WHERE t.updated_at >= NOW() - INTERVAL '${TIME_WINDOW} minutes'
        AND j.status = 'IN_PROGRESS'
        AND (t.error_log LIKE '%[ORCHESTRATED]%' OR t.status = 'COMPLETED')
    GROUP BY t.id, t.agent_id, t.status
    HAVING COUNT(*) >= ${THRESHOLD}
)
SELECT 
    json_agg(
        json_build_object(
            'task_id', id,
            'agent_id', agent_id,
            'status', status,
            'processing_count', processing_count,
            'last_updated', last_updated,
            'time_span_minutes', time_span_minutes,
            'severity', CASE 
                WHEN processing_count >= 10 THEN 'P0'
                WHEN processing_count >= 5 THEN 'P1'
                ELSE 'P2'
            END
        )
    ) as zombie_tasks
FROM task_processing_count;
"

# Execute query and format output
RESULT=$(docker exec helix_postgres psql -U helix_user -d helix -t -c "$ZOMBIE_QUERY" 2>/dev/null | tr -d ' \n\t')

if [ "$RESULT" = "null" ] || [ -z "$RESULT" ]; then
    echo '{"zombie_tasks": [], "status": "clean", "message": "No zombie tasks detected"}' 
    echo "✅ No zombie tasks detected" >&2
else
    echo "$RESULT"
    echo "⚠️  Zombie tasks detected! Check output for details" >&2
fi

echo "Detection completed at $(date)" >&2