# Modbus Testing Guide - Real-Time HMI Sync

## Overview
The Modbus server and web interface now share state in real-time. When you write to Modbus registers, the changes appear live on the HMI!

## Quick Start

```bash
# Terminal 1: Start the simulator
vuln-plc

# Terminal 2: Open browser
firefox http://localhost:5000

# Login as operator/operator123 and go to HMI page
# Terminal 3: Control via Modbus and watch HMI update!
```

## Modbus Register Map

### Holding Registers (Read/Write - Function Code 3/6/16)

| Register | Description | Scaling | Example |
|----------|-------------|---------|---------|
| 0 | Tank 1 Level (%) | x10 | 800 = 80.0% |
| 1 | Tank 1 Temperature (°C) | x10 | 300 = 30.0°C |
| 2 | Tank 1 Pressure (kPa) | x10 | 1200 = 120.0 kPa |
| 3 | Tank 2 Level (%) | x10 | 500 = 50.0% |
| 4 | Tank 2 Temperature (°C) | x10 | 250 = 25.0°C |
| 5 | Tank 2 Pressure (kPa) | x10 | 1000 = 100.0 kPa |
| 6 | Pump 1 Speed (RPM) | 1 | 2000 = 2000 RPM |
| 7 | Pump 2 Speed (RPM) | 1 | 1500 = 1500 RPM |
| 8 | Pump 3 Speed (RPM) | 1 | 1000 = 1000 RPM |
| 14 | Flow Rate (L/min) | x10 | 200 = 20.0 L/min |
| 15 | Vibration (mm/s) | x10 | 50 = 5.0 mm/s |

### Coils (Read/Write Boolean - Function Code 1/5/15)

| Coil | Description | Values |
|------|-------------|--------|
| 0 | Pump 1 Status | 0=OFF, 1=ON |
| 1 | Pump 2 Status | 0=OFF, 1=ON |
| 2 | Pump 3 Status | 0=OFF, 1=ON |
| 3 | Valve 1 Status | 0=CLOSED, 1=OPEN |
| 4 | Valve 2 Status | 0=CLOSED, 1=OPEN |
| 5 | Valve 3 Status | 0=CLOSED, 1=OPEN |
| 6 | Valve 4 Status | 0=CLOSED, 1=OPEN |
| 10 | Emergency Stop | 0=NORMAL, 1=STOPPED |
| 11 | Safety Interlock | 0=OFF, 1=ON |

## Testing with modbus-cli

Install modbus-cli:
```bash
pip install modbus-cli
```

### Read Operations

```bash
# Read tank level (register 0)
modbus read localhost:5502 0 1

# Read first 10 registers
modbus read localhost:5502 0 10

# Read input registers (sensor readings)
modbus read localhost:5502 -t 4 0 10

# Read coils (pump/valve status)
modbus read localhost:5502 -t 0 0 12
```

### Write Operations (Watch HMI Update!)

```bash
# Set tank level to 90%
modbus write localhost:5502 0 900
# 🎯 Watch the tank fill up on the HMI!

# Set tank level to 20%
modbus write localhost:5502 0 200
# 🎯 Watch the tank drain on the HMI!

# Increase temperature to 40°C
modbus write localhost:5502 1 400
# 🎯 Watch temperature sensor update!

# Set pressure to 150 kPa
modbus write localhost:5502 2 1500
# 🎯 Watch pressure go into warning zone!

# Turn pump ON (coil write)
modbus write localhost:5502 -t 0 0 1
# 🎯 Watch pump icon animate on HMI!

# Turn pump OFF
modbus write localhost:5502 -t 0 0 0
# 🎯 Watch pump icon stop!

# Open valve 1
modbus write localhost:5502 -t 0 3 1
# 🎯 Watch valve change color!

# Trigger emergency stop
modbus write localhost:5502 -t 0 10 1
# 🎯 Watch alarm appear!
```

## Testing with Metasploit

```bash
msfconsole

# Scan Modbus server
use auxiliary/scanner/scada/modbusclient
set RHOSTS localhost
set RPORT 5502
run

# Read registers
use auxiliary/scanner/scada/modbusdetect
set RHOSTS localhost
set RPORT 5502
run

# Write to registers (turn on pump)
use auxiliary/scanner/scada/modbusdetect
set RHOSTS localhost
set RPORT 5502
set FUNCTION READ_COILS
set ADDRESS 0
set NUMBER 10
run
```

## Testing with Python (pymodbus)

```python
from pymodbus.client.sync import ModbusTcpClient

client = ModbusTcpClient('localhost', port=5502)

# Read tank level
result = client.read_holding_registers(0, 1)
print(f"Tank Level: {result.registers[0] / 10}%")

# Set tank level to 75%
client.write_register(0, 750)
print("Tank set to 75% - check HMI!")

# Turn on pump
client.write_coil(0, True)
print("Pump ON - check HMI!")

# Read multiple registers
result = client.read_holding_registers(0, 10)
print(f"Registers: {result.registers}")

client.close()
```

## Real-Time Sync Test Scenarios

### Scenario 1: Fill the Tank
```bash
# Open HMI in browser first
for i in {100..900..100}; do
  modbus write localhost:5502 0 $i
  sleep 2
done
# Watch tank fill up smoothly!
```

### Scenario 2: Overfill Attack (Trigger Alarm)
```bash
# Set tank to critical high level
modbus write localhost:5502 0 950
# 🚨 Watch alarm appear on HMI!
```

### Scenario 3: Pump Control
```bash
# Turn all pumps ON
modbus write localhost:5502 -t 0 0 1
modbus write localhost:5502 -t 0 1 1
modbus write localhost:5502 -t 0 2 1
# Watch all pumps activate!

# Turn all pumps OFF
modbus write localhost:5502 -t 0 0 0
modbus write localhost:5502 -t 0 1 0
modbus write localhost:5502 -t 0 2 0
```

### Scenario 4: Emergency Stop
```bash
# Trigger emergency stop
modbus write localhost:5502 -t 0 10 1
# 🚨 Watch emergency alarm!

# Reset emergency stop
modbus write localhost:5502 -t 0 10 0
```

### Scenario 5: Temperature Attack
```bash
# Overheat the tank
modbus write localhost:5502 1 850
# 🔥 Watch temperature sensor go red!
```

## Vulnerability Testing

### Test 1: Unauthorized Access
```bash
# No authentication required!
modbus write localhost:5502 0 999
# Even without web login, you can control the PLC!
```

### Test 2: Buffer Overflow Attempt
```bash
# Try to overflow register
modbus write localhost:5502 0 65535
modbus write localhost:5502 0 99999
```

### Test 3: Rapid Register Flooding
```bash
# Flood with rapid writes
for i in {1..100}; do
  modbus write localhost:5502 0 $((RANDOM % 1000))
done
```

### Test 4: Coil Manipulation
```bash
# Rapidly toggle safety systems
for i in {1..50}; do
  modbus write localhost:5502 -t 0 11 0
  modbus write localhost:5502 -t 0 11 1
done
```

## Nmap Scanning

```bash
# Discover Modbus service
nmap -p 5502 localhost

# Modbus-specific scan
nmap -sT -p 502,5502 --script modbus-discover localhost
```

## State File Location

The shared state is stored at: `/tmp/vulnplc_state.json`

You can view it in real-time:
```bash
# Watch state changes
watch -n 1 cat /tmp/vulnplc_state.json

# Or use jq for pretty output
watch -n 1 'cat /tmp/vulnplc_state.json | jq'
```

## HMI Update Rate

- HMI polls every 2 seconds
- Modbus-to-state sync is immediate
- State-to-HMI sync happens on next poll
- Maximum latency: ~2 seconds

## Troubleshooting

If HMI doesn't update:

1. Check state file exists:
   ```bash
   ls -la /tmp/vulnplc_state.json
   ```

2. Verify Modbus write succeeded:
   ```bash
   modbus read localhost:5502 0 1
   ```

3. Check browser console (F12) for errors

4. Verify you're logged in (not guest)

5. Refresh the HMI page

## Advanced: Metasploit Module Development

You can develop custom Metasploit modules to exploit this PLC:

```ruby
# Example: Tank overflow attack
use auxiliary/scanner/scada/modbusclient
set RHOSTS localhost
set RPORT 5502
set DATA 999
set ADDRESS 0
set FUNCTION WRITE_REGISTER
run
```

---

**Remember:** All changes via Modbus appear on the HMI in real-time!
This simulates a real ICS environment where SCADA operators would see unauthorized changes happening.
