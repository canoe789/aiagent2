#!/bin/bash
#
# HELIX Emergency Recovery Script
# Purpose: Emergency system recovery with SSH safety
# Usage: ./scripts/emergency-recovery.sh [--action restart|cleanup|reset] [--force]
# This script follows SSH-safe procedures to avoid lockouts
#

set -e

# Default values
ACTION="restart"
FORCE_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --action)
            ACTION="$2"
            shift 2
            ;;
        --force)
            FORCE_MODE=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: $0 [--action restart|cleanup|reset] [--force]" >&2
            exit 1
            ;;
    esac
done

echo "🚨 HELIX Emergency Recovery" >&2
echo "===============================================" >&2
echo "Action: $ACTION" >&2
echo "Force Mode: $FORCE_MODE" >&2
echo "===============================================" >&2

# SSH Safety Check Function
ssh_safety_check() {
    echo "🔒 Performing SSH safety verification..." >&2
    if ! netstat -tuln | grep -q ":22 "; then
        echo "🚨 CRITICAL: SSH service not detected on port 22" >&2
        echo "🛑 ABORT: Cannot proceed with system operations without SSH safety" >&2
        echo '{"status": "aborted", "reason": "ssh_unsafe", "message": "SSH service not running"}' 
        exit 1
    fi
    echo "✅ SSH service confirmed active on port 22" >&2
}

# Function to safely identify HELIX processes
identify_helix_processes() {
    echo "🔍 Identifying HELIX processes safely..." >&2
    
    HELIX_PIDS=$(ps aux | grep -E "/home/canoezhang/Projects/aiagent.*python.*start_system.py" | grep -v grep | awk '{print $2}' | tr '\n' ' ')
    
    if [ -n "$HELIX_PIDS" ]; then
        echo "📋 Found HELIX processes: $HELIX_PIDS" >&2
        echo "🔍 Verifying each process..." >&2
        
        for PID in $HELIX_PIDS; do
            PROC_CMD=$(ps -p "$PID" -o cmd= 2>/dev/null || echo "")
            if echo "$PROC_CMD" | grep -q "start_system.py"; then
                echo "✅ Verified HELIX process $PID: $PROC_CMD" >&2
            else
                echo "⚠️  Skipping non-HELIX process $PID" >&2
                HELIX_PIDS=$(echo "$HELIX_PIDS" | sed "s/$PID//g")
            fi
        done
    else
        echo "ℹ️  No HELIX processes found running" >&2
    fi
    
    echo "VERIFIED_PIDS=$HELIX_PIDS"
}

# Function to safely terminate HELIX processes
safe_terminate_processes() {
    local pids="$1"
    local results=()
    
    if [ -z "$pids" ]; then
        echo "ℹ️  No processes to terminate" >&2
        return 0
    fi
    
    echo "🛑 Safely terminating HELIX processes..." >&2
    
    for PID in $pids; do
        if kill -TERM "$PID" 2>/dev/null; then
            echo "✅ Sent TERM signal to process $PID" >&2
            results+=("$PID:terminated")
        else
            echo "⚠️  Failed to terminate process $PID (may already be dead)" >&2
            results+=("$PID:failed")
        fi
    done
    
    # Wait for graceful shutdown
    echo "⏱️  Waiting 5 seconds for graceful shutdown..." >&2
    sleep 5
    
    # Check if any processes are still running
    local still_running=""
    for PID in $pids; do
        if kill -0 "$PID" 2>/dev/null; then
            still_running="$still_running $PID"
        fi
    done
    
    # Force kill if necessary and force mode is enabled
    if [ -n "$still_running" ] && [ "$FORCE_MODE" = true ]; then
        echo "🚨 Force killing remaining processes: $still_running" >&2
        for PID in $still_running; do
            if kill -KILL "$PID" 2>/dev/null; then
                echo "💀 Force killed process $PID" >&2
                results+=("$PID:force_killed")
            fi
        done
    elif [ -n "$still_running" ]; then
        echo "⚠️  Some processes still running: $still_running" >&2
        echo "💡 Use --force to force kill remaining processes" >&2
        results+=("remaining:$still_running")
    fi
    
    # Final SSH safety check
    ssh_safety_check
    
    printf '%s\n' "${results[@]}"
}

# Function to cleanup system resources
cleanup_system_resources() {
    echo "🧹 Cleaning up system resources..." >&2
    
    local cleanup_results=()
    
    # Clear temporary files
    if [ -d "./tmp" ]; then
        find ./tmp -type f -mtime +1 -delete 2>/dev/null || true
        cleanup_results+=("temp_files:cleaned")
    fi
    
    # Clear log files (keep last 100 lines)
    for logfile in *.log; do
        if [ -f "$logfile" ]; then
            tail -100 "$logfile" > "${logfile}.tmp" && mv "${logfile}.tmp" "$logfile"
            cleanup_results+=("log_$logfile:truncated")
        fi
    done
    
    # Database cleanup (if accessible)
    if docker exec helix_postgres pg_isready -U helix_user > /dev/null 2>&1; then
        echo "🗄️  Performing database cleanup..." >&2
        
        # Mark old zombie tasks
        ZOMBIE_COUNT=$(docker exec helix_postgres psql -U helix_user -d helix -t -c "
        UPDATE tasks 
        SET status = 'FAILED', 
            error_log = COALESCE(error_log, '') || '[EMERGENCY_CLEANUP_' || NOW() || ']'
        WHERE (error_log LIKE '%[ORCHESTRATED]%' OR status = 'COMPLETED')
            AND updated_at < NOW() - INTERVAL '1 hour'
        RETURNING COUNT(*);
        " 2>/dev/null | tr -d ' \n\t' || echo "0")
        
        cleanup_results+=("zombie_tasks_cleaned:$ZOMBIE_COUNT")
        
        # Database vacuum (light)
        docker exec helix_postgres psql -U helix_user -d helix -c "VACUUM ANALYZE tasks;" >/dev/null 2>&1 || true
        cleanup_results+=("database:vacuumed")
    else
        cleanup_results+=("database:unavailable")
    fi
    
    printf '%s\n' "${cleanup_results[@]}"
}

# Function to restart system with dynamic ports
restart_system_safely() {
    echo "🔄 Restarting HELIX system safely..." >&2
    
    # Ensure we have the port discovery script
    if [ ! -f "./scripts/find-port.sh" ]; then
        echo "❌ ERROR: Port discovery script missing" >&2
        echo '{"status": "failed", "reason": "missing_port_script"}'
        exit 1
    fi
    
    chmod +x ./scripts/find-port.sh
    
    # Discover available port
    AVAILABLE_PORT=$(./scripts/find-port.sh 2>/dev/null)
    if [[ ! "$AVAILABLE_PORT" =~ ^[0-9]+$ ]]; then
        echo "❌ ERROR: Could not find available port" >&2
        echo '{"status": "failed", "reason": "no_available_port", "port_result": "'$AVAILABLE_PORT'"}'
        exit 1
    fi
    
    echo "🌐 Using port: $AVAILABLE_PORT" >&2
    
    # Update configuration
    if [ ! -f ".env" ]; then
        cp .env.example .env
    fi
    
    sed -i "s/^API_PORT=.*/API_PORT=${AVAILABLE_PORT}/" .env
    
    # Activate virtual environment and start system
    if [ -d "helix_env" ]; then
        echo "🐍 Activating virtual environment..." >&2
        source helix_env/bin/activate
    fi
    
    echo "🚀 Starting HELIX system..." >&2
    nohup python start_system.py > emergency_restart.log 2>&1 &
    NEW_PID=$!
    
    echo "⏱️  Waiting for system startup..." >&2
    sleep 8
    
    # Verify startup
    if curl -s -f "http://localhost:${AVAILABLE_PORT}/api/v1/health" >/dev/null 2>&1; then
        echo "✅ System started successfully" >&2
        echo "RESTART_STATUS=success"
        echo "NEW_PID=$NEW_PID"
        echo "API_PORT=$AVAILABLE_PORT"
    else
        echo "❌ System startup verification failed" >&2
        echo "RESTART_STATUS=failed"
        echo "NEW_PID=$NEW_PID"
        echo "API_PORT=$AVAILABLE_PORT"
    fi
}

# Main execution flow
main() {
    local start_time=$(date -Iseconds)
    
    # Always start with SSH safety check
    ssh_safety_check
    
    # Identify processes
    eval $(identify_helix_processes)
    
    local results=()
    
    case $ACTION in
        "restart")
            echo "🔄 Executing emergency restart..." >&2
            termination_results=$(safe_terminate_processes "$VERIFIED_PIDS")
            cleanup_results=$(cleanup_system_resources)
            eval $(restart_system_safely)
            
            results+=("termination:[$termination_results]")
            results+=("cleanup:[$cleanup_results]") 
            results+=("restart_status:$RESTART_STATUS")
            results+=("new_pid:$NEW_PID")
            results+=("api_port:$API_PORT")
            ;;
            
        "cleanup")
            echo "🧹 Executing system cleanup..." >&2
            cleanup_results=$(cleanup_system_resources)
            results+=("cleanup:[$cleanup_results]")
            ;;
            
        "reset")
            echo "🔄 Executing full system reset..." >&2
            termination_results=$(safe_terminate_processes "$VERIFIED_PIDS")
            cleanup_results=$(cleanup_system_resources)
            
            results+=("termination:[$termination_results]")
            results+=("cleanup:[$cleanup_results]")
            results+=("note:Manual restart required after reset")
            ;;
            
        *)
            echo "❌ ERROR: Unknown action: $ACTION" >&2
            echo '{"status": "failed", "reason": "unknown_action", "action": "'$ACTION'"}'
            exit 1
            ;;
    esac
    
    # Final SSH safety verification
    ssh_safety_check
    
    # Output results as JSON
    cat << EOF
{
    "timestamp": "$start_time",
    "action": "$ACTION",
    "force_mode": $FORCE_MODE,
    "ssh_safety": "verified",
    "results": [$(printf '"%s",' "${results[@]}" | sed 's/,$//')],
    "status": "completed"
}
EOF
}

# Execute main function
main

echo "✅ Emergency recovery completed at $(date)" >&2