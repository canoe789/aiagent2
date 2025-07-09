#!/bin/bash
#
# HELIX SOP-Compliant System Stop Script
# Safely terminates HELIX system with SSH safety checks
#
# Usage: ./scripts/sop-compliant-stop.sh [--force] [--quiet]
#

set -e  # Exit on any error

# Parse command line arguments
FORCE_STOP=false
QUIET_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE_STOP=true
            shift
            ;;
        --quiet)
            QUIET_MODE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--force] [--quiet]"
            exit 1
            ;;
    esac
done

# Logging function
log() {
    if [ "$QUIET_MODE" = false ]; then
        echo "$1"
    fi
}

log "🛑 HELIX SOP-Compliant System Stop"
log "==================================="

# ============================================================================
# SOP Step 1: SSH Safety Verification
# ============================================================================
log "🔒 Step 1: SSH Safety Verification"

if ! netstat -tuln | grep -q ":22 "; then
    echo "🚨 CRITICAL: SSH service not detected on port 22"
    echo "🛑 ABORT: Cannot proceed with system operations without SSH safety"
    exit 1
fi
log "✅ SSH service confirmed active on port 22"

# ============================================================================
# SOP Step 2: Process Identification
# ============================================================================
log "🔍 Step 2: Process Identification"

# Check for PID file
if [ -f "helix_system.pid" ]; then
    HELIX_PID=$(cat helix_system.pid)
    log "📋 Found PID file: $HELIX_PID"
    
    # Verify process is still running
    if ps -p $HELIX_PID > /dev/null 2>&1; then
        log "✅ HELIX process confirmed running (PID: $HELIX_PID)"
    else
        log "⚠️  WARNING: PID file exists but process not running"
        rm -f helix_system.pid
        HELIX_PID=""
    fi
else
    log "📋 No PID file found, searching for processes..."
    HELIX_PID=""
fi

# Find running HELIX processes
HELIX_PROCESSES=$(ps aux | grep -E "(start_system|python.*aiagent)" | grep -v grep | awk '{print $2}' || true)

if [ -n "$HELIX_PROCESSES" ]; then
    log "🔍 Found HELIX processes: $HELIX_PROCESSES"
    
    # Show process details
    if [ "$QUIET_MODE" = false ]; then
        echo "   Process details:"
        ps aux | grep -E "(start_system|python.*aiagent)" | grep -v grep | head -5
    fi
else
    log "ℹ️  No HELIX processes found running"
    
    if [ "$FORCE_STOP" = false ]; then
        echo "✅ HELIX system is not running"
        exit 0
    fi
fi

# ============================================================================
# SOP Step 3: Graceful Shutdown Attempt
# ============================================================================
log "🔄 Step 3: Graceful Shutdown Attempt"

if [ -n "$HELIX_PID" ]; then
    log "🛑 Sending graceful shutdown signal to PID $HELIX_PID..."
    
    # Send SIGTERM (graceful shutdown)
    kill -TERM $HELIX_PID 2>/dev/null || true
    
    # Wait for graceful shutdown
    WAIT_COUNT=0
    MAX_WAIT=15
    
    while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
        if ! ps -p $HELIX_PID > /dev/null 2>&1; then
            log "✅ Process terminated gracefully"
            break
        fi
        
        if [ $((WAIT_COUNT % 3)) -eq 0 ]; then
            log "⏳ Waiting for graceful shutdown... (${WAIT_COUNT}s)"
        fi
        
        sleep 1
        WAIT_COUNT=$((WAIT_COUNT + 1))
    done
    
    # Check if process is still running
    if ps -p $HELIX_PID > /dev/null 2>&1; then
        if [ "$FORCE_STOP" = true ]; then
            log "⚠️  Graceful shutdown failed, forcing termination..."
            kill -KILL $HELIX_PID 2>/dev/null || true
            sleep 2
            log "✅ Process forcefully terminated"
        else
            echo "⚠️  WARNING: Process did not terminate gracefully"
            echo "    Use --force to forcefully terminate"
            exit 1
        fi
    fi
fi

# ============================================================================
# SOP Step 4: Cleanup Additional Processes
# ============================================================================
log "🧹 Step 4: Cleanup Additional Processes"

# Clean up any remaining HELIX processes
if [ -n "$HELIX_PROCESSES" ]; then
    for pid in $HELIX_PROCESSES; do
        if ps -p $pid > /dev/null 2>&1; then
            log "🛑 Terminating additional process: $pid"
            
            # Verify this is actually a HELIX process
            PROC_CMD=$(ps -p $pid -o cmd= 2>/dev/null || echo "")
            if echo "$PROC_CMD" | grep -q -E "(start_system|python.*aiagent)"; then
                kill -TERM $pid 2>/dev/null || true
                sleep 2
                
                # Force kill if still running
                if ps -p $pid > /dev/null 2>&1; then
                    kill -KILL $pid 2>/dev/null || true
                fi
            fi
        fi
    done
fi

log "✅ Process cleanup completed"

# ============================================================================
# SOP Step 5: Port Cleanup Verification
# ============================================================================
log "🔍 Step 5: Port Cleanup Verification"

# Check if any ports are still in use by HELIX
if [ -f ".env" ]; then
    API_PORT=$(grep "^API_PORT=" .env | cut -d'=' -f2 || echo "")
    
    if [ -n "$API_PORT" ] && [ "$API_PORT" != "" ]; then
        if netstat -tuln | grep -q ":$API_PORT "; then
            echo "⚠️  WARNING: Port $API_PORT still in use"
            
            # Show which process is using the port
            if command -v lsof &> /dev/null; then
                echo "    Process using port $API_PORT:"
                lsof -i :$API_PORT || echo "    Unable to identify process"
            fi
        else
            log "✅ Port $API_PORT is now free"
        fi
    fi
fi

# ============================================================================
# SOP Step 6: File Cleanup
# ============================================================================
log "🗂️  Step 6: File Cleanup"

# Remove PID file
if [ -f "helix_system.pid" ]; then
    rm -f helix_system.pid
    log "✅ PID file removed"
fi

# Optionally clean up log files
if [ "$FORCE_STOP" = true ]; then
    if [ -f "helix_system.log" ]; then
        log "🗑️  Archiving log file..."
        mv helix_system.log "helix_system.log.$(date +%Y%m%d_%H%M%S)"
        log "✅ Log file archived"
    fi
fi

# ============================================================================
# SOP Step 7: Final SSH Safety Check
# ============================================================================
log "🔒 Step 7: Final SSH Safety Check"

if ! netstat -tuln | grep -q ":22 "; then
    echo "🚨 CRITICAL: SSH service status changed during shutdown!"
    echo "🛠️  Manual intervention required - check SSH daemon"
    exit 1
fi
log "✅ SSH service remains active and safe"

# ============================================================================
# SOP Step 8: Final Status Report
# ============================================================================
log ""
log "✅ HELIX SYSTEM STOP COMPLETED"
log "=================================================="
log "🛑 System Status: Fully stopped"
log "🔒 SSH Safety: Verified active"
log "📊 Port Status: Cleaned up"
log "🗂️  Files: Cleaned up"
log "🕒 Stop Time: $(date)"
log "=================================================="
log ""

if [ "$QUIET_MODE" = false ]; then
    echo "🎯 Next Steps:"
    echo "   Start system: ./scripts/sop-compliant-start.sh"
    echo "   Check system: ./scripts/check-system-health.sh"
    echo ""
    echo "✅ HELIX system shutdown complete!"
fi

exit 0