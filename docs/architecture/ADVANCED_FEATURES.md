# Advanced Features Guide

This document describes the advanced, realistic features added to Vuln-PLC to bridge the gap between educational tool and real-world ICS environments.

## Table of Contents

1. [PLC Simulation Engine](#plc-simulation-engine)
2. [Modbus Intrusion Detection System](#modbus-intrusion-detection-system)
3. [S7 Protocol Support](#s7-protocol-support)
4. [System Monitoring](#system-monitoring)
5. [Training Scenarios](#training-scenarios)

---

## PLC Simulation Engine

### Overview

The PLC Engine (`plc_engine.py`) implements a realistic PLC simulation with:

- **Scan Cycle Execution**: Mimics real PLC scan cycles (10-100ms typical)
- **Ladder Logic Interpreter**: Executes simple ladder logic programs
- **Memory Areas**: Input/Output image tables, markers, data blocks
- **PLC States**: RUN, STOP, PROGRAM, ERROR
- **Watchdog Timer**: Detects scan cycle overruns
- **Timers & Counters**: Standard PLC timing/counting instructions

### Key Features

#### 1. Scan Cycle

Real PLCs execute programs in a continuous cycle:

```
[Read Inputs] → [Execute Program] → [Write Outputs] → [Update Timers] → [Repeat]
```

The PLC engine maintains configurable scan times (default 50ms):

```python
from plc_engine import PLCEngine

engine = PLCEngine('plc1', scan_time_ms=50)
engine.start()
```

#### 2. Ladder Logic Programming

Create ladder logic programs using instructions:

```python
from plc_engine import Instruction, InstructionType, create_tank_control_program

# Example: Pump control based on tank level
program = [
    # Network 1: Start pump if level < 30%
    Instruction(InstructionType.CMP, ['tank1_level', '<', '30'], "Low level check"),
    Instruction(InstructionType.OUT, ['pump1_status'], "Start pump"),

    # Network 2: Stop pump if level > 80%
    Instruction(InstructionType.CMP, ['tank1_level', '>', '80'], "High level check"),
    Instruction(InstructionType.AND, ['pump1_status'], "Check pump running"),
    Instruction(InstructionType.OUT, ['pump1_status'], "Stop pump"),
]

engine.load_program(program)
```

#### 3. Supported Instructions

| Instruction | Description | Example |
|-------------|-------------|---------|
| `LD` | Load normally-open contact | `LD('I0.0')` |
| `LDN` | Load normally-closed contact | `LDN('I0.1')` |
| `AND` | AND logic | `AND('I0.2')` |
| `OR` | OR logic | `OR('I0.3')` |
| `OUT` | Output coil | `OUT('Q0.0')` |
| `TON` | Timer ON-delay | `TON('T1', '5.0')` |
| `CMP` | Compare values | `CMP('level', '>', '50')` |
| `MOV` | Move value | `MOV('value', 'register')` |

#### 4. Memory Areas

Simulates real PLC memory organization:

- **I (Inputs)**: `I0.0`, `I0.1`, ... - Read from sensors/field devices
- **Q (Outputs)**: `Q0.0`, `Q0.1`, ... - Write to actuators/field devices
- **M (Markers)**: `M0.0`, `M0.1`, ... - Internal memory bits
- **DB (Data Blocks)**: `DB1`, `DB2`, ... - Structured data storage

#### 5. Diagnostics

Real-time PLC diagnostics:

```python
diag = engine.get_diagnostics()
print(f"State: {diag['state']}")
print(f"Scan Time: {diag['last_scan_time_ms']:.2f}ms")
print(f"Max Scan Time: {diag['max_scan_time_ms']:.2f}ms")
print(f"Scan Count: {diag['scan_count']}")
```

### Attack Surface

The PLC engine introduces realistic attack vectors:

1. **Scan Cycle Manipulation**: Overloading the PLC to cause watchdog faults
2. **Logic Injection**: Modifying ladder logic programs (if upload/download implemented)
3. **Memory Tampering**: Direct memory writes via Modbus to bypass logic
4. **State Manipulation**: Forcing PLC into STOP or ERROR states

---

## Modbus Intrusion Detection System

### Overview

The Modbus IDS (`modbus_ids.py`) provides real-time monitoring and anomaly detection for Modbus TCP traffic.

### Detection Capabilities

#### 1. Signature-Based Detection

Detects known attack patterns:

- **Invalid Function Codes**: Non-standard Modbus functions
- **Malformed Packets**: Protocol violations
- **Known Attack Signatures**: Specific exploit patterns

#### 2. Anomaly-Based Detection

Statistical analysis of traffic:

- **Rate Limiting**: Flooding attacks (>50 req/sec)
- **Sequential Scanning**: Register enumeration patterns
- **Timing Anomalies**: Commands at unusual hours
- **Baseline Deviations**: Unusual function code distributions

#### 3. Policy-Based Detection

Rule-based access control:

- **Unauthorized Writes**: Write attempts from non-whitelisted IPs
- **Protected Addresses**: Access to critical registers
- **Critical Function Codes**: Monitoring FC06, FC15, FC16

### Configuration

```python
from modbus_ids import ModbusIDS, ModbusEvent

# Create IDS
ids = ModbusIDS()

# Configure authorized writers
ids.add_authorized_writer('192.168.100.20')  # HMI
ids.add_authorized_writer('192.168.100.30')  # Engineering WS

# Protect critical registers
ids.add_protected_address(10)  # Emergency stop
ids.add_protected_address(15)  # Safety valve

# Start monitoring
ids.start()
```

### Analyzing Events

```python
# Create event
event = ModbusEvent(
    timestamp=time.time(),
    source_ip='192.168.1.100',
    dest_ip='192.168.100.10',
    function_code=6,  # Write Single Register
    address=10,       # Protected address!
    value=0
)

# Analyze (returns alerts)
alerts = ids.analyze_event(event)

for alert in alerts:
    print(f"[{alert.severity}] {alert.alert_type}: {alert.description}")
```

### Alert Severities

| Severity | Description | Example |
|----------|-------------|---------|
| `LOW` | Informational, possible reconnaissance | Unusual access time |
| `MEDIUM` | Suspicious activity worth investigating | Sequential register scan |
| `HIGH` | Likely attack or policy violation | Rate limit exceeded |
| `CRITICAL` | Active attack on critical systems | Unauthorized write to protected address |

### IDS Statistics

```python
stats = ids.get_statistics()
# {
#     'total_events': 1523,
#     'total_alerts': 47,
#     'recent_alerts': 12,
#     'function_code_distribution': {3: 890, 4: 350, 6: 180, 16: 103},
#     'source_distribution': {'192.168.100.20': 1200, '192.168.1.100': 323}
# }
```

### Training Scenarios

Use the IDS to practice blue team skills:

1. **Baseline Learning**: Observe normal traffic patterns
2. **Alert Tuning**: Adjust thresholds to reduce false positives
3. **Incident Response**: Investigate and respond to alerts
4. **Threat Hunting**: Proactive search for IOCs

---

## S7 Protocol Support

### Overview

The S7 server (`s7_server.py`) implements basic Siemens S7comm protocol (ISO-on-TCP, port 102).

**Note**: This is a simplified implementation for educational purposes. Real S7 protocol is significantly more complex.

### Features

- **Connection Management**: COTP connection establishment
- **Read/Write Operations**: Data block access
- **PLC Control**: START/STOP commands (⚠️ no authentication!)
- **Memory Areas**: Data blocks, inputs, outputs, markers

### Starting S7 Server

```python
from s7_server import S7Server

server = S7Server(host='0.0.0.0', port=102, plc_id='plc1_s7')
server.start()
```

**Important**: Requires root/admin privileges to bind to port 102:

```bash
sudo python3 s7_server.py
```

### Testing with Snap7

Install Snap7 library:

```bash
pip install python-snap7
```

Test S7 connection:

```python
import snap7

# Connect to S7 server
plc = snap7.client.Client()
plc.connect('localhost', 0, 1, 102)

# Read from Data Block 1
data = plc.db_read(1, 0, 10)  # DB1, offset 0, 10 bytes
print(f"Read: {data.hex()}")

# Write to Data Block 1
plc.db_write(1, 0, bytearray([0x01, 0x02, 0x03]))

# Get PLC status
status = plc.get_cpu_state()
print(f"PLC State: {status}")

# VULNERABILITY: Stop PLC without auth!
plc.plc_stop()

plc.disconnect()
```

### Attack Scenarios

The S7 server demonstrates real vulnerabilities:

1. **No Authentication**: Any client can connect
2. **Unrestricted Access**: Read/write all memory areas
3. **PLC Control**: Can STOP PLC remotely
4. **No Encryption**: All traffic in plaintext

### Detection

The Modbus IDS can be extended to monitor S7 traffic:

```python
# Monitor S7 control commands
if function == 0x28:  # PLC_CONTROL
    log_alert('S7_PLC_CONTROL', source_ip, 'CRITICAL')
```

---

## System Monitoring

### Overview

The System Monitor (`system_monitor.py`) provides centralized monitoring of all ICS components.

### Console Mode

Real-time terminal dashboard:

```bash
python3 system_monitor.py
```

Output:
```
======================================================================
ICS SYSTEM MONITOR - 2024-12-07 14:30:15
Uptime: 00:15:23
======================================================================

🟢 SECURITY STATUS: NORMAL
  Total Alerts: 47 (Critical: 2)
  Last Alert: 2024-12-07 14:29:58

🏭 PLC ENGINES:
  ✓ PLC1   | State: RUN     | Scan:  52.34ms | Count:   18456
  ✓ PLC2   | State: RUN     | Scan:  48.21ms | Count:   19012
  ✓ PLC3   | State: RUN     | Scan:  51.67ms | Count:   18234
  ✗ PLC4   | State: ERROR   | Scan:   0.00ms | Count:       0

🛡️  MODBUS IDS:
  Status: ACTIVE
  Events: 1,523 | Alerts: 47 (Recent: 12)
  Severity: LOW=20 MED=15 HIGH=10 CRIT=2

📡 NETWORK TRAFFIC:
  Total Packets: 1,523 (Recent: 100)
  Protocols: modbus=1200, s7=323
  Top Sources:
    • 192.168.100.20: 650 packets
    • 192.168.100.30: 450 packets
```

### Web Dashboard Mode

Browser-based monitoring:

```bash
python3 system_monitor.py --web
```

Access at: **http://localhost:5999**

Features:
- Real-time updates (2-second refresh)
- Security status overview
- PLC health metrics
- Active issues/alerts
- Auto-refreshing statistics

### Integration

Monitor integrates with all components automatically via `shared_state`:

```python
# PLC engine updates
shared_state.update_state('plc1_scan_time_ms', 52.34)
shared_state.update_state('plc1_state', 'RUN')

# IDS updates
shared_state.update_state('modbus_ids_stats', stats)
shared_state.update_state('modbus_ids_alerts', alerts)

# Monitor reads and displays
monitor = SystemMonitor()
monitor.start()
```

---

## Training Scenarios

### Scenario 1: PLC Logic Analysis

**Objective**: Understand PLC program execution

1. Load custom ladder logic into PLC engine
2. Monitor scan cycles and diagnostics
3. Observe input/output relationships
4. Identify logic vulnerabilities

**Skills**: PLC programming, reverse engineering

### Scenario 2: IDS Tuning

**Objective**: Configure IDS for environment

1. Establish traffic baseline (normal operations)
2. Generate test attacks (unauthorized writes, flooding)
3. Observe alerts and false positives
4. Tune thresholds and whitelists
5. Document detection rules

**Skills**: Security monitoring, baseline analysis, alert tuning

### Scenario 3: Multi-Protocol Attack

**Objective**: Exploit multiple protocols

1. Scan for Modbus (port 502) and S7 (port 102)
2. Use Modbus to modify registers
3. Use S7 to upload malicious logic
4. Use S7 PLC_STOP to create denial-of-service
5. Observe IDS alerts and monitor dashboard

**Skills**: Protocol analysis, attack chaining, ICS exploitation

### Scenario 4: Incident Response

**Objective**: Respond to active attack

1. Monitor detects unauthorized write attempt
2. Investigate source IP and command details
3. Block malicious source in firewall
4. Analyze affected PLC states
5. Restore safe configuration
6. Document incident timeline

**Skills**: Incident response, forensics, remediation

### Scenario 5: Red vs Blue Team Exercise

**Objective**: Full adversary simulation

**Red Team**: Gain access and disrupt operations
- Enumerate PLCs and protocols
- Identify critical processes
- Execute attacks while evading detection
- Achieve objectives (data exfiltration, DoS, process manipulation)

**Blue Team**: Detect and respond
- Monitor IDS alerts
- Analyze traffic patterns
- Identify and block attacks
- Restore systems
- Improve defenses

**Skills**: Teamwork, realistic attack/defense, post-exercise review

---

## Performance Considerations

### Scan Cycle Timing

Typical PLC scan times:
- **Small programs**: 5-20ms
- **Medium programs**: 20-50ms
- **Large programs**: 50-100ms
- **Very large**: 100-500ms

Configure appropriately:

```python
# Fast cycle for responsive control
engine = PLCEngine('plc1', scan_time_ms=20)

# Slower cycle for complex logic
engine = PLCEngine('plc1', scan_time_ms=100)
```

### IDS Performance

IDS overhead is minimal:
- Event analysis: <1ms per event
- Baseline updates: Every 10 seconds
- Alert storage: Last 1000 alerts in memory

For high-traffic environments, consider:
- Sampling (analyze 1 in N events)
- Distributed IDS (multiple instances)
- Async processing

### Monitoring Overhead

System monitor:
- Dashboard updates: Every 5 seconds (console), 2 seconds (web)
- Metrics collection: Every 1 second
- Memory usage: ~50MB typical

---

## Security Best Practices

### Defense in Depth

Layer multiple security controls:

1. **Network Segmentation**: Isolate OT from IT
2. **Firewalls**: Restrict protocols and IPs
3. **IDS/IPS**: Monitor and block attacks
4. **Authentication**: Strong passwords, MFA
5. **Encryption**: TLS/VPN for all communications
6. **Monitoring**: Continuous visibility
7. **Incident Response**: Documented procedures

### Configuration Hardening

Harden Vuln-PLC for more realistic security:

```python
# Enable IDS with strict policies
ids = ModbusIDS()
ids.add_authorized_writer('192.168.100.20')  # Only HMI
ids.add_protected_address(10)  # Emergency systems
ids.start()

# Reduce scan cycle (faster anomaly detection)
engine = PLCEngine('plc1', scan_time_ms=20)
engine.start()

# Enable all monitoring
monitor = SystemMonitor()
monitor.start()
```

### Vulnerability Management

Track and remediate vulnerabilities:

1. Inventory all systems (PLCs, protocols, versions)
2. Scan for known CVEs
3. Apply vendor patches
4. Implement compensating controls for unpatchable systems
5. Regular security assessments

---

## Troubleshooting

### PLC Engine Issues

**Problem**: High scan times / watchdog faults

```python
# Check diagnostics
diag = engine.get_diagnostics()
print(f"Max scan: {diag['max_scan_time_ms']}ms")

# Optimize program
- Reduce instruction count
- Simplify logic
- Remove unnecessary timers
```

**Problem**: Program not executing

```python
# Check PLC state
if engine.state != PLCState.RUN:
    engine.set_state(PLCState.RUN)

# Reset watchdog
engine.reset_watchdog()
```

### IDS Issues

**Problem**: Too many false positives

```python
# Tune thresholds
ids.rate_limit_threshold = 100  # Increase from 50

# Add legitimate sources to whitelist
ids.add_authorized_writer('192.168.100.25')

# Exclude noisy alerts
ids.ignore_alert_types.add('UNUSUAL_TIME')
```

**Problem**: Missing alerts

```python
# Check IDS is running
print(f"IDS enabled: {ids.enabled}")

# Verify events are being analyzed
stats = ids.get_statistics()
print(f"Total events: {stats['total_events']}")

# Lower detection thresholds
ids.rate_limit_threshold = 25  # Decrease from 50
```

### S7 Server Issues

**Problem**: Can't bind to port 102

```bash
# Port 102 requires root privileges
sudo python3 s7_server.py

# Or use higher port
server = S7Server(host='0.0.0.0', port=10102)
```

**Problem**: Clients can't connect

```python
# Check firewall
sudo ufw allow 102/tcp

# Verify server is listening
netstat -an | grep 102
```

---

## References

- **IEC 61131-3**: Programmable controllers - Programming languages
- **IEC 61850**: Communication networks and systems for power utility automation
- **Modbus Protocol**: Modbus Application Protocol Specification V1.1b
- **S7comm Protocol**: Wireshark S7comm dissector documentation
- **NIST SP 800-82**: Guide to Industrial Control Systems (ICS) Security
- **ICS-CERT**: ICS Security Advisories and alerts

---

## Next Steps

1. **Experiment**: Load custom ladder logic, generate attacks, tune IDS
2. **Customize**: Extend protocols, add new detection rules, create scenarios
3. **Learn**: Study real ICS systems, compare to simulations
4. **Practice**: Red team exercises, blue team defense, incident response
5. **Contribute**: Submit improvements to the project repository

Happy learning! 🏭🔐
