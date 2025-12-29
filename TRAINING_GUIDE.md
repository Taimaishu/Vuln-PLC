# ICS/SCADA Attack Training Guide

## Overview

This guide provides realistic attack scenarios for training security professionals in industrial control system (ICS) and SCADA security. All scenarios are designed for educational purposes only and should only be executed in controlled lab environments.

## Training Scenarios

### Scenario 1: Reconnaissance - System Discovery
**Difficulty:** Beginner
**Target:** All PLCs
**MITRE ATT&CK:** T0840 - Network Connection Enumeration

**Learning Objectives:**
- Understand ICS network discovery techniques
- Learn Modbus port scanning methodology
- Practice PLC fingerprinting

**Skills Developed:**
- Network enumeration
- Service identification
- Target profiling

---

### Scenario 2: Tank Overflow Attack (PLC-1)
**Difficulty:** Intermediate
**Target:** PLC-1 (Tank Control System)
**MITRE ATT&CK:** T0836 - Modify Parameter

**Real-World Parallel:** Water treatment facility attacks

**Attack Methodology:**
1. Turn ON pump (coil 0) to fill tank
2. Close outlet valve (coil 3) to prevent drainage
3. Result: Uncontrolled tank level rise

**Expected Impact:**
- Tank overflow
- High-level alarms triggered
- Physical damage to tank
- Production downtime

**Blue Team Detection:**
- Write operations to critical coils
- Abnormal process values
- Safety system alarms

---

### Scenario 3: Pressure Vessel Rupture (PLC-2)
**Difficulty:** Advanced
**Target:** PLC-2 (Pressure Control System)
**MITRE ATT&CK:** T0816 - Device Restart/Shutdown

**Real-World Parallel:** Triton/TRISIS safety system attacks

**Attack Methodology:**
1. Enable compressor (coil 0) to increase pressure
2. Close relief valve (coil 4) to disable safety relief
3. Result: Pressure exceeds safe operating limits

**Expected Impact:**
- CRITICAL: Pressure exceeds safe limits
- Risk of vessel rupture/explosion
- Safety systems bypassed
- Potential for casualties

**Blue Team Detection:**
- CRITICAL alerts for safety tampering
- Relief valve closure during high pressure
- Emergency shutdown procedures triggered

---

### Scenario 4: Thermal Stress Attack (PLC-3)
**Difficulty:** Intermediate
**Target:** PLC-3 (Temperature Control System)
**MITRE ATT&CK:** T0879 - Damage to Property

**Real-World Parallel:** Stuxnet equipment degradation methodology

**Attack Methodology:**
1. Rapid heating/cooling cycles
2. Thermal stress on equipment
3. Result: Accelerated equipment degradation

**Expected Impact:**
- Thermal shock to equipment
- Accelerated wear and tear
- Reduced equipment lifespan
- Increased maintenance costs

**Blue Team Detection:**
- Abnormal temperature fluctuations
- Rapid setpoint changes
- Process deviation alarms

---

### Scenario 5: Safety System Shutdown (PLC-4)
**Difficulty:** Expert
**Target:** PLC-4 (Safety/Emergency Shutdown System)
**MITRE ATT&CK:** T0816 - Device Restart/Shutdown

**Real-World Parallel:** Triton/TRISIS attack methodology

⚠️ **WARNING:** This is the most dangerous attack scenario!

**Attack Methodology:**
1. Disable emergency stop (coil 0)
2. Disable safety interlock (coil 1)
3. Result: No safety systems to prevent catastrophe

**Expected Impact:**
- CRITICAL: No emergency stop capability
- CRITICAL: Safety interlocks bypassed
- Plant cannot be safely shut down
- Other attacks become more dangerous

**Blue Team Detection:**
- MAXIMUM PRIORITY ALERT
- Safety system tampering detected
- Immediate incident response required
- Consider emergency plant shutdown

---

### Scenario 6: Multi-Stage APT Campaign
**Difficulty:** Expert
**Target:** All PLCs (System-Wide)
**MITRE ATT&CK:** Multiple Techniques

**Real-World Parallel:** Nation-state APT campaigns

**Attack Timeline:**
- **Phase 1:** Disable safety systems (PLC-4)
- **Phase 2:** Overflow tank (PLC-1)
- **Phase 3:** Over-pressurize (PLC-2)
- **Phase 4:** Thermal damage (PLC-3)
- **Result:** Cascading system failure

**Expected Impact:**
- Complete loss of safety systems
- Multiple simultaneous process failures
- Cascading equipment damage
- Potential for catastrophic incident
- Extended recovery time (days/weeks)

**Blue Team Response:**
- Declare security incident
- Emergency plant shutdown
- Isolate OT network from IT
- Begin forensic investigation
- Notify authorities/regulatory bodies

---

### Scenario 7: Stealthy Reconnaissance
**Difficulty:** Intermediate
**Target:** All PLCs
**MITRE ATT&CK:** T0888 - Remote System Information Discovery

**Learning Objectives:**
- Understand detection evasion techniques
- Learn how attackers avoid triggering alarms
- Practice covert intelligence gathering

**Stealth Techniques:**
- Slow scanning (avoid rate-based detection)
- Read-only operations (no process changes)
- Randomized timing (avoid pattern detection)
- Legitimate-looking requests

**Blue Team Detection:**
- LOW - Stealthy approach reduces detection
- Slow scan may blend with normal traffic
- Long-term behavioral analysis needed

---

## Using the Training Scenarios

### Quick Start

Run the interactive training menu:

```bash
./training_scenarios.py
```

or

```bash
python3 training_scenarios.py
```

### Prerequisites

1. Vuln-PLC environment running (all 4 PLCs active)
2. Python 3.x installed
3. Network access to PLCs:
   - PLC-1: localhost:5502
   - PLC-2: localhost:5503
   - PLC-3: localhost:5504
   - PLC-4: localhost:5505

### Training Recommendations

**For Beginners:**
1. Start with Scenario 1 (Reconnaissance)
2. Progress to Scenario 2 (Tank Overflow)
3. Try Scenario 7 (Stealthy Reconnaissance)

**For Intermediate Users:**
1. Scenarios 2, 4, 7
2. Focus on understanding blue team detection indicators
3. Practice both attack and defense perspectives

**For Advanced Users:**
1. Scenarios 3, 5, 6
2. Understand APT methodologies
3. Learn incident response procedures

**For Expert Red Teams:**
1. Scenario 6 (Multi-Stage APT)
2. Develop custom attack chains
3. Practice covert persistence

---

## MITRE ATT&CK for ICS Mapping

This training covers the following MITRE ATT&CK for ICS techniques:

- **T0816** - Device Restart/Shutdown
- **T0836** - Modify Parameter
- **T0840** - Network Connection Enumeration
- **T0879** - Damage to Property
- **T0888** - Remote System Information Discovery

Reference: https://attack.mitre.org/matrices/ics/

---

## Safety and Ethics

### Training Environment Only

⚠️ **CRITICAL:** These scenarios must ONLY be executed in:
- Isolated lab environments
- Virtual/containerized systems
- Educational settings with proper authorization

### Never Execute Against:
- Production ICS/SCADA systems
- Real industrial facilities
- Systems you don't own or have explicit permission to test
- Any system where failure could cause harm

### Legal Considerations

Unauthorized access to ICS/SCADA systems is illegal and can result in:
- Criminal prosecution
- Significant fines
- Imprisonment
- Civil liability

### Ethical Use

This training is designed to:
- Educate security professionals
- Improve industrial cybersecurity
- Demonstrate attack techniques for defensive purposes
- Prepare incident responders

---

## Blue Team Training

Each scenario includes blue team detection indicators. Use these to:

1. **Configure Detection Rules:**
   - Set up IDS/IPS signatures
   - Configure SIEM alerts
   - Implement behavioral analytics

2. **Incident Response Practice:**
   - Recognize attack patterns
   - Execute response playbooks
   - Coordinate with OT teams

3. **Security Hardening:**
   - Implement network segmentation
   - Deploy monitoring tools
   - Strengthen access controls

---

## Additional Resources

### Documentation
- [README.md](README.md) - Project overview
- [MODBUS_IMPLEMENTATION.md](MODBUS_IMPLEMENTATION.md) - Modbus technical details
- [FILTERING_VERIFICATION_REPORT.md](FILTERING_VERIFICATION_REPORT.md) - Alert filtering tests

### Test Scripts
- `test_50_attacks.py` - Comprehensive testing
- `test_all_plcs.py` - Multi-PLC testing
- `test_visual_alerts.py` - Alert system testing

### Attack Demos
- `attack.py` - Basic attack demonstrations
- `demo_attack.py` - Guided attack demos
- `quick_test.py` - Quick functionality tests

---

## Contributing

To add new training scenarios:

1. Follow the existing scenario format
2. Include MITRE ATT&CK mappings
3. Provide clear learning objectives
4. Document expected impacts
5. Include blue team detection indicators

---

## License

See [LICENSE](LICENSE) file for details.

---

## Disclaimer

This software is provided for educational and research purposes only. The authors and contributors are not responsible for any misuse or damage caused by this program. Use at your own risk in authorized environments only.

---

**Generated:** 2025-12-28
**Version:** 1.0
**Project:** Vuln-PLC ICS/SCADA Training Environment
