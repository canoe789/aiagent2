#!/bin/bash
#
# HELIX Port Discovery Script
# Purpose: Find an available TCP port in specified range
# Usage: ./scripts/find-port.sh [start_port] [end_port]
# Default: 8000-9000
#

START_PORT=${1:-8000}
END_PORT=${2:-9000}
MAX_ATTEMPTS=50
SERVICE_TYPE=${3:-"api"}  # api, orchestrator, worker

# Service-specific port ranges to reduce conflicts (only if no explicit range provided)
if [ -z "$1" ] && [ -z "$2" ]; then
    case $SERVICE_TYPE in
        "api")
            START_PORT=8000
            END_PORT=8099
            ;;
        "orchestrator")
            START_PORT=8100
            END_PORT=8199
            ;;
        "worker")
            START_PORT=8200
            END_PORT=8299
            ;;
    esac
fi

echo "Searching for available port in range $START_PORT-$END_PORT for service: $SERVICE_TYPE" >&2

for (( i=0; i<MAX_ATTEMPTS; i++ )); do
    # Generate random port in range
    PORT=$(( RANDOM % (END_PORT - START_PORT + 1) + START_PORT ))
    
    # Check if port is available using multiple methods
    if ! ss -tulpn | grep -q ":$PORT " && \
       ! netstat -tuln 2>/dev/null | grep -q ":$PORT " && \
       ! lsof -i :$PORT >/dev/null 2>&1; then
        echo $PORT
        exit 0
    fi
    
    # Small delay to avoid CPU spinning
    sleep 0.02
done

echo "Error: Could not find available port in range $START_PORT-$END_PORT after $MAX_ATTEMPTS attempts" >&2
exit 1