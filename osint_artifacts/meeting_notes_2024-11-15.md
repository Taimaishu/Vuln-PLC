# Weekly Engineering Meeting - November 15, 2024
**Attendees:** Sarah Chen, John Smith, Lisa Brown, Michael Anderson
**Location:** Conference Room B
**Time:** 10:00 AM - 11:30 AM

## Agenda Items

### 1. Network Security Audit Findings
- External auditor found CRITICAL issues with network segmentation
- **Action Item:** Firewall needs reconfiguration - CorpNet should NOT have direct access to OT network
- Timeline: Pushed to Q1 2025 (budget constraints)
- Temporary mitigation: Monitor logs more frequently

**CONCERN:** Until firewall is fixed, any compromised laptop on CorpNet can directly access PLCs!

### 2. Device 192.168.100.99 Investigation
- Unknown device causing network congestion
- Generates ~500 packets/second to PLCs
- **Root cause:** Old temperature sensor with faulty firmware
- **Action:** Schedule maintenance window to replace (next Tuesday 2PM-4PM)
- Mike approved 2-hour downtime

### 3. Default Password Issue
- Security scan revealed multiple systems still using default credentials
- **Systems affected:**
  - HMI Server: admin/admin
  - Historian: historian/data123
  - PLC-1, 2, 3: No authentication on Modbus
  - PLC-4 Safety Override: 1234 (CRITICAL!)
- **Action:** Create password rotation policy
- **Status:** IN PROGRESS (60% complete)

**NOTE:** PLC-4 safety override code MUST be changed - it's documented in multiple places

### 4. Recent Incidents
- **Nov 10:** Pressure vessel 1 exceeded 175 PSI (limit is 150)
  - Relief valve opened automatically
  - No injuries
  - Cause: Operator error + faulty sensor
  - **Mitigation:** Added additional pressure monitoring

- **Nov 12:** Temperature control thermal runaway
  - Zone 1 reached 95°C (safe limit 80°C)
  - Emergency cooling activated
  - **Root cause:** Software bug in PLC-3 logic
  - **Status:** Patched on Nov 13

### 5. Vendor Access
- Rockwell Automation needs remote access for PLC firmware update
- VPN credentials: rockwell_support / Automation2024
- **Access granted:** Nov 20-22 (3 days)
- **Scope:** PLC-1 and PLC-2 only
- Michael will monitor their activities

**SECURITY CONCERN:** Vendor has full OT network access, not just specific PLCs

### 6. Backup System
- Weekly PLC backups to \\192.168.1.20\PLC_Backups
- **Issue:** File share has no password protection
- **Risk:** Anyone on network can access/modify backup files
- **Action:** Dave Miller to implement access controls by end of month

### 7. Planned Upgrades
- Q1 2025: Deploy Zeek IDS on OT network
- Q2 2025: Implement proper network segmentation
- Q3 2025: Replace all PLCs with newer models (with authentication)
- Q4 2025: Complete security audit and compliance review

### 8. Emergency Procedures
- Updated emergency shutdown procedure document
- **Location:** \\192.168.1.20\Procedures\Emergency_Shutdown_v3.pdf
- All operators trained on new procedure
- Emergency contact: Plant Manager (555-0101) or Safety Manager (555-0105)

## Action Items Summary
| Task | Owner | Due Date | Status |
|------|-------|----------|--------|
| Fix firewall segmentation | Dave Miller | Q1 2025 | Not Started |
| Replace faulty device (.99) | James Taylor | Nov 19, 2PM | Scheduled |
| Change default passwords | Michael Anderson | Dec 1 | In Progress |
| Update PLC-4 safety code | Sarah Chen | Nov 30 | Pending |
| Implement backup access controls | Dave Miller | Nov 30 | Not Started |

## Open Discussion
- John asked about penetration testing - Sarah said "maybe next year"
- Lisa raised concerns about lack of IDS/IPS on OT network
- Michael mentioned seeing suspicious login attempts from 192.168.1.100 (employee laptop)
  - Investigated - false positive (authorized access)

## Next Meeting
**Date:** November 22, 2024
**Time:** 10:00 AM
**Location:** Conference Room B

---
**CONFIDENTIAL - INTERNAL USE ONLY**

**NOTE:** This document was accidentally left on Mike Johnson's laptop, which was later stolen from his car on Nov 20, 2024.
Police report filed. All passwords should be considered compromised.
Incident report: IR-2024-Nov-021

**UPDATE (Nov 21):** Laptop recovered, but hard drive was accessed.
Changing all credentials over next 2 weeks.
