# ICS/SCADA Detection Playbook for Defenders

## Overview

This playbook provides detection strategies, IOCs (Indicators of Compromise), and response procedures for defending industrial control systems against cyber attacks.

**Target Audience:** Blue Team, SOC Analysts, ICS Security Personnel

---

## Table of Contents

1. [Detection Strategies](#detection-strategies)
2. [IOC Categories](#ioc-categories)
3. [Network-Based Detection](#network-based-detection)
4. [Host-Based Detection](#host-based-detection)
5. [Modbus-Specific Detection](#modbus-specific-detection)
6. [Anomaly Detection](#anomaly-detection)
7. [Response Procedures](#response-procedures)
8. [Forensics & Investigation](#forensics--investigation)

---

## Detection Strategies

### Defense-in-Depth Layers

```
┌─────────────────────────────────────┐
│   Layer 1: Network Perimeter        │  Firewalls, IDS
├─────────────────────────────────────┤
│   Layer 2: Network Segmentation     │  VLANs, Micro-segmentation
├─────────────────────────────────────┤
│   Layer 3: Application Security     │  Authentication, Input validation
├─────────────────────────────────────┤
│   Layer 4: Protocol Monitoring      │  Modbus analysis, anomaly detection
├─────────────────────────────────────┤
│   Layer 5: Process Monitoring       │  Safety limits, process deviation
├─────────────────────────────────────┤
│   Layer 6: Physical Security        │  Access control, CCTV
└─────────────────────────────────────┘
```

### Key Detection Methods

1. **Signature-Based Detection**
   - Known exploit patterns
   - Malicious payloads
   - C2 communications

2. **Anomaly-Based Detection**
   - Baseline deviation
   - Unusual traffic patterns
   - Process value anomalies

3. **Behavioral Analysis**
   - User activity monitoring
   - Device behavior profiling
   - Network communication patterns

4. **Threat Intelligence**
   - Known IOCs from threat feeds
   - APT group TTPs
   - Vulnerability exploitation patterns

---

## IOC Categories

### Network IOCs

**Suspicious Traffic Patterns:**
- Unexpected cross-zone traffic (Corp -> OT)
- High-volume Modbus requests
- Modbus traffic from unknown sources
- Port scanning activity
- Unusual protocols on industrial network

**Example Zeek Log Entry:**
```
# Suspicious CorpNet to OT traffic
src_ip: 192.168.1.100 (Corp)
dst_ip: 192.168.100.10 (PLC-1)
dst_port: 502 (Modbus)
verdict: ALERT - Cross-zone violation
```

### Application IOCs

**Web Application Exploitation:**
- SQL injection attempts
- Command injection patterns
- Directory traversal attempts
- Multiple failed login attempts
- Session hijacking indicators

**Example Web Log:**
```
2024-12-07 10:15:32 192.168.1.100 POST /login
username=admin' OR '1'='1&password=x
Response: 302 Redirect
ALERT: SQL Injection Detected
```

### Process IOCs

**Abnormal Process Behavior:**
- Safety limits exceeded
- Rapid setpoint changes
- Simultaneous multiple alarms
- Process values outside normal range
- Emergency shutdowns

**Example Process Alert:**
```
Timestamp: 2024-12-07 10:20:45
PLC: PLC-2
Variable: pressure_vessel_1
Value: 180.5 PSI
Limit: 150.0 PSI
Status: CRITICAL OVERPRESSURE
```

### File System IOCs

**Suspicious File Activities:**
- Unauthorized file modifications
- New executables in system directories
- Modified PLC logic files
- Unusual file access patterns
- Backup file tampering

---

## Network-Based Detection

### 1. Zeek IDS Configuration

**Modbus Detection Script:**

```zeek
# modbus_detect.zeek
@load base/protocols/modbus

event modbus_message(c: connection, is_orig: bool, header: ModbusHeader, pdu: string)
{
    # Detect writes to critical registers
    if (header$function_code == 6 || header$function_code == 16) {
        print fmt("MODBUS WRITE: %s -> %s Function=%d",
                  c$id$orig_h, c$id$resp_h, header$function_code);

        # Alert on safety system writes
        if (c$id$resp_p == 5505/tcp) {
            NOTICE([$note=ModbusSafetyWrite,
                    $msg=fmt("Write to safety PLC from %s", c$id$orig_h),
                    $conn=c,
                    $identifier=cat(c$id$orig_h, c$id$resp_h)]);
        }
    }

    # Detect excessive polling
    local key = cat(c$id$orig_h, c$id$resp_h);
    if (key !in modbus_rate_tracker) {
        modbus_rate_tracker[key] = 0;
    }
    modbus_rate_tracker[key] += 1;

    if (modbus_rate_tracker[key] > 100) {  # More than 100 req/min
        NOTICE([$note=ModbusFlooding,
                $msg=fmt("Excessive Modbus traffic from %s", c$id$orig_h),
                $conn=c]);
    }
}

# Detect cross-zone violations
event connection_state_remove(c: connection)
{
    # Check if Corp network accessing OT
    if (/192\.168\.1\./ in c$id$orig_h && /192\.168\.100\./ in c$id$resp_h) {
        NOTICE([$note=CrossZoneViolation,
                $msg=fmt("CorpNet -> OT traffic: %s -> %s",
                        c$id$orig_h, c$id$resp_h),
                $conn=c]);
    }
}
```

**Zeek Alerts to Monitor:**
```
- ModbusSafetyWrite: Writes to safety PLC
- ModbusFlooding: Excessive Modbus traffic
- CrossZoneViolation: Unexpected network zone traversal
- UnauthorizedModbusSource: Unknown device sending Modbus
- ModbusAnomalousFunction: Unusual function codes
```

### 2. Suricata IDS Rules

**Custom ICS Rules:**

```
# Detect SQL injection attempts
alert http any any -> any any (msg:"SQL Injection in Login";
  flow:established,to_server;
  content:"POST"; http_method;
  content:"/login"; http_uri;
  pcre:"/username=.*?(\'|%27).*(OR|or).*(\'|%27)/i";
  classtype:web-application-attack;
  sid:1000001; rev:1;)

# Detect command injection
alert http any any -> any any (msg:"Command Injection Attempt";
  flow:established,to_server;
  content:"POST"; http_method;
  pcre:"/(;|%3B|\||%7C|&|%26).*(ls|cat|whoami|wget|curl)/i";
  classtype:attempted-admin;
  sid:1000002; rev:1;)

# Detect Modbus writes to safety PLC
alert tcp any any -> any 5505 (msg:"Modbus Write to Safety PLC";
  content:"|00 00|"; offset:0; depth:2;  # Transaction ID
  content:"|00 00|"; offset:2; depth:2;  # Protocol ID
  byte_test:1,>,5,7;  # Function code > 5 (write functions)
  threshold:type both, track by_src, count 5, seconds 60;
  classtype:attempted-dos;
  sid:1000003; rev:1;)

# Detect excessive Modbus requests (DoS)
alert tcp any any -> any 502:505 (msg:"Modbus Flooding Detected";
  flags:A+;
  detection_filter:track by_src, count 100, seconds 10;
  classtype:attempted-dos;
  sid:1000004; rev:1;)

# Detect unauthorized Modbus source
alert tcp !$HOME_NET any -> any 502:505 (msg:"Modbus from External IP";
  flags:S;
  classtype:attempted-recon;
  sid:1000005; rev:1;)

# Detect directory traversal
alert http any any -> any any (msg:"Directory Traversal Attack";
  flow:established,to_server;
  content:".."; http_uri; nocase;
  pcre:"/\.\.(\/|%2F|\\|%5C)/i";
  classtype:web-application-attack;
  sid:1000006; rev:1;)

# Detect historian injection
alert http any any -> any 8888 (msg:"Historian Data Injection";
  flow:established,to_server;
  content:"POST"; http_method;
  content:"/api/inject"; http_uri;
  classtype:web-application-attack;
  sid:1000007; rev:1;)
```

### 3. Network Traffic Baselines

**Normal Traffic Patterns:**

| Source | Destination | Protocol | Frequency | Purpose |
|--------|-------------|----------|-----------|---------|
| HMI (192.168.100.20) | PLC-1 (192.168.100.10) | Modbus (502) | 1 req/sec | Polling |
| HMI (192.168.100.20) | PLC-2 (192.168.100.11) | Modbus (502) | 1 req/sec | Polling |
| HMI (192.168.100.20) | PLC-3 (192.168.100.12) | Modbus (502) | 1 req/sec | Polling |
| HMI (192.168.100.20) | PLC-4 (192.168.100.13) | Modbus (502) | 1 req/sec | Polling |
| Historian (192.168.50.10) | All PLCs | Modbus (502) | 1 req/5sec | Data collection |
| Eng WS (192.168.100.30) | PLCs | Modbus (502) | Occasional | Maintenance |

**Anomalous Patterns:**

- ❌ Corp laptop (192.168.1.x) -> PLC (Unauthorized)
- ❌ Unknown device (192.168.100.99) -> PLCs (Misbehaving device)
- ❌ PLC -> Internet (C2 communication)
- ❌ External IP -> Modbus port (Attack)
- ❌ >10 req/sec from single source (Flooding)

---

## Host-Based Detection

### 1. Log Analysis

**Critical Log Files:**

```bash
# Web application logs
/var/log/nginx/access.log
/var/log/flask/app.log

# System logs
/var/log/syslog
/var/log/auth.log

# Application-specific
./plc.db (SQLite database)
./historian.db (Historian database)
```

**Suspicious Log Entries:**

```bash
# SQL Injection attempts
grep -i "OR '1'='1" /var/log/nginx/access.log
grep -i "UNION SELECT" /var/log/nginx/access.log

# Command injection
grep -i "ls -la" /var/log/flask/app.log
grep -i "whoami" /var/log/flask/app.log

# Failed authentication
grep "Failed login" /var/log/flask/app.log
grep "401 Unauthorized" /var/log/nginx/access.log

# Privilege escalation
grep "role.*admin" /var/log/flask/app.log

# File access anomalies
grep "/backup" /var/log/nginx/access.log
grep "etc/passwd" /var/log/nginx/access.log
```

### 2. File Integrity Monitoring

**Critical Files to Monitor:**

```bash
# PLC configuration files
/var/plc/config/*.cfg
/var/plc/logic/*.ladder

# Application code
/home/*/vulnerable_plc/*.py
/home/*/vulnerable_plc/templates/*.html

# Database files
plc.db
historian.db

# System files
/etc/passwd
/etc/shadow
/etc/crontab
```

**FIM Configuration (AIDE):**

```bash
# /etc/aide/aide.conf
/home/*/vulnerable_plc/app.py R+b+sha256
/home/*/vulnerable_plc/*.py R+b+sha256
/home/*/vulnerable_plc/plc.db R+b+sha256
/home/*/vulnerable_plc/historian.db R+b+sha256

# Run integrity check
aide --check
```

### 3. Process Monitoring

**Normal Processes:**

```bash
# Expected processes
python app.py (PLC-1 web interface)
python modbus_server.py (PLC-1 Modbus)
python plc2_pressure.py
python modbus_server2.py
python plc3_temperature.py
python modbus_server3.py
python plc4_safety.py
python modbus_server4.py
python historian.py
python network_simulator.py
```

**Suspicious Processes:**

```bash
# Unexpected network tools
nc -l -p 4444  # Reverse shell
nmap 192.168.100.0/24  # Scanning
tcpdump -i eth0  # Packet capture

# Unauthorized Python scripts
python attack.py
python exploit.py
python backdoor.py
```

**Process Monitoring Script:**

```bash
#!/bin/bash
# monitor_processes.sh

# List of allowed processes
ALLOWED_PROCS=(
    "app.py"
    "modbus_server.py"
    "plc2_pressure.py"
    "modbus_server2.py"
    "plc3_temperature.py"
    "modbus_server3.py"
    "plc4_safety.py"
    "modbus_server4.py"
    "historian.py"
    "network_simulator.py"
)

# Get all Python processes
ps aux | grep python | grep -v grep | while read line; do
    proc=$(echo $line | awk '{print $11}')

    # Check if process is in allowed list
    allowed=false
    for allowed_proc in "${ALLOWED_PROCS[@]}"; do
        if [[ "$proc" == *"$allowed_proc"* ]]; then
            allowed=true
            break
        fi
    done

    if [ "$allowed" = false ]; then
        echo "[ALERT] Unauthorized process: $proc"
        echo "$line"
    fi
done
```

---

## Modbus-Specific Detection

### 1. Modbus Function Code Analysis

**Normal Function Codes:**
- FC01: Read Coils (legitimate polling)
- FC03: Read Holding Registers (legitimate polling)
- FC04: Read Input Registers (legitimate polling)

**Suspicious Function Codes:**
- FC05: Write Single Coil (control action - verify source)
- FC06: Write Single Register (control action - verify source)
- FC15: Write Multiple Coils (bulk write - suspicious)
- FC16: Write Multiple Registers (bulk write - suspicious)

**Detection Logic:**

```python
#!/usr/bin/env python3
# modbus_monitor.py

from pymodbus.client.sync import ModbusTcpClient
import time
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

PLCS = [
    ('PLC-1', 'localhost', 5502),
    ('PLC-2', 'localhost', 5503),
    ('PLC-3', 'localhost', 5504),
    ('PLC-4', 'localhost', 5505),
]

# Store previous values for change detection
previous_values = {}

def monitor_plc(name, host, port):
    """Monitor PLC for unauthorized changes"""
    client = ModbusTcpClient(host, port=port)

    # Read holding registers
    result = client.read_holding_registers(0, 100)
    if result:
        current_values = result.registers

        key = f"{name}_holding"
        if key in previous_values:
            # Check for changes
            for i, (prev, curr) in enumerate(zip(previous_values[key], current_values)):
                if prev != curr:
                    log.warning(f"[{name}] Register {i} changed: {prev} -> {curr}")

                    # Check for dangerous values
                    if name == 'PLC-2' and i == 0 and curr > 1500:  # Pressure > 150 PSI
                        log.error(f"[{name}] CRITICAL: Pressure exceeds safe limit!")

                    if name == 'PLC-3' and i == 0 and curr > 800:  # Temp > 80°C
                        log.error(f"[{name}] CRITICAL: Temperature exceeds safe limit!")

        previous_values[key] = current_values

    # Read coils
    result = client.read_coils(0, 50)
    if result:
        coils = result.bits

        key = f"{name}_coils"
        if key in previous_values:
            for i, (prev, curr) in enumerate(zip(previous_values[key], coils)):
                if prev != curr:
                    log.warning(f"[{name}] Coil {i} changed: {prev} -> {curr}")

                    # Check for safety system bypass
                    if name == 'PLC-4' and i == 40 and curr == True:
                        log.error(f"[{name}] CRITICAL: Safety bypass enabled!")

        previous_values[key] = coils

    client.close()

# Monitor loop
while True:
    for name, host, port in PLCS:
        try:
            monitor_plc(name, host, port)
        except Exception as e:
            log.error(f"Error monitoring {name}: {e}")

    time.sleep(5)
```

### 2. Register Change Alerting

**Critical Register Monitors:**

```yaml
# critical_registers.yaml

PLC-2:
  register_0:  # Pressure vessel 1
    name: "Pressure Vessel 1"
    critical_value: 1500  # 150.0 PSI
    unit: "PSI (x10)"
    alert_level: "CRITICAL"

PLC-3:
  register_0:  # Zone 1 temperature
    name: "Zone 1 Temperature"
    critical_value: 800  # 80.0°C
    unit: "°C (x10)"
    alert_level: "CRITICAL"

  coil_10:  # Thermal runaway
    name: "Thermal Runaway Mode"
    critical_value: True
    alert_level: "CRITICAL"

PLC-4:
  coil_40:  # Safety bypass
    name: "Safety Bypass Mode"
    critical_value: True
    alert_level: "CRITICAL"

  coil_41:  # Watchdog
    name: "Watchdog Enabled"
    critical_value: False
    alert_level: "HIGH"
```

---

## Anomaly Detection

### 1. Statistical Baselines

**Process Value Baselines:**

```python
#!/usr/bin/env python3
# baseline_monitor.py

import numpy as np
import shared_state

# Define normal ranges (mean ± 3 std dev)
BASELINES = {
    'tank1_level': {'mean': 50.0, 'std': 10.0, 'min': 20.0, 'max': 80.0},
    'plc2_pressure_vessel_1': {'mean': 105.0, 'std': 10.0, 'min': 80.0, 'max': 130.0},
    'plc3_zone1_temp': {'mean': 25.0, 'std': 5.0, 'min': 15.0, 'max': 35.0},
}

def check_anomalies():
    state = shared_state.load_state()

    for key, baseline in BASELINES.items():
        if key in state:
            value = state[key]

            # Check if value is outside normal range
            if value < baseline['min'] or value > baseline['max']:
                print(f"[ANOMALY] {key} = {value} (Normal: {baseline['min']}-{baseline['max']})")

                # Calculate z-score
                z_score = (value - baseline['mean']) / baseline['std']
                if abs(z_score) > 3:
                    print(f"  [CRITICAL] Z-score: {z_score:.2f} (>3 standard deviations!)")

check_anomalies()
```

### 2. Time-Series Analysis

**Detect Rapid Changes:**

```python
#!/usr/bin/env python3
# rapid_change_detector.py

import sqlite3
from datetime import datetime, timedelta

def detect_rapid_changes():
    conn = sqlite3.connect('historian.db')
    c = conn.cursor()

    # Get data from last 5 minutes
    start_time = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')

    c.execute("""
        SELECT timestamp, tag_name, value
        FROM timeseries
        WHERE timestamp > ? AND plc_id = 2 AND tag_name = 'pressure_vessel_1'
        ORDER BY timestamp ASC
    """, (start_time,))

    rows = c.fetchall()
    conn.close()

    # Check for rapid increases
    for i in range(1, len(rows)):
        prev_value = rows[i-1][2]
        curr_value = rows[i][2]

        change_rate = (curr_value - prev_value) / 5  # Per second

        if change_rate > 5:  # More than 5 PSI/sec increase
            print(f"[ALERT] Rapid pressure increase detected: {change_rate:.2f} PSI/sec")
            print(f"  Time: {rows[i][0]}")
            print(f"  Value: {prev_value} -> {curr_value}")

detect_rapid_changes()
```

---

## Response Procedures

### Incident Response Workflow

```
┌─────────────────────┐
│  1. DETECTION       │  Alert triggered
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  2. TRIAGE          │  Assess severity & impact
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  3. CONTAINMENT     │  Isolate affected systems
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  4. INVESTIGATION   │  Forensics & root cause
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  5. REMEDIATION     │  Fix vulnerabilities
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  6. RECOVERY        │  Restore normal operations
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  7. POST-MORTEM     │  Lessons learned
└─────────────────────┘
```

### Priority Levels

**P1 - CRITICAL (Respond immediately)**
- Safety system compromise
- Active process manipulation
- Potential physical damage
- Life safety risk

**P2 - HIGH (Respond within 1 hour)**
- Process value anomalies
- Unauthorized access to PLCs
- Safety limit approached
- Lateral movement detected

**P3 - MEDIUM (Respond within 4 hours)**
- Failed authentication attempts
- Reconnaissance activity
- Cross-zone traffic violations
- Suspicious file access

**P4 - LOW (Respond within 24 hours)**
- Policy violations
- Normal threshold deviations
- Non-critical alarms

---

## [Continued...]

This Detection Playbook provides comprehensive guidance for defenders. Would you like me to continue with the Forensics & Investigation section, or move on to creating the Evasion Techniques guide and final docker-compose orchestration?

