#!/bin/bash
# Vulnerable PLC - Installation Script
# Creates symlink so 'vuln-plc' command is available system-wide

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VULN_PLC_SCRIPT="$SCRIPT_DIR/vuln-plc"
INSTALL_PATH="/usr/local/bin/vuln-plc"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Vulnerable PLC - Installation                            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if vuln-plc script exists
if [ ! -f "$VULN_PLC_SCRIPT" ]; then
    echo -e "${RED}Error: vuln-plc script not found at $VULN_PLC_SCRIPT${NC}"
    exit 1
fi

# Make sure script is executable
chmod +x "$VULN_PLC_SCRIPT"
chmod +x "$SCRIPT_DIR/start_all.sh"
chmod +x "$SCRIPT_DIR/stop_all.sh"
chmod +x "$SCRIPT_DIR/status.sh"

echo -e "${YELLOW}Creating system-wide command...${NC}"

# Check if /usr/local/bin exists
if [ ! -d "/usr/local/bin" ]; then
    echo -e "${RED}Error: /usr/local/bin directory not found${NC}"
    exit 1
fi

# Remove existing symlink if present
if [ -L "$INSTALL_PATH" ]; then
    echo -e "${YELLOW}Removing existing symlink...${NC}"
    sudo rm "$INSTALL_PATH"
fi

# Create symlink
if sudo ln -s "$VULN_PLC_SCRIPT" "$INSTALL_PATH"; then
    echo -e "${GREEN}✓ Symlink created: $INSTALL_PATH -> $VULN_PLC_SCRIPT${NC}"
else
    echo -e "${RED}Error: Failed to create symlink${NC}"
    echo -e "${YELLOW}You may need sudo privileges${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}You can now use the 'vuln-plc' command from anywhere:${NC}"
echo ""
echo -e "  ${YELLOW}vuln-plc start${NC}      Start all services"
echo -e "  ${YELLOW}vuln-plc stop${NC}       Stop all services"
echo -e "  ${YELLOW}vuln-plc status${NC}     Show service status"
echo -e "  ${YELLOW}vuln-plc restart${NC}    Restart all services"
echo -e "  ${YELLOW}vuln-plc logs${NC}       Follow all logs"
echo -e "  ${YELLOW}vuln-plc help${NC}       Show help"
echo ""
echo -e "${BLUE}Get started:${NC}"
echo -e "  ${YELLOW}vuln-plc start${NC}"
echo ""
