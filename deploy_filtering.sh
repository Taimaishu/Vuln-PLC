#!/bin/bash
# Deploy Alert Filtering Feature to PLC-1 Container
# This script rebuilds the PLC-1 container with the new filtering UI

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Deploying Alert Filtering Feature to PLC-1                  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

cd /home/taimaishu/Vuln-PLC

echo "Step 1: Stopping PLC-1..."
sudo docker-compose stop plc1

echo ""
echo "Step 2: Removing old container..."
sudo docker-compose rm -f plc1

echo ""
echo "Step 3: Rebuilding PLC-1 image..."
sudo docker-compose build plc1

echo ""
echo "Step 4: Starting PLC-1 with filtering feature..."
sudo docker-compose up -d plc1

echo ""
echo "Step 5: Waiting 30 seconds for startup..."
sleep 30

echo ""
echo "Step 6: Verifying deployment..."
if curl -s http://localhost:5000/ > /dev/null 2>&1; then
    echo "  ✓ PLC-1 web server is responding"

    # Check for filtering UI
    if curl -s http://localhost:5000/process 2>/dev/null | grep -q "filter-plc1"; then
        echo "  ✓ Filtering UI deployed successfully!"
        echo ""
        echo "╔═══════════════════════════════════════════════════════════════╗"
        echo "║  ✅ DEPLOYMENT SUCCESSFUL!                                    ║"
        echo "╚═══════════════════════════════════════════════════════════════╝"
        echo ""
        echo "🌐 Access the filtering interface:"
        echo "   URL: http://localhost:5000/process"
        echo "   Login: admin / admin"
        echo ""
        echo "🔍 Features available:"
        echo "   • Filter by PLC (PLC-1, PLC-2, PLC-3, PLC-4)"
        echo "   • Filter by Severity (CRITICAL, WARNING, HIGH)"
        echo "   • Real-time alert count updates"
        echo "   • Export filtered alerts to CSV"
        echo "   • Clear filters button"
    else
        echo "  ⚠️  Filtering UI not detected yet"
        echo "     (May need more startup time, try checking the web interface)"
    fi
else
    echo "  ✗ PLC-1 web server not responding"
    echo "     Check logs: docker logs vuln-plc1"
fi

echo ""
