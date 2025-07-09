#!/bin/bash
# HELIX SSH-Safe Process Manager
# Prevents accidental SSH service termination
# 
# Usage: 
#   source ./scripts/ssh-safe-manager.sh
#   SSH_SAFETY_CHECK
#   SAFE_KILL_HELIX <PID>

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# SSH Safety Check Function
SSH_SAFETY_CHECK() {
    echo -e "${BLUE}🔒 Performing SSH safety verification...${NC}"
    
    # Check if SSH is running on port 22
    if ! netstat -tuln 2>/dev/null | grep -q ":22 " && ! ss -tuln 2>/dev/null | grep -q ":22 "; then
        echo -e "${RED}🚨 CRITICAL: SSH service not detected on port 22${NC}"
        echo -e "${RED}🛑 SYSTEM SAFETY VIOLATED - Operation aborted${NC}"
        echo -e "${YELLOW}Manual intervention required:${NC}"
        echo -e "   → Check SSH daemon: ${BLUE}systemctl status sshd${NC}"
        echo -e "   → Manual restart: ${BLUE}sudo systemctl restart sshd${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ SSH service verified active on port 22${NC}"
    return 0
}

# Safe HELIX Process Termination Function
SAFE_KILL_HELIX() {
    local TARGET_PID=$1
    
    echo -e "${BLUE}🛡️  Initiating SSH-Safe HELIX process termination...${NC}"
    
    # Step 1: SSH Safety Check
    SSH_SAFETY_CHECK || {
        echo -e "${RED}🛑 ABORT: Cannot proceed without SSH safety confirmation${NC}"
        exit 1
    }
    
    # Step 2: Validate PID argument
    if [ -z "$TARGET_PID" ]; then
        echo -e "${RED}❌ Error: Missing PID argument${NC}"
        echo -e "${YELLOW}Usage: SAFE_KILL_HELIX <PID>${NC}"
        return 1
    fi
    
    # Step 3: Verify PID is numeric
    if ! [[ "$TARGET_PID" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}❌ Error: PID must be numeric, got: $TARGET_PID${NC}"
        return 1
    fi
    
    # Step 4: Check if process exists
    if ! ps -p "$TARGET_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Warning: Process $TARGET_PID not found (may have already terminated)${NC}"
        return 0
    fi
    
    # Step 5: Verify this is actually a HELIX process
    local PROC_CMD=$(ps -p "$TARGET_PID" -o cmd= 2>/dev/null || echo "")
    if [ -z "$PROC_CMD" ]; then
        echo -e "${RED}❌ Error: Cannot retrieve process command for PID $TARGET_PID${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🔍 Process command: ${NC}$PROC_CMD"
    
    # Check if it's a HELIX start_system.py process
    if echo "$PROC_CMD" | grep -q "start_system.py" && echo "$PROC_CMD" | grep -q "aiagent"; then
        echo -e "${GREEN}✅ Verified HELIX process PID $TARGET_PID${NC}"
    else
        echo -e "${RED}❌ ERROR: PID $TARGET_PID is NOT a HELIX process${NC}"
        echo -e "${YELLOW}   Process command: $PROC_CMD${NC}"
        echo -e "${YELLOW}   Expected: process containing 'start_system.py' and 'aiagent'${NC}"
        return 1
    fi
    
    # Step 6: Graceful termination
    echo -e "${BLUE}🛑 Safely terminating HELIX process $TARGET_PID...${NC}"
    kill -TERM "$TARGET_PID"
    
    # Step 7: Wait for graceful shutdown
    local WAIT_COUNT=0
    local MAX_WAIT=10
    
    while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
        if ! ps -p "$TARGET_PID" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Process $TARGET_PID terminated gracefully${NC}"
            break
        fi
        sleep 1
        WAIT_COUNT=$((WAIT_COUNT + 1))
        echo -e "${YELLOW}⏳ Waiting for graceful shutdown... ($WAIT_COUNT/$MAX_WAIT)${NC}"
    done
    
    # Step 8: Force kill if necessary
    if ps -p "$TARGET_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Process did not terminate gracefully, using SIGKILL...${NC}"
        kill -KILL "$TARGET_PID"
        sleep 1
        
        if ps -p "$TARGET_PID" > /dev/null 2>&1; then
            echo -e "${RED}❌ ERROR: Failed to terminate process $TARGET_PID${NC}"
            return 1
        else
            echo -e "${GREEN}✅ Process $TARGET_PID force-terminated${NC}"
        fi
    fi
    
    # Step 9: Final SSH safety verification
    SSH_SAFETY_CHECK || {
        echo -e "${RED}🚨 WARNING: SSH safety status changed after process termination!${NC}"
        echo -e "${RED}This may indicate system instability or unintended side effects${NC}"
        return 1
    }
    
    echo -e "${GREEN}✅ SSH-Safe process termination completed successfully${NC}"
    return 0
}

# Find and safely terminate all HELIX processes
SAFE_CLEANUP_ALL_HELIX() {
    echo -e "${BLUE}🧹 Initiating SSH-Safe cleanup of all HELIX processes...${NC}"
    
    # SSH Safety Check
    SSH_SAFETY_CHECK || {
        echo -e "${RED}🛑 ABORT: Cannot proceed without SSH safety confirmation${NC}"
        exit 1
    }
    
    # Find all HELIX processes
    echo -e "${BLUE}🔍 Searching for HELIX processes...${NC}"
    local HELIX_PIDS=$(ps aux | grep -E "/home/canoezhang/Projects/aiagent.*python.*start_system.py" | grep -v grep | awk '{print $2}' || echo "")
    
    if [ -z "$HELIX_PIDS" ]; then
        echo -e "${GREEN}ℹ️  No HELIX processes found running${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}📋 Found HELIX processes: $HELIX_PIDS${NC}"
    
    # Terminate each process safely
    for PID in $HELIX_PIDS; do
        echo -e "${BLUE}🎯 Processing PID: $PID${NC}"
        SAFE_KILL_HELIX "$PID" || {
            echo -e "${RED}❌ Failed to safely terminate PID $PID${NC}"
            return 1
        }
        echo ""  # Add spacing between processes
    done
    
    echo -e "${GREEN}✅ All HELIX processes safely terminated${NC}"
    return 0
}

# Display usage information
show_usage() {
    echo -e "${BLUE}SSH-Safe Process Manager for HELIX${NC}"
    echo ""
    echo -e "${YELLOW}Available functions:${NC}"
    echo -e "  ${GREEN}SSH_SAFETY_CHECK${NC}           - Verify SSH service is running"
    echo -e "  ${GREEN}SAFE_KILL_HELIX <PID>${NC}      - Safely terminate a specific HELIX process"
    echo -e "  ${GREEN}SAFE_CLEANUP_ALL_HELIX${NC}     - Safely terminate all HELIX processes"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ${BLUE}source ./scripts/ssh-safe-manager.sh${NC}"
    echo -e "  ${BLUE}SSH_SAFETY_CHECK${NC}"
    echo -e "  ${BLUE}SAFE_KILL_HELIX 12345${NC}"
    echo -e "  ${BLUE}SAFE_CLEANUP_ALL_HELIX${NC}"
    echo ""
    echo -e "${YELLOW}Safety Features:${NC}"
    echo -e "  • Verifies SSH service is running before any operation"
    echo -e "  • Validates target processes are actually HELIX applications"
    echo -e "  • Uses graceful termination (SIGTERM) before force kill"
    echo -e "  • Re-verifies SSH service after operations"
    echo -e "  • Provides detailed logging and error reporting"
}

# Export functions for use in other scripts
export -f SSH_SAFETY_CHECK SAFE_KILL_HELIX SAFE_CLEANUP_ALL_HELIX show_usage

# If script is run directly (not sourced), show usage
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    show_usage
fi

echo -e "${GREEN}✅ SSH-Safe Manager loaded successfully${NC}"
echo -e "${BLUE}ℹ️  Type 'show_usage' for available functions${NC}"