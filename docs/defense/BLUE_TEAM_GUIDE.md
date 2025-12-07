# Blue Team Defense Guide

Comprehensive guide for defending ICS/SCADA environments using Vuln-PLC as a training platform.

## Table of Contents

1. [Defense Strategy](#defense-strategy)
2. [Monitoring & Detection](#monitoring--detection)
3. [Incident Response](#incident-response)
4. [Hardening Recommendations](#hardening-recommendations)
5. [Training Exercises](#training-exercises)

---

## Defense Strategy

### Defense in Depth

Implement multiple layers of security:

```
┌─────────────────────────────────────────┐
│  Layer 7: Policy & Procedures          │
├─────────────────────────────────────────┤
│  Layer 6: User Education & Training    │
├─────────────────────────────────────────┤
│  Layer 5: Application Security         │
├─────────────────────────────────────────┤
│  Layer 4: Host Security (PLCs)         │
├─────────────────────────────────────────┤
│  Layer 3: Network Security (IDS/IPS)   │
├─────────────────────────────────────────┤
│  Layer 2: Perimeter Security (FW)      │
├─────────────────────────────────────────┤
│  Layer 1: Physical Security            │
└─────────────────────────────────────────┘
```

### Purdue Model Implementation

Proper network segmentation:

```
┌────────────────────────────────────┐
│  Enterprise Zone (IT)              │  Level 4-5
│  - Business systems                │
│  - Email, ERP, etc.                │
└────────────┬───────────────────────┘
             │ DMZ with firewall
┌────────────▼───────────────────────┐
│  DMZ / Industrial DMZ              │  Level 3.5
│  - Historian                       │
│  - Engineering workstations        │
│  - Jump servers                    │
└────────────┬───────────────────────┘
             │ Strict firewall rules
┌────────────▼───────────────────────┐
│  Control Zone (SCADA/HMI)          │  Level 2-3
│  - HMI servers                     │
│  - SCADA systems                   │
│  - Data concentrators              │
└────────────┬───────────────────────┘
             │ Industrial firewall
┌────────────▼───────────────────────┐
│  Process Zone (PLCs)               │  Level 0-1
│  - PLCs, RTUs, IEDs                │
│  - Field devices                   │
│  - Sensors & actuators             │
└────────────────────────────────────┘
```

---

## Monitoring & Detection

### 1. Deploy Modbus IDS

Configure comprehensive monitoring:

```python
from modbus_ids import ModbusIDS

# Initialize IDS
ids = ModbusIDS()

# Whitelist authorized systems
ids.add_authorized_writer('192.168.100.20')  # Primary HMI
ids.add_authorized_writer('192.168.100.30')  # Engineering WS
ids.add_authorized_writer('192.168.50.10')   # Historian

# Protect critical addresses
ids.add_protected_address(10)  # Emergency stop
ids.add_protected_address(11)  # Safety interlock
ids.add_protected_address(15)  # Critical valve
ids.add_protected_address(20)  # Master shutdown

# Start monitoring
ids.start()
```

### 2. Baseline Normal Traffic

Establish what "normal" looks like:

```bash
# Collect 24 hours of baseline
python3 modbus_ids.py --baseline --duration 86400

# Analyze patterns
- Typical function code distribution
- Expected source IPs
- Normal command rates
- Hourly traffic patterns
```

Typical baseline for water treatment plant:

| Metric | Normal Range |
|--------|--------------|
| HMI polling rate | 1-2 req/sec per PLC |
| Historian collection | Every 5-10 seconds |
| Engineering access | 0-5 req/hour |
| Function codes | 90% FC03/04 (reads), 10% FC06/16 (writes) |

### 3. Real-Time Monitoring Dashboard

Use system monitor for centralized visibility:

```bash
# Console mode
python3 system_monitor.py

# Web dashboard (recommended)
python3 system_monitor.py --web
# Access at http://localhost:5999
```

Monitor these key metrics:

✅ **PLC Health**
- Scan cycle times (<100ms normal)
- Watchdog faults (0 expected)
- PLC states (all RUN)
- Communication errors

✅ **Security Events**
- IDS alerts (investigate all HIGH/CRITICAL)
- Unauthorized access attempts
- Protocol violations
- Unusual traffic patterns

✅ **Network Traffic**
- Packet rates (watch for spikes)
- Protocol distribution
- Source IP analysis
- Command sequences

### 4. Alert Triage Matrix

Prioritize alerts by severity and context:

| Alert Type | Severity | Response Time | Action |
|------------|----------|---------------|--------|
| Unauthorized write to protected address | CRITICAL | Immediate | Block source, investigate |
| Invalid function code | HIGH | <5 min | Verify legitimacy, block if attack |
| Rate limit exceeded | HIGH | <10 min | Check source, possible DoS |
| Sequential register scan | MEDIUM | <30 min | Investigate, possible recon |
| Unusual access time | LOW | <1 hour | Log for analysis |

---

## Incident Response

### Incident Response Playbook

#### Phase 1: Detection

1. **Alert Received**
   ```bash
   # Check alert details
   cat /tmp/vulnplc_state.json | jq '.modbus_ids_alerts | .[-1]'
   ```

2. **Verify Alert**
   - Is this a true positive?
   - What is the affected system?
   - Is the attack still active?

#### Phase 2: Containment

1. **Immediate Actions** (< 5 minutes)
   ```bash
   # Block attacking IP at firewall
   sudo iptables -I INPUT -s <ATTACKER_IP> -j DROP

   # Isolate affected PLC if necessary
   # (Coordinate with operations first!)
   ```

2. **Preserve Evidence**
   ```bash
   # Capture traffic
   sudo tcpdump -i any port 502 -w /tmp/incident_$(date +%s).pcap

   # Save IDS alerts
   cp /tmp/vulnplc_state.json /tmp/incident_state_$(date +%s).json

   # Save logs
   cp logs/*.log /tmp/incident_logs/
   ```

#### Phase 3: Eradication

1. **Identify Root Cause**
   - How did attacker gain access?
   - What vulnerability was exploited?
   - Are there backdoors/persistence?

2. **Remove Threat**
   ```bash
   # Kill malicious processes
   ps aux | grep <suspicious>
   kill -9 <PID>

   # Check for modified files
   find /home/taimaishu/vulnerable_plc -type f -mtime -1

   # Restore from backup if necessary
   ./restore_from_backup.sh
   ```

#### Phase 4: Recovery

1. **Restore Normal Operations**
   ```bash
   # Verify PLC states
   python3 system_monitor.py

   # Check all PLCs in RUN mode
   # Verify no watchdog faults
   # Confirm process values normal
   ```

2. **Increase Monitoring**
   - Watch for re-compromise attempts
   - Monitor same attacker IP
   - Look for lateral movement

#### Phase 5: Lessons Learned

1. **Document Incident**
   - Timeline of events
   - Attack vector and techniques
   - Response actions taken
   - Effectiveness of defenses

2. **Improve Defenses**
   - Patch vulnerabilities
   - Update IDS rules
   - Enhance monitoring
   - Conduct training

### Incident Response Checklist

```
□ Alert received and verified
□ Incident classified (severity, scope)
□ Incident commander assigned
□ Operations team notified
□ Attacker contained/blocked
□ Evidence preserved
□ Forensic analysis initiated
□ Root cause identified
□ Threat removed
□ Systems restored
□ Normal operations verified
□ Increased monitoring active
□ Incident documented
□ Post-incident review scheduled
□ Defenses improved
```

---

## Hardening Recommendations

### 1. Network Security

**Implement Strict Firewall Rules:**

```bash
# Example iptables rules

# Allow HMI → PLCs (Modbus)
iptables -A FORWARD -s 192.168.100.20 -d 192.168.100.0/24 -p tcp --dport 502 -j ACCEPT

# Allow Historian → PLCs (Modbus, read-only)
iptables -A FORWARD -s 192.168.50.10 -d 192.168.100.0/24 -p tcp --dport 502 -j ACCEPT

# Block all other access to PLCs
iptables -A FORWARD -d 192.168.100.0/24 -p tcp --dport 502 -j DROP

# Log dropped packets
iptables -A FORWARD -j LOG --log-prefix "ICS_FIREWALL_DROP: "
```

**Network Segmentation:**

```
┌────────────────┐
│   IT Network   │ 192.168.1.0/24
└───────┬────────┘
        │ DENY ALL
        │
┌───────▼────────┐
│      DMZ       │ 192.168.50.0/24
└───────┬────────┘
        │ Restricted
        │
┌───────▼────────┐
│   OT Network   │ 192.168.100.0/24
└────────────────┘
```

### 2. Access Control

**Strong Authentication:**

```python
# Disable default credentials
- Remove admin/admin
- Remove engineer/plc2pass
- Require complex passwords (min 12 chars)

# Implement multi-factor authentication
- Hardware tokens
- OTP codes
- Certificate-based auth

# Use role-based access control
- Read-only for operators
- Write access only for authorized engineers
- Control access only during change windows
```

**Session Management:**

```python
# Implement secure sessions
- Use strong secret keys (not 'dev-secret-key')
- Enable HTTP-only cookies
- Implement session timeouts (15 minutes)
- Require re-authentication for critical actions
```

### 3. Protocol Security

**Modbus Security:**

```bash
# Option 1: VPN tunnel
openvpn --config ics-tunnel.conf

# Option 2: TLS wrapper
stunnel4 /etc/stunnel/modbus-tls.conf

# Option 3: Application-layer authentication
# Implement custom auth before Modbus commands
```

**S7 Protocol Hardening:**

```python
# Add authentication layer
def authenticate_s7_client(client_ip):
    if client_ip not in AUTHORIZED_S7_CLIENTS:
        return False
    return verify_client_certificate(client_ip)

# Restrict PLC control commands
if command == S7Function.PLC_CONTROL:
    if not is_authorized_for_control(client_ip):
        return build_error_response("Unauthorized")
```

### 4. Application Security

**Fix Web Vulnerabilities:**

```python
# SQL Injection - Use parameterized queries
c.execute("SELECT * FROM users WHERE username=?", (username,))

# Command Injection - Use subprocess.run with list args
subprocess.run(['ls', '-la'], capture_output=True)

# XSS - Escape output
from markupsafe import escape
return f"<p>{escape(user_input)}</p>"

# Directory Traversal - Validate paths
def safe_path(user_path):
    base = os.path.abspath('/var/data')
    requested = os.path.abspath(os.path.join(base, user_path))
    if not requested.startswith(base):
        raise ValueError("Invalid path")
    return requested
```

### 5. Monitoring & Logging

**Comprehensive Logging:**

```python
# Log all access attempts
log.info(f"Login attempt: user={username} source={request.remote_addr} success={success}")

# Log all Modbus commands
log.info(f"Modbus: {source_ip} → {dest_ip} FC={func_code} addr={address} value={value}")

# Log all configuration changes
log.warning(f"Config change: user={user} action={action} details={details}")

# Log all PLC state changes
log.warning(f"PLC state: {plc_id} {old_state} → {new_state}")
```

**Log Retention:**

```bash
# Rotate logs
/etc/logrotate.d/vulnplc:
  /home/taimaishu/vulnerable_plc/logs/*.log {
    daily
    rotate 90
    compress
    missingok
    notifempty
  }
```

### 6. Change Management

**Implement Change Control:**

1. **Request**: Document proposed change
2. **Review**: Security and operations review
3. **Test**: Validate in test environment
4. **Approve**: Management sign-off
5. **Schedule**: Plan change window
6. **Execute**: Implement change
7. **Verify**: Confirm successful
8. **Document**: Update documentation

**Example Change Process:**

```
Change Request: Update PLC-2 ladder logic

1. Requested by: John Engineer
2. Reason: Optimize pump control sequence
3. Risk assessment: Medium (affects production)
4. Test results: Passed in lab environment
5. Rollback plan: Keep backup of current logic
6. Approval: Manager signed 2024-12-07
7. Window: Saturday 2024-12-14 02:00-04:00
8. Verification: Monitor for 24 hours post-change
```

---

## Training Exercises

### Exercise 1: Baseline & Anomaly Detection

**Objective**: Learn to distinguish normal from malicious traffic

**Setup:**
```bash
# Start all systems
./start_all.sh

# Start IDS and monitor
python3 modbus_ids.py &
python3 system_monitor.py --web &
```

**Tasks:**
1. Observe normal traffic patterns for 10 minutes
2. Document baseline metrics
3. Generate test attacks:
   ```bash
   # Unauthorized write
   sudo modbus 127.0.0.1:5502 write 10 9999

   # Flooding
   for i in {1..100}; do sudo modbus 127.0.0.1:5502 read $i 1; done

   # Sequential scan
   for i in {0..50}; do sudo modbus 127.0.0.1:5502 read $i 1; sleep 0.1; done
   ```
4. Observe IDS alerts
5. Distinguish true attacks from false positives

**Questions:**
- What is normal HMI polling rate?
- Which function codes are most common?
- How did IDS detect each attack?
- Were there any false positives?

### Exercise 2: Incident Response Drill

**Objective**: Practice incident response procedures

**Scenario:**
"At 14:35, the IDS detected unauthorized write commands to PLC-2 from IP 192.168.1.100. The PLC pressure relief valve was disabled."

**Tasks:**
1. **Detect**: Review IDS alert details
2. **Contain**: Block attacker IP
3. **Investigate**:
   - What was written?
   - Which addresses affected?
   - How many commands sent?
4. **Eradicate**: Verify no backdoors
5. **Recover**: Restore safe configuration
6. **Document**: Write incident report

**Time limit:** 30 minutes

### Exercise 3: Security Hardening

**Objective**: Implement defense improvements

**Current State:**
- Default credentials enabled
- No firewall rules
- All IPs can write to PLCs
- No audit logging

**Tasks:**
1. Change all default passwords
2. Configure firewall rules (only HMI → PLC)
3. Configure IDS whitelist
4. Enable comprehensive logging
5. Test that legitimate access still works
6. Verify unauthorized access is blocked

**Validation:**
```bash
# Should succeed (HMI)
curl -X POST http://localhost:5000/login -d "username=newadmin&password=ComplexPass123!"

# Should fail (blocked IP)
curl -X POST http://localhost:5000/login -d "username=admin&password=anything" --interface eth1

# Should alert (unauthorized write)
sudo modbus 127.0.0.1:5502 write 10 9999
# Check IDS alerts
```

### Exercise 4: Red vs Blue Team

**Objective**: Full adversary simulation

**Red Team Mission:**
- Gain access to PLC network
- Identify critical processes
- Disrupt operations (stop pumps, modify setpoints)
- Avoid detection

**Blue Team Mission:**
- Monitor all traffic
- Detect reconnaissance
- Block attacks
- Restore normal operations
- Document tactics

**Rules:**
- 2-hour exercise
- Red team starts from external network (192.168.1.0/24)
- Blue team monitors from SOC
- Scoring:
  - Red: +10 per successful attack, -5 per detection
  - Blue: +10 per detected attack, -5 per missed attack

**Debrief:**
- What worked well?
- What attacks were missed?
- How can defenses be improved?
- Lessons learned

---

## Continuous Improvement

### Security Metrics

Track these KPIs:

| Metric | Target | Current |
|--------|--------|---------|
| Mean time to detect (MTTD) | < 5 minutes | ? |
| Mean time to respond (MTTR) | < 15 minutes | ? |
| False positive rate | < 5% | ? |
| Security events per day | Baseline ± 20% | ? |
| Patching compliance | 100% critical patches within 30 days | ? |

### Regular Activities

**Daily:**
- Review IDS alerts
- Check system health dashboard
- Verify backup completion

**Weekly:**
- Analyze traffic trends
- Review access logs
- Test incident response procedures

**Monthly:**
- Security assessment
- Update threat intelligence
- Conduct training exercises

**Quarterly:**
- Full security audit
- Penetration testing
- Update security documentation

---

## PCAP Analysis Exercises

### Exercise 5: Packet Capture and Analysis

**Objective**: Learn to capture, analyze, and reconstruct attacks from packet data

#### Part 1: Capture Attack Traffic

```bash
# Start environment with IDS (captures PCAP automatically)
docker-compose --profile full up -d

# Or manually start PCAP capture
python3 -c "
from modbus_ids import ModbusIDS
ids = ModbusIDS(pcap_dir='./forensics_pcaps')
ids.start()
"

# Perform test attacks
# 1. Unauthorized write
sudo modbus 127.0.0.1:5502 write 10 9999

# 2. Sequential scan
for i in {0..50}; do sudo modbus 127.0.0.1:5502 read $i 1; sleep 0.1; done

# 3. Flooding
for i in {1..100}; do sudo modbus 127.0.0.1:5502 read 0 1; done

# Stop capture after 60 seconds
sleep 60
```

#### Part 2: Extract PCAP Files

```bash
# Copy from Docker container
docker cp vuln-modbus-ids:/app/pcaps/ ./investigation/

# Or check local directory
ls -lh pcaps/*.pcap
```

#### Part 3: Basic Analysis

```bash
# Count total Modbus packets
tcpdump -r pcaps/modbus_*.pcap 'tcp port 502' | wc -l

# Show unique source IPs
tcpdump -r pcaps/modbus_*.pcap -nn 'tcp port 502' | \
  awk '{print $3}' | cut -d. -f1-4 | sort -u

# Extract Modbus function codes
tshark -r pcaps/modbus_*.pcap -Y modbus -T fields -e modbus.func_code | \
  sort | uniq -c | sort -rn
```

#### Part 4: Detect Attack Patterns

**Unauthorized Write Detection:**
```bash
# Find all Write Single Register commands (FC06)
tshark -r pcaps/modbus_*.pcap -Y "modbus.func_code == 6" \
  -T fields -e frame.time -e ip.src -e modbus.regnum16 -e modbus.regval_uint16
```

**Sequential Scanning:**
```bash
# Show sequential address access
tshark -r pcaps/modbus_*.pcap -Y "modbus.func_code == 3" \
  -T fields -e frame.number -e modbus.regnum16 | \
  awk '{if (prev) print prev, $2-prev_addr; prev=$1; prev_addr=$2}'
```

**Flooding Detection:**
```bash
# Count requests per second
tshark -r pcaps/modbus_*.pcap -T fields -e frame.time_epoch -e ip.src | \
  awk '{count[int($1)" "$2]++} END {for (key in count) print key, count[key]}' | \
  sort -k1 -n
```

#### Part 5: Wireshark Deep Dive

```bash
wireshark pcaps/modbus_*.pcap
```

**Wireshark Filters to Use:**

```
# Show only Modbus traffic
modbus

# Write operations only
modbus.func_code == 6 || modbus.func_code == 16

# Specific register access
modbus.regnum16 == 10

# Large writes (potential attack)
modbus.word_cnt > 10

# Exception responses (errors)
modbus.func_code > 128

# Conversation between specific IPs
ip.addr == 192.168.100.10 && ip.addr == 192.168.1.100
```

#### Part 6: Timeline Reconstruction

Create attack timeline from PCAP:

```bash
# Extract all Modbus operations with timestamps
tshark -r pcaps/modbus_*.pcap -Y modbus -T fields \
  -e frame.time \
  -e ip.src \
  -e ip.dst \
  -e modbus.func_code \
  -e modbus.regnum16 \
  -e modbus.regval_uint16 > timeline.csv

# Analyze in spreadsheet or Python
python3 << 'EOF'
import csv
with open('timeline.csv') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        time, src, dst, fc, addr, val = row
        fc_name = {
            '3': 'READ', '4': 'READ',
            '6': 'WRITE', '16': 'WRITE_MULTI'
        }.get(fc, fc)
        print(f"[{time}] {src} → {dst}: {fc_name} addr={addr} val={val}")
EOF
```

#### Part 7: Incident Report

**Template:**
```markdown
# Incident Report: [Attack Type]

## Executive Summary
- Date/Time: [timestamp]
- Affected Systems: [PLCs, networks]
- Attack Type: [unauthorized write, DoS, etc.]
- Impact: [consequences]

## Timeline
1. [HH:MM:SS] - Initial reconnaissance detected
2. [HH:MM:SS] - Unauthorized access attempt
3. [HH:MM:SS] - Malicious commands executed
4. [HH:MM:SS] - IDS alert triggered
5. [HH:MM:SS] - Response initiated

## Technical Analysis
- Source IP: [attacker IP]
- Target: [PLC-X, register Y]
- Function Codes Used: [FC06, FC16]
- Commands Executed: [details]

## Evidence
- PCAP file: modbus_20241207_143022.pcap
- IDS alerts: [count] total, [count] critical
- Screenshots: [attached]

## Impact Assessment
- Process disruption: [Yes/No]
- Safety incidents: [overflow, pressure, etc.]
- Data integrity: [compromised/intact]

## Remediation
- Actions taken: [blocked IP, restored values]
- Time to contain: [X minutes]
- Time to recover: [Y minutes]

## Recommendations
1. Implement firewall rules
2. Add IDS signatures
3. Enable authentication
4. Increase monitoring
```

---

## Resources

### Tools

- **Wireshark**: Protocol analysis and PCAP inspection
- **tshark**: Command-line packet analysis
- **tcpdump**: Packet capture and basic analysis
- **Nmap**: Network scanning
- **Metasploit**: Penetration testing
- **Zeek (Bro)**: Network security monitoring
- **Suricata**: IDS/IPS
- **OpenVAS**: Vulnerability scanning

### References

- **NIST Cybersecurity Framework**: Framework for improving critical infrastructure cybersecurity
- **IEC 62443**: Industrial cybersecurity standards
- **SANS ICS**: ICS security training and resources
- **ICS-CERT**: Advisories and threat intelligence
- **MITRE ATT&CK for ICS**: ICS-specific tactics and techniques

---

**Remember**: Defense is not a one-time activity. It requires continuous monitoring, regular testing, and constant improvement.

Stay vigilant! 🛡️🏭
