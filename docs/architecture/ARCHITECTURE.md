# ICS/SCADA Security Training Lab - Architecture

## Overview

This is a comprehensive ICS/SCADA security training environment based on the Purdue Model for Industrial Control Systems. It includes multiple PLCs, a historian, engineering workstation, and integrated detection systems.

## Network Architecture (Purdue Model)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Level 4-5: Enterprise Zone                                          │
│ - Corporate network                                                  │
│ - Business systems                                                   │
└─────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │ Firewall
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Level 3.5: DMZ                                                       │
│ - Historian (Port 8086 - InfluxDB API)                             │
│ - Historian Web UI (Port 8888)                                      │
│ - Grafana Dashboards (Port 3000)                                    │
└─────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │ Firewall
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Level 2-3: Control/Supervisory Zone                                 │
│ - HMI/SCADA Server (Port 5000)                                      │
│ - Engineering Workstation (Port 5020)                               │
│ - IDS/IPS Systems:                                                   │
│   • Zeek (Network monitoring)                                        │
│   • Suricata (Port 8080 - Management UI)                           │
│   • Snort (Inline detection)                                        │
└─────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │ Industrial Firewall
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Level 1: Field Control Zone                                          │
│                                                                       │
│ PLC Network (192.168.100.0/24)                                       │
│                                                                       │
│ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│ │ PLC-1           │  │ PLC-2           │  │ │ PLC-3           │     │
│ │ Tank Control    │  │ Pressure System │  │ Temperature     │     │
│ │ Modbus: 5502    │  │ Modbus: 5503    │  │ Modbus: 5504    │     │
│ │ Web: 5010       │  │ Web: 5011       │  │ Web: 5012       │     │
│ └─────────────────┘  └─────────────────┘  └─────────────────┘     │
│                                                                       │
│ ┌─────────────────┐                                                  │
│ │ PLC-4           │                                                  │
│ │ Safety/ESD      │                                                  │
│ │ Modbus: 5505    │                                                  │
│ │ Web: 5013       │                                                  │
│ └─────────────────┘                                                  │
└─────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Level 0: Field Devices                                               │
│ - Sensors (simulated in PLCs)                                        │
│ - Actuators (simulated in PLCs)                                      │
│ - I/O Modules                                                        │
└─────────────────────────────────────────────────────────────────────┘
```

## Components

### PLC Descriptions

#### PLC-1: Tank Control System (Original)
- **Role**: Liquid level control, primary process control
- **Modbus Port**: 5502
- **Web Interface**: 5000
- **Registers**:
  - 0-19: Tank 1 controls (level, temp, pressure)
  - 20-39: Tank 2 controls
  - 40-49: Pump controls
  - 50-59: Valve controls
- **Vulnerabilities**: SQL injection, command injection, XSS, SSTI, directory traversal

#### PLC-2: Pressure Control System
- **Role**: Compressor and pressure vessel control
- **Modbus Port**: 5503
- **Web Interface**: 5011
- **Registers**:
  - 0-19: Pressure vessel 1
  - 20-39: Pressure vessel 2
  - 40-49: Compressor controls
  - 50-59: Relief valve controls
- **Vulnerabilities**: Authentication bypass, buffer overflow (simulated), replay attacks

#### PLC-3: Temperature Control System
- **Role**: Heating/cooling system, thermal process control
- **Modbus Port**: 5504
- **Web Interface**: 5012
- **Registers**:
  - 0-19: Heater controls
  - 20-39: Cooler controls
  - 40-49: Temperature sensors
  - 50-59: Thermal safety limits
- **Vulnerabilities**: Firmware upload bypass, insecure deserialization, race conditions

#### PLC-4: Safety/Emergency Shutdown System (ESD)
- **Role**: Emergency stop, safety interlocks, critical safety functions
- **Modbus Port**: 5505
- **Web Interface**: 5013
- **Registers**:
  - 0-9: Emergency stop states
  - 10-19: Safety interlocks
  - 20-29: Fire/gas detection
  - 30-39: Critical alarm states
- **Vulnerabilities**: Weak authentication, timing attacks, safety system bypass

### Historian System

**Technology**: InfluxDB 2.x compatible storage

**Ports**:
- 8086: InfluxDB API
- 8888: Historian Web Interface

**Features**:
- Collects data from all PLCs every 1-5 seconds
- Stores process variables, alarms, events
- Provides query API for trending
- Web interface for data visualization
- **Vulnerabilities**: Time-series injection, unauthorized data access, query injection

### Engineering Workstation

**Port**: 5020

**Features**:
- Ladder logic editor (simplified)
- PLC programming interface
- Firmware upload/download
- Configuration management
- Diagnostic tools
- **Vulnerabilities**: Insecure firmware updates, code injection in logic editor, credential theft

### Detection Systems

#### Zeek (Network Security Monitor)
- Monitors all traffic between zones
- Generates conn.log, modbus.log, http.log
- Custom ICS protocol parsers
- Anomaly detection scripts

#### Suricata (IDS/IPS)
- Port 8080: Management UI
- ICS/SCADA rule sets
- Modbus protocol detection
- Attack signature detection
- ET Open rules + custom ICS rules

#### Grafana Dashboards
- Port 3000
- Real-time monitoring
- Alert visualization
- Process trends
- Security events dashboard
- Network traffic analysis

## Attack Toolkit

### Modbus Attack Tools (Port 5002 - Attack Console)

1. **Packet Crafter**
   - Build custom Modbus TCP packets
   - Function code manipulation
   - CRC/checksum bypass
   - Malformed packet testing

2. **Replay Attack Tool**
   - Capture legitimate Modbus traffic
   - Store and replay commands
   - Timing analysis
   - Session hijacking

3. **Register Fuzzer**
   - Automated fuzzing of all register addresses
   - Value boundary testing
   - Function code fuzzing
   - Crash/hang detection

4. **Bit Flipper**
   - Systematic bit manipulation
   - Single-bit error injection
   - Multi-bit pattern testing
   - Error handling analysis

5. **Denial-of-View (DoV) Attacks**
   - Flood historian with bad data
   - Corrupt HMI display values
   - Manipulate trending data
   - Hide malicious activity

6. **Denial-of-Control (DoC) Attacks**
   - Lock out operators
   - Block legitimate commands
   - Fill command queues
   - Induce safety shutdowns

7. **Custom Modbus Client Builder**
   - Interactive client creation
   - Function code tester
   - Multi-PLC coordinator
   - Scripted attack sequences

## Additional Protocols

### DNP3 (Distributed Network Protocol)
- Port 20000
- Power/utility grid simulation
- SCADA-to-RTU communication
- Vulnerable to authentication bypass

### OPC-UA (OPC Unified Architecture)
- Port 4840
- Modern industrial protocol
- Certificate-based security (weak implementation)
- Vulnerable to certificate forgery

## Network Segmentation

### VLAN Configuration
- VLAN 100: PLC Network (Field Zone)
- VLAN 200: Control Network (SCADA/HMI)
- VLAN 300: DMZ (Historian)
- VLAN 400: Enterprise

### Firewall Rules (Intentionally Weak)
- Allows cross-zone traffic for testing
- Logging enabled for all traffic
- Vulnerable rules for privilege escalation
- Misconfigured NAT for exploitation

## Security Monitoring

### Log Sources
1. **Application Logs**: All web services log to centralized syslog
2. **Modbus Logs**: All Modbus transactions logged
3. **Authentication Logs**: Login attempts, session data
4. **Network Logs**: Zeek, Suricata, Snort outputs
5. **Process Logs**: PLC state changes, alarm events

### Alert Categories
- **Critical**: Safety system compromise, emergency stop manipulation
- **High**: Unauthorized PLC programming, firmware changes
- **Medium**: Unusual Modbus traffic, failed authentication
- **Low**: Reconnaissance, port scans, information gathering

## Learning Objectives

### For Red Team (Attackers)
1. Reconnaissance of ICS networks
2. Identifying PLCs and their functions
3. Exploiting web vulnerabilities to gain initial access
4. Pivoting to PLC network
5. Crafting Modbus attacks
6. Manipulating process values
7. Evading IDS detection
8. Maintaining persistence
9. Causing physical process impact

### For Blue Team (Defenders)
1. Network monitoring and baseline creation
2. Detecting reconnaissance activity
3. Identifying Modbus anomalies
4. Analyzing logs for IOCs
5. Responding to incidents
6. Implementing compensating controls
7. Hardening ICS systems
8. Forensic analysis

## Data Flow

```
Physical Process (Simulated)
        ▼
Field Devices (Sensors/Actuators)
        ▼
PLCs (Modbus TCP Servers)
        ▼
HMI/SCADA (Monitoring/Control)
        ▼
Historian (Data Storage)
        ▼
Enterprise (Reporting/Analysis)
```

## Attack Scenarios

### Scenario 1: Web-to-PLC Compromise
1. Exploit SQL injection in HMI
2. Gain admin access
3. Use command injection to pivot
4. Scan PLC network
5. Craft Modbus attacks
6. Manipulate process values

### Scenario 2: Modbus-Only Attack
1. Direct access to Modbus network
2. Enumerate all PLCs
3. Read all registers (reconnaissance)
4. Write malicious values
5. Trigger safety systems
6. Evade detection

### Scenario 3: Historian Poisoning
1. Compromise historian
2. Inject false data
3. Hide attack indicators
4. Manipulate trends
5. Cause operator confusion

### Scenario 4: Engineering Workstation Compromise
1. Exploit firmware upload
2. Install backdoored PLC code
3. Establish persistence
4. Remote access to all PLCs

### Scenario 5: Multi-Stage APT
1. Initial web exploitation
2. Lateral movement
3. Credential harvesting
4. Engineering workstation access
5. PLC reprogramming
6. Long-term manipulation

## Detection Use Cases

### UC-1: Unauthorized Modbus Write
- Detect writes from unknown sources
- Alert on critical register changes
- Log all write operations

### UC-2: Reconnaissance Activity
- Port scanning detection
- Service enumeration
- Register scanning patterns

### UC-3: Replay Attacks
- Detect duplicate Modbus transactions
- Timing analysis
- Sequence number anomalies

### UC-4: Denial of Service
- High request rates
- Malformed packets
- Resource exhaustion

### UC-5: Man-in-the-Middle
- ARP spoofing detection
- Unexpected routing changes
- Certificate anomalies (OPC-UA)

## Evasion Techniques

1. **Slow and Low**: Spread attacks over time
2. **Blending**: Mimic legitimate traffic patterns
3. **Fragmentation**: Split attacks across packets
4. **Protocol Abuse**: Use legitimate features maliciously
5. **Encryption**: Tunnel attacks through encrypted channels
6. **Timing**: Attack during maintenance windows

## File Structure

```
vulnerable_plc/
├── app.py                      # Main HMI/SCADA (PLC-1)
├── plc2_pressure.py           # PLC-2 server
├── plc3_temperature.py        # PLC-3 server
├── plc4_safety.py             # PLC-4 server
├── modbus_server.py           # PLC-1 Modbus
├── modbus_server2.py          # PLC-2 Modbus
├── modbus_server3.py          # PLC-3 Modbus
├── modbus_server4.py          # PLC-4 Modbus
├── historian.py               # Historian service
├── engineering_workstation.py # Engineering tools
├── attack_console.py          # Attack toolkit web UI
├── shared_state.py            # Shared state management
├── ids_monitor.py             # IDS aggregation
├── docker-compose.yml         # All services orchestration
├── zeek/                      # Zeek configuration
├── suricata/                  # Suricata rules
├── grafana/                   # Grafana dashboards
├── templates/                 # HTML templates
├── tools/                     # Attack scripts
│   ├── modbus_fuzzer.py
│   ├── replay_attack.py
│   ├── bit_flipper.py
│   ├── register_scanner.py
│   └── packet_crafter.py
└── docs/                      # Documentation
    ├── ATTACK_SCENARIOS.md
    ├── DETECTION_GUIDE.md
    ├── EVASION_TECHNIQUES.md
    └── CTF_CHALLENGES.md
```

## Getting Started

### Quick Start (Docker)
```bash
docker-compose up --build
```

### Access Points
- HMI/SCADA: http://localhost:5000
- Engineering Workstation: http://localhost:5020
- Attack Console: http://localhost:5002
- Grafana: http://localhost:3000
- Historian: http://localhost:8888
- Suricata UI: http://localhost:8080
- PLC-2 Web: http://localhost:5011
- PLC-3 Web: http://localhost:5012
- PLC-4 Web: http://localhost:5013

### Modbus Endpoints
- PLC-1: localhost:5502
- PLC-2: localhost:5503
- PLC-3: localhost:5504
- PLC-4: localhost:5505

## Safety Notice

**THIS IS A TRAINING ENVIRONMENT ONLY**

- Use only in isolated networks
- Do not connect to production systems
- Practice responsible disclosure
- Follow ethical hacking guidelines
- Understand legal implications

## License

For educational and authorized security testing only.
