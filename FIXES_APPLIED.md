# Web UI Update Fix - Applied Changes

## Problem
Web UIs on ports 5011, 5012, 5013 were not showing visual updates from Modbus commands.

## Root Causes
1. **Hardcoded Docker path**: `shared_state.py` used `/app/shared/vulnplc_state.json` which doesn't exist when running on host
2. **No shared state file**: Without the correct path, no state file was being created
3. **Empty state filtering**: PLC web UIs filtered for `plc2_*`, `plc3_*`, `plc4_*` keys that didn't exist

## Changes Made

### 1. Fixed shared_state.py (line 7-18)
- Changed hardcoded `/app/shared` path to auto-detect environment
- Now works both in Docker and on host system
- Falls back to `./shared/` directory in project root

### 2. Fixed plc2_pressure.py (line 36-43)
- Removed filtering for `plc2_*` keys
- Now returns entire shared state
- Web UI will display all process data

### 3. Fixed plc3_temperature.py (line 35-41)
- Removed filtering for `plc3_*` keys
- Now returns entire shared state
- Web UI will display all process data

### 4. Fixed plc4_safety.py (line 37-43)
- Removed filtering for `plc4_*` keys
- Now returns entire shared state
- Web UI will display all process data

## How to Apply

Run these commands as root:

```bash
# Stop all PLC services
sudo pkill -f "python.*plc[234]"
sudo pkill -f "python.*app.py"

# Start PLCs again (from project root)
cd /home/taimaishu/Vuln-PLC

# Option 1: Use the startup script
sudo bash scripts/start_all.sh

# Option 2: Start individually
sudo python3 core/app.py &          # Port 5000
sudo python3 core/plc2_pressure.py &  # Port 5011
sudo python3 core/plc3_temperature.py & # Port 5012
sudo python3 core/plc4_safety.py &   # Port 5013
sudo python3 core/hmi_server.py &    # Port 8000
```

## Test the Fix

1. Send Modbus commands via modbus-cli:
   ```bash
   modbus write --port 5502 --address 0 --value 800
   ```

2. Check web UIs - they should now show live updates:
   - http://localhost:5000 - Main SCADA
   - http://localhost:5011 - PLC-2 Pressure System
   - http://localhost:5012 - PLC-3 Temperature System
   - http://localhost:5013 - PLC-4 Safety System
   - http://localhost:8000 - HMI Dashboard

## Optional: Start Physical Process Simulator

For more realistic behavior with physics-based simulations:

```bash
sudo python3 core/physical_process.py &
```

This will add realistic process dynamics like:
- Tank level changes based on pump/valve states
- Pressure buildup with compressor operation
- Temperature control with heating/cooling
- Safety alarms and interlocks
