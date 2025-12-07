#!/bin/bash
# Vulnerable PLC - Status Check Script
# Shows which services are currently running

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Vulnerable PLC - Service Status                          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check service status
check_service() {
    local name=$1
    local pidfile="logs/${name}.pid"
    local port=$2

    if [ -f "$pidfile" ]; then
        pid=$(cat "$pidfile")

        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} $name (PID: $pid) - ${GREEN}RUNNING${NC}"

            # Check port if provided
            if [ ! -z "$port" ]; then
                if netstat -tuln 2>/dev/null | grep -q ":$port " || ss -tuln 2>/dev/null | grep -q ":$port "; then
                    echo -e "  └─ Port $port: ${GREEN}LISTENING${NC}"
                else
                    echo -e "  └─ Port $port: ${RED}NOT LISTENING${NC}"
                fi
            fi
        else
            echo -e "${RED}✗${NC} $name (PID: $pid) - ${RED}DEAD (stale PID file)${NC}"
        fi
    else
        echo -e "${RED}✗${NC} $name - ${RED}NOT RUNNING${NC}"
    fi
}

# Check if logs directory exists
if [ ! -d "logs" ]; then
    echo -e "${YELLOW}No services appear to have been started yet${NC}"
    echo -e "${YELLOW}Run: ${BLUE}./start_all.sh${NC}"
    echo ""
    exit 0
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  PLC Systems${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

check_service "PLC1-Modbus" 5502
check_service "PLC1-Web" 5000
echo ""
check_service "PLC2-Modbus" 5503
check_service "PLC2-Web" 5011
echo ""
check_service "PLC3-Modbus" 5504
check_service "PLC3-Web" 5012
echo ""
check_service "PLC4-Modbus" 5505
check_service "PLC4-Web" 5013

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Infrastructure Services${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

check_service "Historian" 8888
check_service "NetworkSim"

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Quick Links${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Count running services
running_count=0
total_count=10

for pidfile in logs/*.pid; do
    if [ -f "$pidfile" ]; then
        pid=$(cat "$pidfile")
        if ps -p $pid > /dev/null 2>&1; then
            ((running_count++))
        fi
    fi
done

echo -e "Services Running: ${GREEN}$running_count${NC} / $total_count"
echo ""

if [ $running_count -gt 0 ]; then
    echo -e "${BLUE}Web Interfaces:${NC}"
    echo -e "  PLC-1: ${YELLOW}http://localhost:5000${NC}"
    echo -e "  PLC-2: ${YELLOW}http://localhost:5011${NC}"
    echo -e "  PLC-3: ${YELLOW}http://localhost:5012${NC}"
    echo -e "  PLC-4: ${YELLOW}http://localhost:5013${NC}"
    echo -e "  Historian: ${YELLOW}http://localhost:8888${NC}"
    echo ""
    echo -e "${BLUE}Logs:${NC}"
    echo -e "  ${YELLOW}tail -f logs/*.log${NC}"
    echo ""
else
    echo -e "${YELLOW}No services running. Start with: ${BLUE}./start_all.sh${NC}"
    echo ""
fi
