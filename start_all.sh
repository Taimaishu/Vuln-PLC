#!/bin/bash
# Vulnerable PLC - Master Startup Script
# Starts all PLCs, Historian, and Network Simulator

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Vulnerable PLC - ICS/SCADA Security Training Lab        ║${NC}"
echo -e "${BLUE}║  Starting All Services...                                 ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Create logs directory
mkdir -p logs

# Function to start a service
start_service() {
    local name=$1
    local command=$2
    local logfile=$3

    echo -e "${YELLOW}Starting $name...${NC}"
    nohup python3 $command > logs/$logfile 2>&1 &
    local pid=$!
    echo $pid > logs/${name}.pid

    # Wait a moment and check if process is still running
    sleep 1
    if ps -p $pid > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $name started (PID: $pid)${NC}"
    else
        echo -e "${RED}✗ $name failed to start${NC}"
    fi
}

# Stop any existing processes
echo -e "${YELLOW}Checking for existing processes...${NC}"
if [ -d "logs" ]; then
    for pidfile in logs/*.pid; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${YELLOW}Stopping existing process $pid...${NC}"
                kill $pid 2>/dev/null
            fi
            rm "$pidfile"
        fi
    done
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Starting PLC Systems${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Start PLC-1 (Tank Control)
start_service "PLC1-Modbus" "modbus_server.py" "plc1_modbus.log"
start_service "PLC1-Web" "app.py" "plc1_web.log"

# Start PLC-2 (Pressure Control)
start_service "PLC2-Modbus" "modbus_server2.py" "plc2_modbus.log"
start_service "PLC2-Web" "plc2_pressure.py" "plc2_web.log"

# Start PLC-3 (Temperature Control)
start_service "PLC3-Modbus" "modbus_server3.py" "plc3_modbus.log"
start_service "PLC3-Web" "plc3_temperature.py" "plc3_web.log"

# Start PLC-4 (Safety/ESD)
start_service "PLC4-Modbus" "modbus_server4.py" "plc4_modbus.log"
start_service "PLC4-Web" "plc4_safety.py" "plc4_web.log"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Starting Infrastructure Services${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Start Historian
start_service "Historian" "historian.py" "historian.log"

# Start Network Simulator
start_service "NetworkSim" "network_simulator.py" "network.log"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  All Services Started Successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Web Interfaces:${NC}"
echo -e "  PLC-1 (Tank Control):      ${YELLOW}http://localhost:5000${NC}  (admin/admin)"
echo -e "  PLC-2 (Pressure System):   ${YELLOW}http://localhost:5011${NC}  (engineer/plc2pass)"
echo -e "  PLC-3 (Temperature):       ${YELLOW}http://localhost:5012${NC}  (engineer/temp123)"
echo -e "  PLC-4 (Safety/ESD):        ${YELLOW}http://localhost:5013${NC}  (safety_eng/safe123)"
echo -e "  Historian:                 ${YELLOW}http://localhost:8888${NC}  (historian/data123)"
echo ""
echo -e "${BLUE}Modbus TCP Endpoints:${NC}"
echo -e "  PLC-1: ${YELLOW}localhost:5502${NC}"
echo -e "  PLC-2: ${YELLOW}localhost:5503${NC}"
echo -e "  PLC-3: ${YELLOW}localhost:5504${NC}"
echo -e "  PLC-4: ${YELLOW}localhost:5505${NC}"
echo ""
echo -e "${BLUE}Logs:${NC} ${YELLOW}tail -f logs/*.log${NC}"
echo -e "${BLUE}Stop All:${NC} ${YELLOW}./stop_all.sh${NC}"
echo -e "${BLUE}Status:${NC} ${YELLOW}./status.sh${NC}"
echo ""
echo -e "${RED}⚠️  WARNING: This is an INTENTIONALLY VULNERABLE system${NC}"
echo -e "${RED}    Use ONLY in isolated lab environments!${NC}"
echo ""
