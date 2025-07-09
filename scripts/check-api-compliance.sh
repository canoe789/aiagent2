#!/bin/bash
#
# HELIX API Interface Compliance Check Script
# Purpose: Comprehensive API specification and security compliance detection
# Usage: ./scripts/check-api-compliance.sh [--format json|human] [--severity critical|high|all]
# Based on zen-mcp multi-model analysis and HELIX project specifics
#

set -e

# Default values
FORMAT="human"
SEVERITY_FILTER="all"
API_PORT=""
API_HOST="localhost"
PROJECT_ROOT=$(pwd)
TIMEOUT=30

# Color codes for human readable output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --severity)
            SEVERITY_FILTER="$2"
            shift 2
            ;;
        --port)
            API_PORT="$2"
            shift 2
            ;;
        --host)
            API_HOST="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: $0 [--format json|human] [--severity critical|high|all] [--port PORT] [--host HOST]" >&2
            exit 1
            ;;
    esac
done

# Get API port from .env if not specified
if [ -z "$API_PORT" ]; then
    API_PORT=$(grep "^API_PORT=" .env 2>/dev/null | cut -d'=' -f2 || echo "8000")
fi

if [ "$FORMAT" != "human" ]; then
    # Suppress stderr for JSON output
    exec 2>/dev/null
fi

echo "🔍 HELIX API Interface Compliance Check" >&2
echo "===============================================" >&2
echo "API Endpoint: http://${API_HOST}:${API_PORT}" >&2
echo "Severity Filter: ${SEVERITY_FILTER}" >&2
echo "===============================================" >&2

# Function to check JSON Schema syntax
check_json_schemas() {
    echo "📋 Checking JSON Schema syntax..." >&2
    
    local schema_issues=()
    local schemas_found=0
    
    # Check all .json files in schemas/ directory
    if [ -d "schemas" ]; then
        for schema_file in schemas/*.json; do
            if [ -f "$schema_file" ]; then
                schemas_found=$((schemas_found + 1))
                
                # Check JSON syntax
                if ! python3 -c "import json; json.load(open('$schema_file'))" 2>/dev/null; then
                    schema_issues+=("CRITICAL:JSON syntax error in $schema_file")
                fi
                
                # Check for common issues like missing commas
                if grep -n '}[[:space:]]*"' "$schema_file" >/dev/null; then
                    schema_issues+=("HIGH:Potential missing comma in $schema_file")
                fi
                
                # Check for schema compliance
                if ! python3 -c "
import json
from jsonschema import Draft7Validator
try:
    with open('$schema_file') as f:
        schema = json.load(f)
    Draft7Validator.check_schema(schema)
except Exception as e:
    print(f'Schema validation error: {e}')
    exit(1)
" 2>/dev/null; then
                    schema_issues+=("HIGH:Schema validation error in $schema_file")
                fi
            fi
        done
    fi
    
    echo "SCHEMA_RESULTS='{\"schemas_found\": $schemas_found, \"issues\": [$(printf '\"%s\",' "${schema_issues[@]}" | sed 's/,$//')], \"status\": \"$([ ${#schema_issues[@]} -eq 0 ] && echo "clean" || echo "issues_found")\"}'"
}

# Function to check security configuration
check_security_config() {
    echo "🔒 Checking security configuration..." >&2
    
    local security_issues=()
    
    # Check CORS configuration in main.py
    if [ -f "src/api/main.py" ]; then
        if grep -q 'allow_origins=\["*"\]' src/api/main.py; then
            security_issues+=("CRITICAL:CORS allows all origins (*) - production security risk")
        fi
        
        if grep -q 'allow_credentials=True' src/api/main.py && grep -q 'allow_origins=\["*"\]' src/api/main.py; then
            security_issues+=("CRITICAL:CORS allows credentials with wildcard origins - severe security vulnerability")
        fi
    fi
    
    # Check for debug mode
    if grep -rq "debug=True" src/api/ --include="*.py"; then
        security_issues+=("HIGH:Debug mode enabled - may leak sensitive information")
    fi
    
    # Check for hardcoded secrets or keys
    if grep -rq -E "(password|secret|key|token).*=.*['\"][^'\"]*['\"]" src/ --include="*.py" | grep -v -E "(key.*input|password.*field|secret.*config)"; then
        security_issues+=("CRITICAL:Potential hardcoded secrets found in source code")
    fi
    
    # Check for missing authentication middleware
    auth_middleware_found=false
    if grep -rq -E "(Depends\(.*auth|Security\(|@authenticated)" src/api/ --include="*.py"; then
        auth_middleware_found=true
    fi
    
    if [ "$auth_middleware_found" = false ]; then
        security_issues+=("HIGH:No authentication middleware detected in API routes")
    fi
    
    # Check for rate limiting
    if ! grep -rq -E "(limiter|rate.*limit|slowapi)" src/ --include="*.py"; then
        security_issues+=("HIGH:No rate limiting mechanism detected")
    fi
    
    echo "SECURITY_RESULTS='{\"issues\": [$(printf '\"%s\",' "${security_issues[@]}" | sed 's/,$//')], \"status\": \"$([ ${#security_issues[@]} -eq 0 ] && echo "secure" || echo "vulnerabilities_found")\"}'"
}

# Function to check API endpoint compliance
check_api_endpoints() {
    echo "🌐 Checking API endpoint compliance..." >&2
    
    local endpoint_issues=()
    local api_available=false
    
    # Check if API is accessible
    if curl -s -f --max-time $TIMEOUT "http://${API_HOST}:${API_PORT}/api/v1/health" >/dev/null 2>&1; then
        api_available=true
        echo "✅ API is accessible" >&2
    else
        endpoint_issues+=("CRITICAL:API not accessible at http://${API_HOST}:${API_PORT}")
        echo "ENDPOINT_RESULTS='{\"api_available\": false, \"issues\": [$(printf '\"%s\",' "${endpoint_issues[@]}" | sed 's/,$//')], \"status\": \"unavailable\"}'"
        return
    fi
    
    # Test health endpoints
    health_response=$(curl -s --max-time $TIMEOUT "http://${API_HOST}:${API_PORT}/api/v1/health" 2>/dev/null)
    if ! echo "$health_response" | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
        endpoint_issues+=("HIGH:Health endpoint returns invalid JSON")
    fi
    
    # Check for proper error handling
    error_response=$(curl -s -w "%{http_code}" --max-time $TIMEOUT "http://${API_HOST}:${API_PORT}/api/v1/nonexistent" 2>/dev/null)
    http_code="${error_response: -3}"
    if [ "$http_code" != "404" ]; then
        endpoint_issues+=("MEDIUM:Non-existent endpoint should return 404, got $http_code")
    fi
    
    # Check error response format
    error_body=$(curl -s --max-time $TIMEOUT "http://${API_HOST}:${API_PORT}/api/v1/nonexistent" 2>/dev/null)
    if echo "$error_body" | grep -qi "traceback\|exception\|error.*line"; then
        endpoint_issues+=("CRITICAL:Error responses leak internal stack traces")
    fi
    
    # Test OpenAPI documentation availability
    if ! curl -s -f --max-time $TIMEOUT "http://${API_HOST}:${API_PORT}/docs" >/dev/null 2>&1; then
        endpoint_issues+=("MEDIUM:OpenAPI documentation (/docs) not accessible")
    fi
    
    # Check API versioning consistency
    if ! curl -s --max-time $TIMEOUT "http://${API_HOST}:${API_PORT}/api" | grep -q "v2.0"; then
        endpoint_issues+=("LOW:API version in response may not match documented version")
    fi
    
    echo "ENDPOINT_RESULTS='{\"api_available\": $api_available, \"issues\": [$(printf '\"%s\",' "${endpoint_issues[@]}" | sed 's/,$//')], \"status\": \"$([ ${#endpoint_issues[@]} -eq 0 ] && echo "compliant" || echo "issues_found")\"}'"
}

# Function to check response format consistency
check_response_formats() {
    echo "📊 Checking response format consistency..." >&2
    
    local format_issues=()
    
    if curl -s -f --max-time $TIMEOUT "http://${API_HOST}:${API_PORT}/api/v1/health" >/dev/null 2>&1; then
        # Check health endpoint response structure
        health_response=$(curl -s --max-time $TIMEOUT "http://${API_HOST}:${API_PORT}/api/v1/health" 2>/dev/null)
        
        # Verify required fields in health response
        required_fields=("status" "timestamp" "components")
        for field in "${required_fields[@]}"; do
            if ! echo "$health_response" | python3 -c "import json, sys; data=json.load(sys.stdin); exit(0 if '$field' in data else 1)" 2>/dev/null; then
                format_issues+=("HIGH:Health response missing required field: $field")
            fi
        done
        
        # Check timestamp format (ISO 8601)
        if ! echo "$health_response" | python3 -c "
import json, sys
from datetime import datetime
try:
    data = json.load(sys.stdin)
    if 'timestamp' in data:
        datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
except:
    exit(1)
" 2>/dev/null; then
            format_issues+=("MEDIUM:Health response timestamp not in ISO 8601 format")
        fi
        
        # Check if detailed health endpoint returns additional statistics
        detailed_response=$(curl -s --max-time $TIMEOUT "http://${API_HOST}:${API_PORT}/api/v1/health/detailed" 2>/dev/null)
        if ! echo "$detailed_response" | python3 -c "import json, sys; data=json.load(sys.stdin); exit(0 if 'statistics' in data else 1)" 2>/dev/null; then
            format_issues+=("MEDIUM:Detailed health endpoint missing statistics field")
        fi
    fi
    
    echo "FORMAT_RESULTS='{\"issues\": [$(printf '\"%s\",' "${format_issues[@]}" | sed 's/,$//')], \"status\": \"$([ ${#format_issues[@]} -eq 0 ] && echo "consistent" || echo "inconsistencies_found")\"}'"
}

# Function to check performance and monitoring
check_performance_monitoring() {
    echo "⚡ Checking performance monitoring..." >&2
    
    local monitoring_issues=()
    
    # Check for metrics endpoint
    if ! curl -s -f --max-time $TIMEOUT "http://${API_HOST}:${API_PORT}/metrics" >/dev/null 2>&1; then
        monitoring_issues+=("MEDIUM:No Prometheus metrics endpoint (/metrics) found")
    fi
    
    # Check for structured logging
    if ! grep -rq -E "(structlog|json.*log)" src/ --include="*.py"; then
        monitoring_issues+=("LOW:No structured logging detected")
    fi
    
    # Check response time of health endpoint
    response_time=$(curl -w "%{time_total}" -s -o /dev/null --max-time $TIMEOUT "http://${API_HOST}:${API_PORT}/api/v1/health" 2>/dev/null)
    if [ -n "$response_time" ] && python3 -c "exit(0 if float('$response_time') < 1.0 else 1)" 2>/dev/null; then
        echo "✅ Health endpoint response time: ${response_time}s" >&2
    elif [ -n "$response_time" ]; then
        monitoring_issues+=("MEDIUM:Health endpoint slow response time: ${response_time}s")
    fi
    
    echo "MONITORING_RESULTS='{\"issues\": [$(printf '\"%s\",' "${monitoring_issues[@]}" | sed 's/,$//')], \"response_time\": \"${response_time:-unknown}\", \"status\": \"$([ ${#monitoring_issues[@]} -eq 0 ] && echo "monitored" || echo "monitoring_gaps")\"}'"
}

# Function to generate recommendations
generate_recommendations() {
    local all_issues=("$@")
    local recommendations=()
    
    # Analyze issues and generate recommendations
    for issue in "${all_issues[@]}"; do
        case "$issue" in
            *"CORS allows all origins"*)
                recommendations+=("HIGH:Configure specific allowed origins in CORS middleware for production")
                ;;
            *"JSON syntax error"*)
                recommendations+=("CRITICAL:Fix JSON syntax errors in schema files - validate with linter")
                ;;
            *"Debug mode enabled"*)
                recommendations+=("HIGH:Disable debug mode in production - set debug=False")
                ;;
            *"hardcoded secrets"*)
                recommendations+=("CRITICAL:Remove hardcoded secrets - use environment variables")
                ;;
            *"No authentication middleware"*)
                recommendations+=("HIGH:Implement API authentication - consider JWT or API keys")
                ;;
            *"No rate limiting"*)
                recommendations+=("HIGH:Add rate limiting middleware - use fastapi-limiter with Redis")
                ;;
            *"stack traces"*)
                recommendations+=("CRITICAL:Implement custom error handlers to prevent information leakage")
                ;;
            *"No Prometheus metrics"*)
                recommendations+=("MEDIUM:Add prometheus_client for metrics collection and monitoring")
                ;;
        esac
    done
    
    # Remove duplicates
    recommendations=($(printf '%s\n' "${recommendations[@]}" | sort -u))
    
    printf '[%s]' "$(printf '\"%s\",' "${recommendations[@]}" | sed 's/,$//')"
}

# Collect all analyses
echo "📋 Running schema validation..." >&2
eval $(check_json_schemas)

echo "🔒 Running security checks..." >&2
eval $(check_security_config)

echo "🌐 Running endpoint checks..." >&2
eval $(check_api_endpoints)

echo "📊 Running format checks..." >&2
eval $(check_response_formats)

echo "⚡ Running monitoring checks..." >&2
eval $(check_performance_monitoring)

# Collect all issues
all_issues=()
for result_var in SCHEMA_RESULTS SECURITY_RESULTS ENDPOINT_RESULTS FORMAT_RESULTS MONITORING_RESULTS; do
    if [ -n "${!result_var}" ]; then
        issues=$(echo "${!result_var}" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'issues' in data:
        for issue in data['issues']:
            print(issue)
except:
    pass
" 2>/dev/null)
        while IFS= read -r issue; do
            if [ -n "$issue" ]; then
                all_issues+=("$issue")
            fi
        done <<< "$issues"
    fi
done

# Filter by severity
filtered_issues=()
for issue in "${all_issues[@]}"; do
    case "$SEVERITY_FILTER" in
        "critical")
            if [[ "$issue" == CRITICAL:* ]]; then
                filtered_issues+=("$issue")
            fi
            ;;
        "high")
            if [[ "$issue" == CRITICAL:* ]] || [[ "$issue" == HIGH:* ]]; then
                filtered_issues+=("$issue")
            fi
            ;;
        "all")
            filtered_issues+=("$issue")
            ;;
    esac
done

# Generate recommendations
RECOMMENDATIONS=$(generate_recommendations "${filtered_issues[@]}")

# Determine overall status
overall_status="compliant"
critical_count=0
high_count=0

for issue in "${filtered_issues[@]}"; do
    if [[ "$issue" == CRITICAL:* ]]; then
        critical_count=$((critical_count + 1))
        overall_status="critical"
    elif [[ "$issue" == HIGH:* ]]; then
        high_count=$((high_count + 1))
        if [ "$overall_status" = "compliant" ]; then
            overall_status="high_risk"
        fi
    elif [ "$overall_status" = "compliant" ]; then
        overall_status="minor_issues"
    fi
done

# Output results
if [ "$FORMAT" = "json" ]; then
    # JSON output for programmatic use
    cat << EOF
{
    "timestamp": "$(date -Iseconds)",
    "overall_status": "$overall_status",
    "severity_filter": "$SEVERITY_FILTER",
    "api_endpoint": "http://${API_HOST}:${API_PORT}",
    "summary": {
        "total_issues": ${#filtered_issues[@]},
        "critical_issues": $critical_count,
        "high_issues": $high_count
    },
    "results": {
        "schema_validation": $SCHEMA_RESULTS,
        "security_compliance": $SECURITY_RESULTS,
        "endpoint_compliance": $ENDPOINT_RESULTS,
        "response_formats": $FORMAT_RESULTS,
        "performance_monitoring": $MONITORING_RESULTS
    },
    "recommendations": $RECOMMENDATIONS
}
EOF
else
    # Human-readable output
    echo >&2
    echo "📋 HELIX API COMPLIANCE REPORT" >&2
    echo "===============================================" >&2
    echo "🕒 Timestamp: $(date)" >&2
    echo "🎯 Overall Status: $overall_status" >&2
    echo "🔍 Issues Found: ${#filtered_issues[@]} (Critical: $critical_count, High: $high_count)" >&2
    echo >&2
    
    if [ ${#filtered_issues[@]} -gt 0 ]; then
        echo "⚠️  Issues:" >&2
        for issue in "${filtered_issues[@]}"; do
            severity=$(echo "$issue" | cut -d':' -f1)
            message=$(echo "$issue" | cut -d':' -f2-)
            case "$severity" in
                "CRITICAL")
                    echo -e "   ${RED}🚨 CRITICAL:${NC} $message" >&2
                    ;;
                "HIGH")
                    echo -e "   ${YELLOW}⚠️  HIGH:${NC} $message" >&2
                    ;;
                "MEDIUM")
                    echo -e "   ${BLUE}📋 MEDIUM:${NC} $message" >&2
                    ;;
                "LOW")
                    echo -e "   ${GREEN}💡 LOW:${NC} $message" >&2
                    ;;
            esac
        done
        echo >&2
        
        # Show recommendations
        if [ "$RECOMMENDATIONS" != "[]" ]; then
            echo "💡 Recommendations:" >&2
            echo "$RECOMMENDATIONS" | python3 -c "
import json, sys
try:
    recs = json.load(sys.stdin)
    for rec in recs:
        severity = rec.split(':')[0]
        message = rec.split(':', 1)[1]
        if severity == 'CRITICAL':
            print(f'   🚨 {message}')
        elif severity == 'HIGH':
            print(f'   ⚠️  {message}')
        else:
            print(f'   💡 {message}')
except:
    pass
" >&2
        fi
    else
        echo -e "${GREEN}✅ No issues found - API is compliant${NC}" >&2
    fi
    echo "===============================================" >&2
fi

echo "✅ API compliance check completed" >&2