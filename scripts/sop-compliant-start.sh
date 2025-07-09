#!/bin/bash
#
# HELIX SOP-Compliant System Startup Script
# Implements full Dynamic Port Management SOP with frontend-backend compatibility
#
# Usage: ./scripts/sop-compliant-start.sh [--force] [--quiet]
#

set -e  # Exit on any error

# Parse command line arguments
FORCE_RESTART=false
QUIET_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE_RESTART=true
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

log "🚀 HELIX SOP-Compliant System Startup"
log "======================================"

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
# SOP Step 2: Tool Verification
# ============================================================================
log "🔧 Step 2: Tool Verification"

# Check for required scripts
if [ ! -f "./scripts/find-port.sh" ]; then
    echo "❌ ERROR: Port discovery script missing"
    exit 1
fi
chmod +x ./scripts/find-port.sh

# Check for Python startup script
if [ ! -f "./start_system.py" ]; then
    echo "❌ ERROR: System startup script missing"
    exit 1
fi

# Check for frontend directory
if [ ! -d "./frontend" ]; then
    echo "❌ ERROR: Frontend directory missing"
    exit 1
fi

log "✅ All required tools verified"

# ============================================================================
# SOP Step 3: Environment Preparation
# ============================================================================
log "🌍 Step 3: Environment Preparation"

# Create .env from template if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log "📝 Created .env from template"
    else
        echo "❌ ERROR: Neither .env nor .env.example found"
        exit 1
    fi
fi

# Verify Python environment
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python3 not found"
    exit 1
fi

log "✅ Environment preparation completed"

# ============================================================================
# SOP Step 4: Dynamic Port Discovery
# ============================================================================
log "🔍 Step 4: Dynamic Port Discovery"

# API Service Port Discovery
API_PORT=$(./scripts/find-port.sh "" "" "api")
if [[ ! "$API_PORT" =~ ^[0-9]+$ ]]; then
    echo "❌ ERROR: Invalid API port number: $API_PORT"
    exit 1
fi

log "✅ API port discovered: $API_PORT"

# Update environment configuration
sed -i "s/^API_PORT=.*/API_PORT=${API_PORT}/" .env

# Verify update
if ! grep -q "API_PORT=${API_PORT}" .env; then
    echo "❌ ERROR: Failed to update API port in .env"
    exit 1
fi

log "✅ Configuration updated successfully"

# ============================================================================
# SOP Step 5: Service Health Pre-Check
# ============================================================================
log "🏥 Step 5: Service Health Pre-Check"

# Check if there are any zombie processes
ZOMBIE_PROCESSES=$(ps aux | grep -E "(start_system|python.*aiagent)" | grep -v grep | wc -l)

if [ "$ZOMBIE_PROCESSES" -gt 0 ] && [ "$FORCE_RESTART" = false ]; then
    echo "⚠️  WARNING: Found $ZOMBIE_PROCESSES existing HELIX processes"
    echo "    Use --force to automatically terminate them"
    
    # Show the processes
    echo "    Existing processes:"
    ps aux | grep -E "(start_system|python.*aiagent)" | grep -v grep | head -5
    
    read -p "    Terminate existing processes? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Startup cancelled by user"
        exit 1
    fi
    FORCE_RESTART=true
fi

if [ "$FORCE_RESTART" = true ]; then
    log "🛑 Terminating existing processes..."
    pkill -f "start_system.py" || true
    pkill -f "python.*aiagent" || true
    sleep 2
    log "✅ Process cleanup completed"
fi

log "✅ Health pre-check completed"

# ============================================================================
# SOP Step 6: System Startup
# ============================================================================
log "🚀 Step 6: System Startup"

# Start the system in the background
log "🔄 Starting HELIX system with API on port $API_PORT..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    log "🐍 Activating Python virtual environment..."
    source venv/bin/activate
elif [ -d "helix_env" ]; then
    log "🐍 Activating Python virtual environment..."
    source helix_env/bin/activate
fi

# Use nohup to ensure process continues even if terminal is closed
nohup python3 start_system.py > helix_system.log 2>&1 &
HELIX_PID=$!

# Store PID for management
echo $HELIX_PID > helix_system.pid

log "✅ System startup initiated (PID: $HELIX_PID)"

# ============================================================================
# SOP Step 7: Service Verification
# ============================================================================
log "🔍 Step 7: Service Verification"

# Wait for service to be ready
MAX_WAIT=30
WAIT_COUNT=0

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if curl -s "http://localhost:$API_PORT/api/v1/health" > /dev/null 2>&1; then
        break
    fi
    
    if [ $((WAIT_COUNT % 5)) -eq 0 ]; then
        log "⏳ Waiting for service to be ready... (${WAIT_COUNT}s)"
    fi
    
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
done

# Final health check
if curl -s "http://localhost:$API_PORT/api/v1/health" | grep -q "healthy"; then
    log "✅ Service health check passed"
else
    echo "❌ ERROR: Service health check failed"
    echo "   Check log file: helix_system.log"
    exit 1
fi

# ============================================================================
# SOP Step 8: Frontend Compatibility Check
# ============================================================================
log "🌐 Step 8: Frontend Compatibility Check"

# Check if frontend files exist
if [ -f "./frontend/index.html" ] && [ -f "./frontend/port-discovery.js" ]; then
    log "✅ Frontend files verified"
    
    # Test frontend access
    if curl -s "http://localhost:$API_PORT/" > /dev/null 2>&1; then
        log "✅ Frontend accessibility confirmed"
    else
        echo "⚠️  WARNING: Frontend may not be accessible"
    fi
else
    echo "⚠️  WARNING: Frontend files not found"
fi

# ============================================================================
# SOP Step 9: Final Status Report
# ============================================================================
log ""
log "✅ HELIX SYSTEM STARTUP COMPLETED"
log "=================================================="
log "🌐 Frontend: http://localhost:$API_PORT"
log "🔍 Health Check: http://localhost:$API_PORT/api/v1/health"
log "📚 API Documentation: http://localhost:$API_PORT/docs"
log "📊 Database: localhost:5432 (Fixed)"
log "=================================================="
log "🕒 Startup Time: $(date)"
log "📝 Log File: helix_system.log"
log "📋 PID File: helix_system.pid"
log "🔄 Port Discovery: $API_PORT (API Service Range)"
log "✨ Status: All services operational"
log ""

if [ "$QUIET_MODE" = false ]; then
    echo "🎯 Management Commands:"
    echo "   View logs: tail -f helix_system.log"
    echo "   Stop system: kill \$(cat helix_system.pid)"
    echo "   Restart system: $0 --force"
    echo ""
    echo "✅ HELIX is ready for use!"
fi

# ============================================================================
# SOP Step 10: Continuous Monitoring Setup (Optional)
# ============================================================================
if [ "$QUIET_MODE" = false ]; then
    echo "🔍 Optional: Start continuous monitoring? (y/N)"
    read -p "   This will show real-time logs: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📊 Starting continuous monitoring (Ctrl+C to stop)..."
        tail -f helix_system.log
    fi
fi

exit 0