# ICS/SCADA Security Training - Student Workbook

## Student Information

**Name:** ________________________________
**Date:** ________________________________
**Instructor:** ________________________________
**Lab Environment:** ________________________________

---

## Lab Safety and Ethics Agreement

Before beginning these exercises, I acknowledge that:

- [ ] I will only use these techniques in authorized lab environments
- [ ] I understand that unauthorized access to ICS/SCADA systems is illegal
- [ ] I will not use these skills maliciously or against production systems
- [ ] I will follow responsible disclosure practices if I discover real vulnerabilities
- [ ] I understand the potential consequences of ICS/SCADA attacks

**Student Signature:** ________________________________ **Date:** ____________

---

## Pre-Lab Assessment

Before starting the hands-on exercises, answer these questions:

### 1. What is Modbus TCP and why is it commonly used in industrial environments?

**Your Answer:**

&nbsp;

&nbsp;

&nbsp;

### 2. What is the difference between IT (Information Technology) and OT (Operational Technology) security?

**Your Answer:**

&nbsp;

&nbsp;

&nbsp;

### 3. Name three real-world ICS/SCADA attacks and their impacts:

**Your Answer:**

1. ________________________________________________________________

2. ________________________________________________________________

3. ________________________________________________________________

### 4. What is the MITRE ATT&CK for ICS framework?

**Your Answer:**

&nbsp;

&nbsp;

&nbsp;

---

# Lab Exercise 1: Reconnaissance - System Discovery

**Difficulty:** Beginner
**Estimated Time:** 20 minutes
**MITRE ATT&CK:** T0840 - Network Connection Enumeration

## Learning Objectives

By the end of this lab, you will be able to:
- [ ] Identify active Modbus TCP devices on a network
- [ ] Understand port scanning techniques for ICS systems
- [ ] Recognize detection indicators for reconnaissance activity

## Pre-Exercise Questions

### 1. What TCP port does Modbus typically use?

**Your Answer:** ________________________________________________

### 2. How might reconnaissance activity be detected by a blue team?

**Your Answer:**

&nbsp;

&nbsp;

## Lab Instructions

### Step 1: Launch the Training Scenario

Run the training scenarios script:
```bash
./training_scenarios.py
```

Select option **[1] Reconnaissance - System Discovery**

### Step 2: Observe the Scan

**Document your observations:**

| PLC Name | Port | Status (Active/Inactive) | Response Time |
|----------|------|--------------------------|---------------|
| PLC-1    |      |                          |               |
| PLC-2    |      |                          |               |
| PLC-3    |      |                          |               |
| PLC-4    |      |                          |               |

### Step 3: Detection Analysis

**How many PLCs were discovered?** ___________

**What information did you gather about each PLC?**

&nbsp;

&nbsp;

**What blue team detection indicators were mentioned?**

1. ________________________________________________________________

2. ________________________________________________________________

3. ________________________________________________________________

## Post-Exercise Questions

### 1. Why is reconnaissance often the first phase of an ICS attack?

**Your Answer:**

&nbsp;

&nbsp;

### 2. What could a defender do to make reconnaissance more difficult?

**Your Answer:**

&nbsp;

&nbsp;

### 3. Is this reconnaissance activity noisy or stealthy? Explain.

**Your Answer:**

&nbsp;

&nbsp;

## Instructor Sign-Off

**Completed:** [ ] Yes [ ] No
**Instructor Signature:** ________________________________

---

# Lab Exercise 2: Tank Overflow Attack (PLC-1)

**Difficulty:** Intermediate
**Estimated Time:** 30 minutes
**MITRE ATT&CK:** T0836 - Modify Parameter

## Learning Objectives

By the end of this lab, you will be able to:
- [ ] Understand process control manipulation techniques
- [ ] Execute a write coil attack against a PLC
- [ ] Predict physical impacts of process attacks

## Pre-Exercise Questions

### 1. What is a Modbus coil and what does it control?

**Your Answer:**

&nbsp;

&nbsp;

### 2. In a tank control system, what could cause an overflow?

**Your Answer:**

&nbsp;

&nbsp;

### 3. What real-world facility might use a tank control system like PLC-1?

**Your Answer:**

&nbsp;

&nbsp;

## Lab Instructions

### Step 1: Review the Attack Scenario

Read the attack methodology:
1. Turn ON pump (coil 0) → Fill tank
2. Close outlet valve (coil 3) → Prevent drainage
3. Result: Tank level rises uncontrollably

**Predict the outcome before executing:**

&nbsp;

&nbsp;

### Step 2: Execute the Attack

Run the training scenarios script and select **[2] Tank Overflow Attack (PLC-1)**

**Document each step:**

| Step | Action | Coil # | Value | Success? | Observation |
|------|--------|--------|-------|----------|-------------|
| 1    |        |        |       |          |             |
| 2    |        |        |       |          |             |

### Step 3: Analyze the Impact

**Expected Impact (from scenario):**

- [ ] Tank level rises uncontrollably
- [ ] High-level alarms triggered
- [ ] Potential physical damage to tank
- [ ] Production downtime

**What blue team indicators were shown?**

1. ________________________________________________________________

2. ________________________________________________________________

3. ________________________________________________________________

## Post-Exercise Questions

### 1. How does this attack compare to real-world water treatment facility attacks?

**Your Answer:**

&nbsp;

&nbsp;

### 2. What safety mechanisms should be in place to prevent this attack?

**Your Answer:**

&nbsp;

&nbsp;

### 3. As a defender, how would you detect this attack in progress?

**Your Answer:**

&nbsp;

&nbsp;

### 4. What Modbus function codes were used in this attack?

**Your Answer:**

&nbsp;

&nbsp;

## Instructor Sign-Off

**Completed:** [ ] Yes [ ] No
**Instructor Signature:** ________________________________

---

# Lab Exercise 3: Pressure Vessel Rupture (PLC-2)

**Difficulty:** Advanced
**Estimated Time:** 30 minutes
**MITRE ATT&CK:** T0816 - Device Restart/Shutdown

## Learning Objectives

By the end of this lab, you will be able to:
- [ ] Understand safety system bypass techniques
- [ ] Recognize the severity of pressure-related attacks
- [ ] Analyze similarities to real-world attacks like Triton/TRISIS

## Pre-Exercise Questions

### 1. What is Triton/TRISIS and what systems did it target?

**Your Answer:**

&nbsp;

&nbsp;

### 2. Why are pressure relief valves critical safety devices?

**Your Answer:**

&nbsp;

&nbsp;

### 3. What physical consequences could result from over-pressurization?

**Your Answer:**

&nbsp;

&nbsp;

## Lab Instructions

### Step 1: Review Safety Implications

This scenario demonstrates a **CRITICAL** safety system attack.

**Before executing, explain why this is more dangerous than the tank overflow:**

&nbsp;

&nbsp;

### Step 2: Execute the Attack

Run the training scenarios script and select **[3] Pressure Vessel Rupture (PLC-2)**

**Document the attack steps:**

| Step | Device | Coil # | Action | Expected Result |
|------|--------|--------|--------|-----------------|
| 1    |        |        |        |                 |
| 2    |        |        |        |                 |

### Step 3: Impact Analysis

**Expected Impact:**

- [ ] Pressure exceeds safe limits
- [ ] Risk of vessel rupture/explosion
- [ ] Safety systems bypassed
- [ ] Potential for casualties

**Blue Team Detection Indicators:**

1. ________________________________________________________________

2. ________________________________________________________________

3. ________________________________________________________________

## Post-Exercise Questions

### 1. How does this attack methodology compare to Triton/TRISIS?

**Your Answer:**

&nbsp;

&nbsp;

### 2. What immediate actions should a blue team take if this is detected?

**Your Answer:**

&nbsp;

&nbsp;

### 3. Why are safety system attacks classified as the highest severity?

**Your Answer:**

&nbsp;

&nbsp;

### 4. What layers of defense should protect against this type of attack?

**Your Answer:**

&nbsp;

&nbsp;

## Instructor Sign-Off

**Completed:** [ ] Yes [ ] No
**Instructor Signature:** ________________________________

---

# Lab Exercise 4: Thermal Stress Attack (PLC-3)

**Difficulty:** Intermediate
**Estimated Time:** 30 minutes
**MITRE ATT&CK:** T0879 - Damage to Property

## Learning Objectives

By the end of this lab, you will be able to:
- [ ] Understand equipment degradation techniques
- [ ] Recognize Stuxnet-style attack patterns
- [ ] Analyze long-term vs. immediate attack impacts

## Pre-Exercise Questions

### 1. How did Stuxnet cause physical damage to centrifuges?

**Your Answer:**

&nbsp;

&nbsp;

### 2. What is thermal stress and how does it damage equipment?

**Your Answer:**

&nbsp;

&nbsp;

### 3. Why might an attacker prefer gradual degradation over immediate destruction?

**Your Answer:**

&nbsp;

&nbsp;

## Lab Instructions

### Step 1: Understand the Attack Pattern

This attack uses rapid heating and cooling cycles to stress equipment.

**Predict the mechanism of damage:**

&nbsp;

&nbsp;

### Step 2: Execute the Attack

Run the training scenarios script and select **[4] Thermal Stress Attack (PLC-3)**

**Document the thermal cycles:**

| Cycle | Heater (Coil 0) | Cooler (Coil 2) | Duration | Observation |
|-------|-----------------|-----------------|----------|-------------|
| 1     |                 |                 |          |             |
| 2     |                 |                 |          |             |
| 3     |                 |                 |          |             |

### Step 3: Analyze the Pattern

**Expected Impact:**

- [ ] Thermal shock to equipment
- [ ] Accelerated wear and tear
- [ ] Reduced equipment lifespan
- [ ] Maintenance costs increase

**Blue Team Detection Indicators:**

1. ________________________________________________________________

2. ________________________________________________________________

3. ________________________________________________________________

## Post-Exercise Questions

### 1. How is this attack more covert than the previous scenarios?

**Your Answer:**

&nbsp;

&nbsp;

### 2. What process monitoring would detect abnormal thermal cycling?

**Your Answer:**

&nbsp;

&nbsp;

### 3. Compare this to Stuxnet's approach - what are the similarities?

**Your Answer:**

&nbsp;

&nbsp;

### 4. What is the advantage of this attack from an attacker's perspective?

**Your Answer:**

&nbsp;

&nbsp;

## Instructor Sign-Off

**Completed:** [ ] Yes [ ] No
**Instructor Signature:** ________________________________

---

# Lab Exercise 5: Safety System Shutdown (PLC-4)

**Difficulty:** Expert
**Estimated Time:** 30 minutes
**MITRE ATT&CK:** T0816 - Device Restart/Shutdown

## Learning Objectives

By the end of this lab, you will be able to:
- [ ] Understand emergency shutdown system attacks
- [ ] Recognize maximum priority security incidents
- [ ] Analyze coordinated attack campaigns

## Pre-Exercise Questions

### 1. What is an Emergency Stop (E-Stop) system?

**Your Answer:**

&nbsp;

&nbsp;

### 2. Why would an attacker disable safety systems before other attacks?

**Your Answer:**

&nbsp;

&nbsp;

### 3. What incident response procedures should follow safety system tampering?

**Your Answer:**

&nbsp;

&nbsp;

## Lab Instructions

### Step 1: Review the Severity

This scenario requires typing **'CONFIRM'** to execute.

**Explain why this confirmation is required:**

&nbsp;

&nbsp;

### Step 2: Execute the Attack

Run the training scenarios script and select **[5] Safety System Shutdown (PLC-4)**

**Document the safety system disable:**

| System Component | Coil # | Action | Result | Severity |
|------------------|--------|--------|--------|----------|
| Emergency Stop   |        |        |        |          |
| Safety Interlock |        |        |        |          |

### Step 3: Incident Response Planning

**Expected Impact:**

- [ ] No emergency stop capability
- [ ] Safety interlocks bypassed
- [ ] Plant cannot be safely shut down
- [ ] Other attacks now more dangerous

**Blue Team Response Actions:**

1. ________________________________________________________________

2. ________________________________________________________________

3. ________________________________________________________________

4. ________________________________________________________________

## Post-Exercise Questions

### 1. Why is this considered the most dangerous attack scenario?

**Your Answer:**

&nbsp;

&nbsp;

### 2. What should the blue team priority level be for this alert?

**Your Answer:**

&nbsp;

&nbsp;

### 3. What regulatory notifications might be required after this incident?

**Your Answer:**

&nbsp;

&nbsp;

### 4. How does disabling PLC-4 enable more dangerous attacks on other PLCs?

**Your Answer:**

&nbsp;

&nbsp;

## Instructor Sign-Off

**Completed:** [ ] Yes [ ] No
**Instructor Signature:** ________________________________

---

# Lab Exercise 6: Multi-Stage APT Campaign

**Difficulty:** Expert
**Estimated Time:** 45 minutes
**MITRE ATT&CK:** Multiple Techniques

## Learning Objectives

By the end of this lab, you will be able to:
- [ ] Understand coordinated multi-stage attacks
- [ ] Recognize APT methodologies
- [ ] Analyze cascading system failures

## Pre-Exercise Questions

### 1. What is an Advanced Persistent Threat (APT)?

**Your Answer:**

&nbsp;

&nbsp;

### 2. Why do APTs use multi-stage attacks instead of single attacks?

**Your Answer:**

&nbsp;

&nbsp;

### 3. Name a real-world nation-state ICS attack campaign:

**Your Answer:**

&nbsp;

&nbsp;

## Lab Instructions

### Step 1: Review the Attack Timeline

Document the planned attack phases:

| Phase | Target | Objective | Expected Impact |
|-------|--------|-----------|-----------------|
| 1     |        |           |                 |
| 2     |        |           |                 |
| 3     |        |           |                 |
| 4     |        |           |                 |

### Step 2: Execute the APT Campaign

Run the training scenarios script and select **[6] Multi-Stage APT Campaign**

Type **'EXECUTE APT'** to confirm.

**Document each phase execution:**

**Phase 1 (PLC-4):**
- Actions taken: ________________________________________________________
- Result: _______________________________________________________________

**Phase 2 (PLC-1):**
- Actions taken: ________________________________________________________
- Result: _______________________________________________________________

**Phase 3 (PLC-2):**
- Actions taken: ________________________________________________________
- Result: _______________________________________________________________

**Phase 4 (PLC-3):**
- Actions taken: ________________________________________________________
- Result: _______________________________________________________________

### Step 3: Analyze the Cascading Failure

**Expected Impact:**

- [ ] Complete loss of safety systems
- [ ] Multiple simultaneous process failures
- [ ] Cascading equipment damage
- [ ] Potential for catastrophic incident
- [ ] Extended recovery time (days/weeks)

**Blue Team Response Requirements:**

1. ________________________________________________________________

2. ________________________________________________________________

3. ________________________________________________________________

4. ________________________________________________________________

5. ________________________________________________________________

## Post-Exercise Questions

### 1. Why was PLC-4 targeted first in the attack sequence?

**Your Answer:**

&nbsp;

&nbsp;

### 2. How does this attack demonstrate the concept of cascading failures?

**Your Answer:**

&nbsp;

&nbsp;

### 3. What is the estimated recovery time from this type of attack? Why?

**Your Answer:**

&nbsp;

&nbsp;

### 4. What defense-in-depth strategies could prevent or mitigate this APT?

**Your Answer:**

&nbsp;

&nbsp;

### 5. Map each phase to a MITRE ATT&CK for ICS technique:

- Phase 1: ___________________________________________________________
- Phase 2: ___________________________________________________________
- Phase 3: ___________________________________________________________
- Phase 4: ___________________________________________________________

## Instructor Sign-Off

**Completed:** [ ] Yes [ ] No
**Instructor Signature:** ________________________________

---

# Lab Exercise 7: Stealthy Reconnaissance

**Difficulty:** Intermediate
**Estimated Time:** 25 minutes
**MITRE ATT&CK:** T0888 - Remote System Information Discovery

## Learning Objectives

By the end of this lab, you will be able to:
- [ ] Understand evasion techniques for reconnaissance
- [ ] Recognize the difference between noisy and stealthy scans
- [ ] Analyze behavioral detection methods

## Pre-Exercise Questions

### 1. What is the difference between active and passive reconnaissance?

**Your Answer:**

&nbsp;

&nbsp;

### 2. How can reconnaissance activity avoid rate-based detection?

**Your Answer:**

&nbsp;

&nbsp;

### 3. What is "living off the land" in the context of ICS attacks?

**Your Answer:**

&nbsp;

&nbsp;

## Lab Instructions

### Step 1: Compare to Lab Exercise 1

**How does stealthy reconnaissance differ from normal reconnaissance?**

&nbsp;

&nbsp;

### Step 2: Execute the Stealthy Scan

Run the training scenarios script and select **[7] Stealthy Reconnaissance**

**Document the timing behavior:**

| PLC Name | Probe Time | Wait Duration | Active? | Notes |
|----------|------------|---------------|---------|-------|
| PLC-1    |            |               |         |       |
| PLC-2    |            |               |         |       |
| PLC-3    |            |               |         |       |
| PLC-4    |            |               |         |       |

### Step 3: Analyze the Stealth Techniques

**Stealth techniques observed:**

- [ ] Slow scanning (avoid rate-based detection)
- [ ] Read-only operations (no process changes)
- [ ] Randomized timing (avoid pattern detection)
- [ ] Legitimate-looking requests

**Detection difficulty level:** ___________

**Why is detection more difficult?**

&nbsp;

&nbsp;

## Post-Exercise Questions

### 1. Compare Lab 1 and Lab 7 reconnaissance approaches - which is stealthier?

**Your Answer:**

&nbsp;

&nbsp;

### 2. What blue team capabilities are needed to detect stealthy reconnaissance?

**Your Answer:**

&nbsp;

&nbsp;

### 3. What is the trade-off for attackers using stealthy techniques?

**Your Answer:**

&nbsp;

&nbsp;

### 4. How could behavioral analysis detect this activity over time?

**Your Answer:**

&nbsp;

&nbsp;

## Instructor Sign-Off

**Completed:** [ ] Yes [ ] No
**Instructor Signature:** ________________________________

---

# Post-Lab Assessment

After completing all lab exercises, answer the following comprehensive questions:

## 1. MITRE ATT&CK Mapping

Map the techniques you practiced to the MITRE ATT&CK for ICS framework:

| Lab Exercise | MITRE Technique ID | Technique Name |
|--------------|-------------------|----------------|
| Lab 1        |                   |                |
| Lab 2        |                   |                |
| Lab 3        |                   |                |
| Lab 4        |                   |                |
| Lab 5        |                   |                |
| Lab 6        |                   |                |
| Lab 7        |                   |                |

## 2. Attack Severity Ranking

Rank the scenarios from least to most dangerous (1 = least, 7 = most):

| Rank | Scenario | Justification |
|------|----------|---------------|
|      |          |               |
|      |          |               |
|      |          |               |
|      |          |               |
|      |          |               |
|      |          |               |
|      |          |               |

## 3. Defense-in-Depth Strategy

For each layer of defense, list specific controls to protect against these attacks:

**Network Security:**

&nbsp;

&nbsp;

**Application Security:**

&nbsp;

&nbsp;

**Endpoint Security:**

&nbsp;

&nbsp;

**Data Security:**

&nbsp;

&nbsp;

**Physical Security:**

&nbsp;

&nbsp;

## 4. Incident Response Planning

Design an incident response procedure for detecting safety system tampering (PLC-4):

**Detection:**

&nbsp;

&nbsp;

**Analysis:**

&nbsp;

&nbsp;

**Containment:**

&nbsp;

&nbsp;

**Eradication:**

&nbsp;

&nbsp;

**Recovery:**

&nbsp;

&nbsp;

**Lessons Learned:**

&nbsp;

&nbsp;

## 5. Real-World Application

Choose one real-world ICS/SCADA incident and compare it to these lab scenarios:

**Incident Name:** ________________________________________________________

**Year:** _________ **Target Industry:** _________________________________

**Attack Techniques Used:**

&nbsp;

&nbsp;

**Similarities to Lab Exercises:**

&nbsp;

&nbsp;

**Differences from Lab Exercises:**

&nbsp;

&nbsp;

**Lessons Learned:**

&nbsp;

&nbsp;

## 6. Blue Team Perspective

You are a SOC analyst monitoring this ICS environment.

**What alerts would you prioritize investigating first?**

1. ________________________________________________________________

2. ________________________________________________________________

3. ________________________________________________________________

**What log sources would you correlate?**

&nbsp;

&nbsp;

**What indicators of compromise (IOCs) would you look for?**

&nbsp;

&nbsp;

## 7. Ethical Considerations

**Why is it critical to only perform these attacks in authorized lab environments?**

&nbsp;

&nbsp;

**What are the legal consequences of unauthorized ICS/SCADA attacks?**

&nbsp;

&nbsp;

**How can you use this knowledge to improve ICS security defensively?**

&nbsp;

&nbsp;

---

# Skills Checklist

After completing this workbook, I can:

**Red Team Skills:**
- [ ] Identify and enumerate Modbus TCP devices
- [ ] Execute Modbus write coil attacks
- [ ] Execute Modbus write register attacks
- [ ] Manipulate process control systems
- [ ] Bypass safety mechanisms
- [ ] Execute multi-stage attack campaigns
- [ ] Perform stealthy reconnaissance

**Blue Team Skills:**
- [ ] Recognize ICS reconnaissance patterns
- [ ] Detect process manipulation attacks
- [ ] Identify safety system tampering
- [ ] Prioritize security incidents by severity
- [ ] Map attacks to MITRE ATT&CK for ICS
- [ ] Design incident response procedures
- [ ] Implement defense-in-depth for ICS

**General ICS Security:**
- [ ] Understand Modbus protocol fundamentals
- [ ] Recognize real-world attack parallels
- [ ] Analyze cascading failure scenarios
- [ ] Evaluate physical safety implications
- [ ] Apply ethical hacking principles

---

# Final Reflection

## What was the most important thing you learned from these exercises?

&nbsp;

&nbsp;

&nbsp;

## What surprised you most about ICS/SCADA security?

&nbsp;

&nbsp;

&nbsp;

## How will you apply this knowledge in your career?

&nbsp;

&nbsp;

&nbsp;

## What additional ICS security topics would you like to explore?

&nbsp;

&nbsp;

&nbsp;

---

# Certificate of Completion

This certifies that **_______________________________** has successfully completed the ICS/SCADA Security Training Workbook and demonstrated proficiency in industrial control system security concepts.

**Completed:** _____ / _____ lab exercises

**Instructor Name:** ________________________________

**Instructor Signature:** ________________________________

**Date:** ________________________________

**Institution/Organization:** ________________________________

---

## Additional Resources

- MITRE ATT&CK for ICS: https://attack.mitre.org/matrices/ics/
- CISA ICS Security Resources: https://www.cisa.gov/topics/industrial-control-systems
- SANS ICS Security Resources: https://www.sans.org/industrial-control-systems-security/
- Project Repository: [Link to your Vuln-PLC repository]

---

**Version:** 1.0
**Created:** 2025-12-28
**Project:** Vuln-PLC ICS/SCADA Training Environment
