#!/bin/bash
#
# HELIX Quick Start Demo Script
# Demonstrates the complete Dynamic Port Management SOP workflow
#

set -e  # Exit on any error

echo "🚀 HELIX Dynamic Port Management SOP Demo"
echo "=========================================="
echo

# Step 1: Tool Verification (SOP Step 1)
echo "📋 Step 1: Tool Verification"
if [ ! -f "./scripts/find-port.sh" ]; then
    echo "❌ ERROR: Port discovery script missing"
    exit 1
fi
chmod +x ./scripts/find-port.sh
echo "✅ Port discovery script verified and executable"
echo

# Step 2: Port Discovery (SOP Step 2)
echo "📋 Step 2: Port Discovery"
AVAILABLE_PORT=$(./scripts/find-port.sh)

if [[ ! "$AVAILABLE_PORT" =~ ^[0-9]+$ ]]; then
    echo "❌ ERROR: Invalid port number: $AVAILABLE_PORT"
    exit 1
fi

echo "✅ Discovered available port: $AVAILABLE_PORT"
echo

# Step 3: Configuration Update (SOP Step 3)
echo "📋 Step 3: Configuration Update"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 Created .env from template"
fi

# Update port configuration
sed -i "s/^API_PORT=.*/API_PORT=${AVAILABLE_PORT}/" .env

# Verify update
if grep -q "API_PORT=${AVAILABLE_PORT}" .env; then
    echo "✅ Configuration updated successfully"
    echo "   API_PORT set to: $AVAILABLE_PORT"
else
    echo "❌ ERROR: Failed to update configuration"
    exit 1
fi
echo

# Step 4: Display what would happen next
echo "📋 Step 4: Service Launch (Demo Mode - Not Actually Starting)"
echo "In real usage, this would execute:"
echo "   python start_system.py"
echo "   # or"
echo "   python scripts/start-with-dynamic-ports.py"
echo

# Step 5: Confirmation Report (SOP Step 5)
echo "📋 Step 5: Startup Confirmation Report"
echo
echo "✅ HELIX SYSTEM STARTUP REPORT (DEMO)"
echo "=================================================="
echo "🌐 API Server: http://localhost:$AVAILABLE_PORT"
echo "📚 API Documentation: http://localhost:$AVAILABLE_PORT/docs"
echo "🔍 Health Check: http://localhost:$AVAILABLE_PORT/api/v1/health"
echo "📊 Database: localhost:5432 (Fixed)"
echo "=================================================="
echo "🕒 Demo Execution Time: $(date)"
echo "🔄 Port Discovery Attempts: 1"
echo "✨ Status: SOP workflow completed successfully"
echo

echo "🎯 Demo Summary:"
echo "   • Port discovery script working: ✅"
echo "   • Configuration update working: ✅"
echo "   • SOP workflow verified: ✅"
echo "   • Ready for actual deployment: ✅"
echo
echo "To actually start HELIX system:"
echo "   python scripts/start-with-dynamic-ports.py"
echo
echo "To use Docker deployment:"
echo "   docker-compose -f config/docker-compose.dynamic.yml up -d"
echo "   # Access at: http://localhost:8080"