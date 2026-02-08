#!/bin/bash
# Restart all PLC services with the fixed shared_state configuration

echo "=========================================="
echo "Restarting Vuln-PLC Services"
echo "=========================================="
echo ""

# Stop all existing PLC processes
echo "Stopping all PLC services..."
sudo pkill -f "python.*plc[234]_"
sudo pkill -f "python.*app.py"
sudo pkill -f "python.*hmi_server"
sudo pkill -f "python.*physical_process"
sleep 2
echo "✓ All services stopped"
echo ""

# Navigate to project directory
cd /home/taimaishu/Vuln-PLC

# Create logs directory
mkdir -p logs

# Start PLC-1 (Main Web + Modbus - Port 5000, 5502)
echo "Starting PLC-1 (Tank Control)..."
sudo nohup python3 core/app.py > logs/plc1.log 2>&1 &
sleep 1

# Start PLC-2 (Pressure Control - Port 5011, 5503)
echo "Starting PLC-2 (Pressure Control)..."
sudo nohup python3 core/plc2_pressure.py > logs/plc2.log 2>&1 &
sleep 1

# Start PLC-3 (Temperature Control - Port 5012, 5504)
echo "Starting PLC-3 (Temperature Control)..."
sudo nohup python3 core/plc3_temperature.py > logs/plc3.log 2>&1 &
sleep 1

# Start PLC-4 (Safety/ESD - Port 5013, 5505)
echo "Starting PLC-4 (Safety/ESD)..."
sudo nohup python3 core/plc4_safety.py > logs/plc4.log 2>&1 &
sleep 1

# Start HMI Server (Port 8000)
echo "Starting HMI Server..."
sudo nohup python3 core/hmi_server.py > logs/hmi.log 2>&1 &
sleep 1

# Optional: Start Physical Process Simulator
echo "Starting Physical Process Simulator (optional)..."
sudo nohup python3 core/physical_process.py > logs/physical.log 2>&1 &
sleep 2

echo ""
echo "=========================================="
echo "✓ All Services Started!"
echo "=========================================="
echo ""
echo "Web Interfaces:"
echo "  PLC-1 (Tank):        http://localhost:5000  (admin/admin)"
echo "  PLC-2 (Pressure):    http://localhost:5011  (engineer/plc2pass)"
echo "  PLC-3 (Temperature): http://localhost:5012  (engineer/temp123)"
echo "  PLC-4 (Safety):      http://localhost:5013  (safety_eng/safe123)"
echo "  HMI Dashboard:       http://localhost:8000"
echo ""
echo "Modbus TCP Ports:"
echo "  PLC-1: localhost:5502"
echo "  PLC-2: localhost:5503"
echo "  PLC-3: localhost:5504"
echo "  PLC-4: localhost:5505"
echo ""
echo "Check logs: tail -f logs/*.log"
echo "Check status: ps aux | grep python | grep -E 'plc|hmi'"
echo ""
echo "Test with: modbus-cli localhost 5502 read holding 0 5"
echo ""
