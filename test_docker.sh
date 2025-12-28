#!/bin/bash
# Test Modbus TCP Server in Docker
set -e

echo "======================================================================"
echo "  Testing Improved Modbus TCP Server in Docker"
echo "======================================================================"
echo

# Check Docker access
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker permission denied. Run with:"
    echo "   sudo ./test_docker.sh"
    exit 1
fi

echo "[1/6] Stopping any running containers..."
docker compose down 2>/dev/null || docker-compose down 2>/dev/null || true
echo "✅ Stopped"
echo

echo "[2/6] Rebuilding plc1 with improved Modbus code..."
docker compose build plc1 2>/dev/null || docker-compose build plc1
if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi
echo "✅ Build complete"
echo

echo "[3/6] Starting plc1 container..."
docker compose up -d plc1 2>/dev/null || docker-compose up -d plc1
if [ $? -ne 0 ]; then
    echo "❌ Failed to start"
    exit 1
fi
echo "✅ Container started"
echo

echo "[4/6] Waiting for services to initialize..."
sleep 3
echo

echo "[5/6] Checking logs for Modbus startup..."
docker logs vuln-plc1 2>&1 | grep -E "\[MODBUS\]|\[STARTUP\]" | tail -10
echo

echo "[6/6] Testing Modbus connectivity on port 5502..."
if nc -zv localhost 5502 2>&1 | grep -q succeeded; then
    echo "✅ Port 5502 is accessible"
else
    echo "❌ Port 5502 not accessible"
    echo "Container logs:"
    docker logs vuln-plc1 2>&1 | tail -20
    exit 1
fi
echo

# Test with Python if available
if command -v python3 >/dev/null 2>&1; then
    echo "Running Modbus test..."
    python3 quick_test.py 5502
    if [ $? -eq 0 ]; then
        echo
        echo "======================================================================"
        echo "  ✅ ALL DOCKER TESTS PASSED!"
        echo "======================================================================"
        echo
        echo "Your improved Modbus TCP server is working in Docker!"
        echo
        echo "Access points:"
        echo "  • Web Interface: http://localhost:5000"
        echo "  • Modbus TCP:    localhost:5502"
        echo
        echo "Improvements applied:"
        echo "  ✓ recv_exact() for message safety"
        echo "  ✓ Connection semaphore (max 50)"
        echo "  ✓ Socket timeout for clean shutdown"
        echo "  ✓ Protocol ID logging"
        echo "  ✓ Documented unimplemented coils"
        echo
    else
        echo "❌ Modbus test failed"
        exit 1
    fi
else
    echo "Python3 not found, but port is accessible!"
    echo "The server is likely working correctly."
fi

echo
echo "To view logs: docker logs -f vuln-plc1"
echo "To stop:      docker compose down"
