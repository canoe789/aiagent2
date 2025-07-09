#!/bin/bash
#
# HELIX Zombie Task Fix Script
# Purpose: Fix detected zombie tasks by marking them properly
# Usage: ./scripts/fix-zombie-tasks.sh [task_id] [action]
# Actions: mark_zombie, force_complete, restart_job
#

set -e

TASK_ID=$1
ACTION=${2:-"mark_zombie"}

if [ -z "$TASK_ID" ]; then
    echo "❌ ERROR: Task ID is required" >&2
    echo "Usage: $0 <task_id> [action]" >&2
    echo "Actions: mark_zombie, force_complete, restart_job" >&2
    exit 1
fi

echo "🛠️  HELIX Zombie Task Fix" >&2
echo "===============================================" >&2
echo "Task ID: $TASK_ID" >&2
echo "Action: $ACTION" >&2
echo "===============================================" >&2

# Check database connectivity
if ! docker exec helix_postgres pg_isready -U helix_user > /dev/null 2>&1; then
    echo "❌ ERROR: Database not available" >&2
    exit 1
fi

# Function to execute SQL and return JSON result
execute_sql() {
    local sql="$1"
    docker exec helix_postgres psql -U helix_user -d helix -t -c "$sql" 2>/dev/null
}

# Get task details first
TASK_INFO=$(execute_sql "
SELECT json_build_object(
    'task_id', id,
    'job_id', job_id,
    'agent_id', agent_id,
    'status', status,
    'error_log', error_log,
    'created_at', created_at,
    'updated_at', updated_at
) FROM tasks WHERE id = $TASK_ID;
")

if [ "$TASK_INFO" = "" ] || [ "$TASK_INFO" = "null" ]; then
    echo "❌ ERROR: Task $TASK_ID not found" >&2
    exit 1
fi

echo "📋 Task Details:" >&2
echo "$TASK_INFO" >&2
echo >&2

case $ACTION in
    "mark_zombie")
        echo "🏷️  Marking task as zombie..." >&2
        RESULT=$(execute_sql "
        UPDATE tasks 
        SET status = 'FAILED',
            error_log = COALESCE(error_log, '') || '[ZOMBIE_TASK_DETECTED_' || NOW() || ']',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = $TASK_ID
        RETURNING json_build_object(
            'action', 'mark_zombie',
            'task_id', id,
            'new_status', status,
            'updated_at', updated_at
        );
        ")
        ;;
        
    "force_complete")
        echo "✅ Force completing task..." >&2
        RESULT=$(execute_sql "
        UPDATE tasks 
        SET status = 'ORCHESTRATED',
            error_log = COALESCE(error_log, '') || '[FORCE_COMPLETED_' || NOW() || ']',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = $TASK_ID
        RETURNING json_build_object(
            'action', 'force_complete',
            'task_id', id,
            'new_status', status,
            'updated_at', updated_at
        );
        ")
        ;;
        
    "restart_job")
        echo "🔄 Restarting associated job..." >&2
        RESULT=$(execute_sql "
        WITH job_info AS (
            SELECT job_id FROM tasks WHERE id = $TASK_ID
        ),
        job_restart AS (
            UPDATE jobs 
            SET status = 'PENDING',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = (SELECT job_id FROM job_info)
            RETURNING id, status
        ),
        task_cleanup AS (
            UPDATE tasks 
            SET status = 'FAILED',
                error_log = COALESCE(error_log, '') || '[JOB_RESTARTED_' || NOW() || ']'
            WHERE job_id = (SELECT job_id FROM job_info)
            RETURNING COUNT(*) as affected_tasks
        )
        SELECT json_build_object(
            'action', 'restart_job',
            'job_id', (SELECT id FROM job_restart),
            'job_status', (SELECT status FROM job_restart),
            'affected_tasks', (SELECT affected_tasks FROM task_cleanup)
        );
        ")
        ;;
        
    *)
        echo "❌ ERROR: Unknown action: $ACTION" >&2
        echo "Available actions: mark_zombie, force_complete, restart_job" >&2
        exit 1
        ;;
esac

echo "🎯 Fix Result:" >&2
echo "$RESULT" >&2

# Also output clean JSON for programmatic use
echo "$RESULT"

echo "✅ Zombie task fix completed at $(date)" >&2