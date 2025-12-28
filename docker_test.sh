#!/bin/bash
# Docker Test Script for Modbus TCP Server
# Run this to test the Modbus implementation in Docker

echo "======================================================================"
echo "  Docker Test for Modbus TCP Server"
echo "======================================================================"
echo

# Check if running with docker permissions
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker permission denied."
    echo
    echo "To fix this, either:"
    echo "  1. Add yourself to docker group: sudo usermod -aG docker \$USER"
    echo "  2. Run with sudo: sudo ./docker_test.sh"
    echo
    exit 1
fi

echo "[1/4] Stopping existing containers..."
docker compose down 2>/dev/null || docker-compose down 2>/dev/null
echo

echo "[2/4] Rebuilding plc1 with new Modbus code..."
docker compose build plc1 2>/dev/null || docker-compose build plc1
if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi
echo "✅ Build successful"
echo

echo "[3/4] Starting plc1 container..."
docker compose up -d plc1 2>/dev/null || docker-compose up -d plc1
if [ $? -ne 0 ]; then
    echo "❌ Failed to start container"
    exit 1
fi
echo "✅ Container started"
echo

echo "Waiting for services to initialize..."
sleep 3
echo

echo "[4/4] Testing Modbus connectivity..."
echo

# Check if port 5502 is accessible
if nc -zv localhost 5502 2>&1 | grep -q succeeded; then
    echo "✅ Port 5502 is accessible"
else
    echo "❌ Port 5502 is not accessible"
    echo "Checking container logs:"
    docker logs vuln-plc1 2>&1 | tail -20
    exit 1
fi
echo

# Test with Python if available
if command -v python3 >/dev/null 2>&1; then
    echo "Running quick test..."
    python3 quick_test.py 5502
    if [ $? -eq 0 ]; then
        echo
        echo "======================================================================"
        echo "  ✅ ALL DOCKER TESTS PASSED!"
        echo "======================================================================"
        echo
        echo "Your Modbus TCP server is working in Docker!"
        echo
        echo "Access points:"
        echo "  • Web Interface: http://localhost:5000"
        echo "  • Modbus TCP:    localhost:5502"
        echo
        echo "Test with pymodbus:"
        echo '  python3 -c "from pymodbus.client.sync import ModbusTcpClient; \'
        echo '    client = ModbusTcpClient(\"localhost\", 5502); client.connect(); \'
        echo '    print(client.read_holding_registers(0, 10, unit=1).registers)"'
        echo
    else
        echo "❌ Modbus test failed"
        exit 1
    fi
else
    echo "Python3 not found, skipping detailed test"
    echo "But port 5502 is accessible, so the server is likely working!"
fi

echo
echo "To view logs: docker logs -f vuln-plc1"
echo "To stop:      docker compose down"
