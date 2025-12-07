#!/bin/bash
# Vulnerable PLC - Master Stop Script
# Stops all running PLCs, Historian, and Network Simulator

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Vulnerable PLC - Stopping All Services...                ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to stop a service
stop_service() {
    local name=$1
    local pidfile="logs/${name}.pid"

    if [ -f "$pidfile" ]; then
        pid=$(cat "$pidfile")

        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping $name (PID: $pid)...${NC}"
            kill $pid 2>/dev/null
            sleep 1

            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${YELLOW}Force stopping $name...${NC}"
                kill -9 $pid 2>/dev/null
            fi

            echo -e "${GREEN}✓ $name stopped${NC}"
        else
            echo -e "${YELLOW}✓ $name not running${NC}"
        fi

        rm "$pidfile"
    else
        echo -e "${YELLOW}✓ $name (no PID file found)${NC}"
    fi
}

# Check if logs directory exists
if [ ! -d "logs" ]; then
    echo -e "${YELLOW}No services appear to be running (logs directory not found)${NC}"
    exit 0
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Stopping PLC Systems${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

stop_service "PLC1-Modbus"
stop_service "PLC1-Web"
stop_service "PLC2-Modbus"
stop_service "PLC2-Web"
stop_service "PLC3-Modbus"
stop_service "PLC3-Web"
stop_service "PLC4-Modbus"
stop_service "PLC4-Web"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Stopping Infrastructure Services${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

stop_service "Historian"
stop_service "NetworkSim"

# Also kill any remaining Python processes that might be from our services
echo ""
echo -e "${YELLOW}Checking for any remaining service processes...${NC}"
pkill -f "modbus_server.*.py" 2>/dev/null
pkill -f "app.py" 2>/dev/null
pkill -f "plc.*_.*\.py" 2>/dev/null
pkill -f "historian.py" 2>/dev/null
pkill -f "network_simulator.py" 2>/dev/null

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  All Services Stopped${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
