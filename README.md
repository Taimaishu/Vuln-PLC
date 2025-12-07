# Vulnerable PLC - ICS/SCADA Security Training Lab

A comprehensive, intentionally vulnerable industrial control system environment for security training, penetration testing practice, and ICS/SCADA research. Features 4 PLCs, historian service, realistic network traffic, OSINT artifacts, and 200+ pages of documentation.

## ⚠️ WARNING

**THIS IS AN INTENTIONALLY VULNERABLE APPLICATION**

- **DO NOT** deploy on production networks
- **DO NOT** expose to the internet
- **ONLY** use in isolated lab environments
- For authorized security testing and education only

## Recent Updates

### Major Enhancements (2024-12-07)
- 🚀 **NEW**: Realistic PLC simulation engine with scan cycles and ladder logic
- 🚀 **NEW**: Modbus intrusion detection system (IDS) with real-time alerts
- 🚀 **NEW**: Siemens S7 protocol support (educational implementation)
- 🚀 **NEW**: System monitoring dashboard (console + web interface)
- ✅ Fixed PLC-1 Modbus server sync feedback loop
- ✅ Added full user management system (add/edit/delete users)
- ✅ Added PLC-4 watchdog enable/disable controls
- ✅ Optimized network traffic log (reduced from 1000 to 100 entries)
- ✅ Comprehensive Blue Team training documentation

## Features

### Web Interface
- **Login System** with default credentials
- **Admin Portal** with system controls
- **User Management** interface (full CRUD)
- **System Logs** viewer
- **PLC Control Dashboard**

### Modbus TCP Server
- Standard Modbus TCP protocol on port 5502
- 100 coils (read/write)
- 100 discrete inputs (read-only)
- 100 holding registers (read/write)
- 100 input registers (read-only)
- Simulated sensor readings

### System Components

1. **PLC-1: Tank Control System**
   - Web: http://localhost:5000 (admin/admin)
   - Modbus: localhost:5502
   - Vulnerabilities: SQL injection, command injection, XSS, SSTI, directory traversal

2. **PLC-2: Pressure Control System**
   - Web: http://localhost:5011 (engineer/plc2pass)
   - Modbus: localhost:5503
   - Vulnerabilities: Timing attacks, auth bypass, replay attacks, buffer overflow

3. **PLC-3: Temperature Control System**
   - Web: http://localhost:5012 (engineer/temp123)
   - Modbus: localhost:5504
   - Vulnerabilities: Insecure firmware upload, pickle deserialization, race conditions

4. **PLC-4: Safety/Emergency Shutdown System**
   - Web: http://localhost:5013 (safety_eng/safe123)
   - Modbus: localhost:5505
   - Vulnerabilities: Weak override code (1234), safety bypass, timing attacks

5. **Historian Service**
   - Web: http://localhost:8888 (historian/data123)
   - Collects data from all PLCs every 5 seconds
   - Vulnerabilities: SQL injection, time-series injection

6. **Network Traffic Simulator**
   - Generates realistic ICS traffic patterns
   - HMI polling, historian queries, engineering access
   - Simulates packet loss and misbehaving devices
   - Automated safety incidents

7. **OSINT Artifacts**
   - Network diagrams with credentials
   - Employee directory
   - Meeting notes with security findings
   - Shodan scan results
   - PLC backup configurations

8. **Advanced Features (NEW)**
   - **PLC Simulation Engine**: Realistic scan cycles, ladder logic execution
   - **Modbus IDS**: Real-time intrusion detection with alerts
   - **S7 Protocol Server**: Siemens S7comm support (port 102)
   - **System Monitor**: Centralized dashboard (console + web)

### Network Architecture

Based on Purdue Model:
- **CorpNet**: 192.168.1.0/24 (Corporate network)
- **OT Zone**: 192.168.100.0/24 (Operational Technology - PLCs, HMI)
- **DMZ**: 192.168.50.0/24 (Historian, web portal)
- **Firewall**: Intentionally misconfigured (ALLOW_ALL between zones)

### Documentation (300+ pages)

- **ARCHITECTURE.md** (30+ pages) - Complete system architecture
- **OSINT_DISCOVERY_GUIDE.md** (40+ pages) - OSINT techniques
- **ATTACK_SCENARIOS.md** (50+ pages) - Detailed attack walkthroughs
- **DETECTION_PLAYBOOK.md** (45+ pages) - Defense strategies and IOCs
- **EVASION_TECHNIQUES.md** (35+ pages) - Advanced evasion tactics
- **ADVANCED_FEATURES.md** (50+ pages) - NEW: PLC engine, IDS, S7 protocol
- **BLUE_TEAM_GUIDE.md** (40+ pages) - NEW: Defense and incident response
- **FINAL_SUMMARY.md** (10+ pages) - Quick reference guide

---

## Quick Start

### Installation

First, install the system-wide command:

```bash
cd /home/taimaishu/vulnerable_plc
./install.sh
```

This creates a `vuln-plc` command you can run from anywhere.

### Starting the Lab

```bash
vuln-plc start
```

This starts all 4 PLCs, the Historian service, and the network traffic simulator.

### Managing Services

```bash
vuln-plc status      # Check which services are running
vuln-plc stop        # Stop all services
vuln-plc restart     # Restart everything
vuln-plc logs        # Monitor all logs in real-time
vuln-plc help        # Show help
```

### Alternative: Manual Start

```bash
cd /home/taimaishu/vulnerable_plc
./start_all.sh       # Start all services
./status.sh          # Check status
./stop_all.sh        # Stop all services
```

## Access Points

### Web Interfaces
- **PLC-1 (Tank Control):** http://localhost:5000 (admin/admin)
- **PLC-2 (Pressure System):** http://localhost:5011 (engineer/plc2pass)
- **PLC-3 (Temperature Control):** http://localhost:5012 (engineer/temp123)
- **PLC-4 (Safety/ESD):** http://localhost:5013 (safety_eng/safe123)
- **Historian:** http://localhost:8888 (historian/data123)

### Modbus TCP Endpoints
- **PLC-1:** localhost:5502
- **PLC-2:** localhost:5503
- **PLC-3:** localhost:5504
- **PLC-4:** localhost:5505

### All Default Credentials
See `FINAL_SUMMARY.md` for complete credential list

---

## Security Testing Guide

See comprehensive testing guides in the documentation files, including:
- SQL Injection techniques
- Command Injection exploits
- Modbus manipulation
- Network reconnaissance
- OSINT discovery
- IDS evasion techniques

### Advanced Testing (NEW)

**PLC Engine Testing:**
```python
from plc_engine import PLCEngine, Instruction, InstructionType

# Create PLC with 50ms scan cycle
engine = PLCEngine('plc1', scan_time_ms=50)

# Load ladder logic
program = [
    Instruction(InstructionType.CMP, ['tank_level', '<', '30']),
    Instruction(InstructionType.OUT, ['pump_status']),
]
engine.load_program(program)
engine.start()
```

**Modbus IDS Testing:**
```python
from modbus_ids import ModbusIDS

# Start IDS with monitoring
ids = ModbusIDS()
ids.add_authorized_writer('192.168.100.20')
ids.add_protected_address(10)
ids.start()

# Generate test attacks - observe alerts!
```

**System Monitoring:**
```bash
# Console dashboard
python3 system_monitor.py

# Web dashboard (recommended)
python3 system_monitor.py --web
# Access at http://localhost:5999
```

**S7 Protocol Testing:**
```python
import snap7

# Connect to S7 server (requires root for port 102)
plc = snap7.client.Client()
plc.connect('localhost', 0, 1, 102)

# Read/write data blocks
data = plc.db_read(1, 0, 10)
plc.db_write(1, 0, bytearray([0x01, 0x02]))

# VULNERABILITY: Stop PLC without auth!
plc.plc_stop()
```

---

## Legal Notice

This tool is provided for **educational and authorized security testing purposes only**.

You must:
- Only use in isolated lab environments
- Have explicit authorization before testing
- Not use for malicious purposes
- Not expose to production networks
- Comply with all applicable laws

The authors assume no liability for misuse of this software.

---

## Credits

Created for security education and ICS/SCADA security awareness training.

**Technologies Used:**
- Python 3.9
- Flask web framework
- PyModbus library
- SQLite database

---

**Remember: Use responsibly and only in authorized environments.**
