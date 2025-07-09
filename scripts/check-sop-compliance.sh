#!/bin/bash
#
# HELIX SOP Compliance Check Script
# Verifies system compliance with Dynamic Port Management SOP
#
# Usage: ./scripts/check-sop-compliance.sh [--verbose]
#

set -e

# Parse command line arguments
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--verbose]"
            exit 1
            ;;
    esac
done

# Logging function
log() {
    echo "$1"
}

verbose_log() {
    if [ "$VERBOSE" = true ]; then
        echo "   $1"
    fi
}

log "🔍 HELIX SOP Compliance Check"
log "============================="

COMPLIANCE_SCORE=0
TOTAL_CHECKS=0

# Function to record check result
check_result() {
    local name="$1"
    local status="$2"
    local message="$3"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [ "$status" = "PASS" ]; then
        COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + 1))
        log "✅ $name: PASS"
    else
        log "❌ $name: FAIL"
    fi
    
    if [ -n "$message" ]; then
        verbose_log "$message"
    fi
}

# ============================================================================
# Check 1: Port Discovery Script
# ============================================================================
log "🔧 Checking SOP Tools..."

if [ -f "./scripts/find-port.sh" ] && [ -x "./scripts/find-port.sh" ]; then
    # Test port discovery script
    if PORT_OUTPUT=$(./scripts/find-port.sh 2>/dev/null); then
        if [[ "$PORT_OUTPUT" =~ ^[0-9]+$ ]]; then
            check_result "Port Discovery Script" "PASS" "Found available port: $PORT_OUTPUT"
        else
            check_result "Port Discovery Script" "FAIL" "Invalid port output: $PORT_OUTPUT"
        fi
    else
        check_result "Port Discovery Script" "FAIL" "Script execution failed"
    fi
else
    check_result "Port Discovery Script" "FAIL" "Script missing or not executable"
fi

# ============================================================================
# Check 2: Environment Configuration
# ============================================================================
log "🌍 Checking Environment Configuration..."

if [ -f ".env" ]; then
    # Check for required environment variables
    if grep -q "^API_PORT=" .env; then
        check_result "Environment File" "PASS" "Contains API_PORT configuration"
    else
        check_result "Environment File" "FAIL" "Missing API_PORT configuration"
    fi
else
    if [ -f ".env.example" ]; then
        check_result "Environment File" "FAIL" "Missing .env file (template exists)"
    else
        check_result "Environment File" "FAIL" "Missing .env and .env.example files"
    fi
fi

# ============================================================================
# Check 3: Frontend Port Discovery
# ============================================================================
log "🌐 Checking Frontend Port Discovery..."

if [ -f "./frontend/port-discovery.js" ]; then
    # Check for SOP compliance markers in frontend code
    if grep -q "SOP compliant" "./frontend/port-discovery.js"; then
        check_result "Frontend Port Discovery" "PASS" "Contains SOP compliance markers"
    else
        check_result "Frontend Port Discovery" "FAIL" "Missing SOP compliance markers"
    fi
else
    check_result "Frontend Port Discovery" "FAIL" "Missing port-discovery.js file"
fi

# ============================================================================
# Check 4: Backend Port Configuration
# ============================================================================
log "⚙️  Checking Backend Port Configuration..."

if [ -f "./start_system.py" ]; then
    # Check for environment variable usage
    if grep -q "os.getenv.*API_PORT" "./start_system.py"; then
        check_result "Backend Port Configuration" "PASS" "Uses environment variable for port"
    else
        check_result "Backend Port Configuration" "FAIL" "Missing environment variable usage"
    fi
else
    check_result "Backend Port Configuration" "FAIL" "Missing start_system.py file"
fi

# ============================================================================
# Check 5: API Health Check Endpoint
# ============================================================================
log "🏥 Checking API Health Check..."

if [ -f "./src/api/health.py" ]; then
    # Check for health endpoint
    if grep -q "/health" "./src/api/health.py"; then
        check_result "API Health Check" "PASS" "Health endpoint implemented"
    else
        check_result "API Health Check" "FAIL" "Missing health endpoint"
    fi
else
    check_result "API Health Check" "FAIL" "Missing health.py file"
fi

# ============================================================================
# Check 6: SOP Startup Scripts
# ============================================================================
log "🚀 Checking SOP Startup Scripts..."

if [ -f "./scripts/sop-compliant-start.sh" ] && [ -x "./scripts/sop-compliant-start.sh" ]; then
    check_result "SOP Startup Script" "PASS" "SOP-compliant startup script exists"
else
    check_result "SOP Startup Script" "FAIL" "Missing or non-executable SOP startup script"
fi

if [ -f "./scripts/sop-compliant-stop.sh" ] && [ -x "./scripts/sop-compliant-stop.sh" ]; then
    check_result "SOP Stop Script" "PASS" "SOP-compliant stop script exists"
else
    check_result "SOP Stop Script" "FAIL" "Missing or non-executable SOP stop script"
fi

# ============================================================================
# Check 7: Database Port Configuration
# ============================================================================
log "📊 Checking Database Configuration..."

if [ -f ".env" ]; then
    # Check that database port is fixed (not dynamic)
    if grep -q "^POSTGRES_PORT=5432" .env; then
        check_result "Database Port Fixed" "PASS" "Database port correctly fixed to 5432"
    else
        check_result "Database Port Fixed" "FAIL" "Database port not fixed to 5432"
    fi
else
    check_result "Database Port Fixed" "FAIL" "Cannot verify database configuration"
fi

# ============================================================================
# Check 8: SSH Safety Implementation
# ============================================================================
log "🔒 Checking SSH Safety Implementation..."

if [ -f "./scripts/sop-compliant-start.sh" ]; then
    # Check for SSH safety checks
    if grep -q "netstat.*:22" "./scripts/sop-compliant-start.sh"; then
        check_result "SSH Safety Checks" "PASS" "SSH safety verification implemented"
    else
        check_result "SSH Safety Checks" "FAIL" "Missing SSH safety verification"
    fi
else
    check_result "SSH Safety Checks" "FAIL" "Cannot verify SSH safety implementation"
fi

# ============================================================================
# Check 9: Port Range Compliance
# ============================================================================
log "🎯 Checking Port Range Compliance..."

if [ -f "./scripts/find-port.sh" ]; then
    # Check for service-specific port ranges
    if grep -q "api" "./scripts/find-port.sh" && grep -q "8000" "./scripts/find-port.sh" && grep -q "8099" "./scripts/find-port.sh"; then
        check_result "Port Range Compliance" "PASS" "Service-specific port ranges implemented"
    else
        check_result "Port Range Compliance" "FAIL" "Missing service-specific port ranges"
    fi
else
    check_result "Port Range Compliance" "FAIL" "Cannot verify port range compliance"
fi

# ============================================================================
# Check 10: Frontend-Backend API Compatibility
# ============================================================================
log "🔄 Checking Frontend-Backend API Compatibility..."

if [ -f "./frontend/index.html" ] && [ -f "./src/api/jobs.py" ]; then
    # Check for matching API endpoints
    if grep -q "/api/v1/jobs" "./frontend/index.html" && grep -q "/jobs" "./src/api/jobs.py"; then
        check_result "API Compatibility" "PASS" "Frontend-backend API endpoints match"
    else
        check_result "API Compatibility" "FAIL" "Frontend-backend API endpoints mismatch"
    fi
else
    check_result "API Compatibility" "FAIL" "Cannot verify API compatibility"
fi

# ============================================================================
# Final Score Calculation
# ============================================================================
log ""
log "📊 SOP Compliance Report"
log "========================"

COMPLIANCE_PERCENTAGE=$((COMPLIANCE_SCORE * 100 / TOTAL_CHECKS))

log "✅ Passed Checks: $COMPLIANCE_SCORE/$TOTAL_CHECKS"
log "📈 Compliance Score: $COMPLIANCE_PERCENTAGE%"

if [ $COMPLIANCE_PERCENTAGE -ge 90 ]; then
    log "🎉 Excellent! System is highly SOP compliant"
    STATUS="EXCELLENT"
elif [ $COMPLIANCE_PERCENTAGE -ge 80 ]; then
    log "✅ Good! System is mostly SOP compliant"
    STATUS="GOOD"
elif [ $COMPLIANCE_PERCENTAGE -ge 70 ]; then
    log "⚠️  Fair! System needs some SOP improvements"
    STATUS="FAIR"
else
    log "❌ Poor! System requires significant SOP improvements"
    STATUS="POOR"
fi

log ""
log "🎯 Recommendations:"

if [ $COMPLIANCE_SCORE -lt $TOTAL_CHECKS ]; then
    log "   • Fix failing checks above"
    log "   • Review HELIX Dynamic Port Management SOP"
    log "   • Test port discovery and startup scripts"
    log "   • Verify frontend-backend compatibility"
fi

log "   • Run system health check: ./scripts/check-system-health.sh"
log "   • Test full startup: ./scripts/sop-compliant-start.sh"
log ""

# Exit with appropriate code
if [ $COMPLIANCE_PERCENTAGE -ge 80 ]; then
    exit 0
else
    exit 1
fi