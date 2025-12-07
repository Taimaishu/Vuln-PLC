# OSINT Discovery Guide for ICS/SCADA Systems

## Overview

This guide demonstrates how attackers discover publicly available information about industrial control systems through Open Source Intelligence (OSINT) gathering. All techniques shown are for educational and authorized testing purposes only.

## Table of Contents

1. [Passive Reconnaissance](#passive-reconnaissance)
2. [Active Scanning](#active-scanning)
3. [Social Engineering Intel](#social-engineering-intel)
4. [Data Breach Intelligence](#data-breach-intelligence)
5. [Physical Security](#physical-security)
6. [Putting It All Together](#putting-it-all-together)

---

## Passive Reconnaissance

### 1. Search Engine Discovery

**Google Dorking for ICS Systems:**

```
# Find exposed HMI interfaces
site:chemicalplant.com inurl:scada
site:chemicalplant.com inurl:hmi
site:chemicalplant.com "modbus"

# Find leaked documents
site:chemicalplant.com filetype:pdf "confidential"
site:chemicalplant.com filetype:xlsx "network"
site:chemicalplant.com filetype:doc "password"

# Find backup files
site:chemicalplant.com inurl:backup
site:chemicalplant.com filetype:zip
site:chemicalplant.com "plc backup"

# Find configuration files
site:chemicalplant.com filetype:cfg
site:chemicalplant.com filetype:conf
site:chemicalplant.com "config.txt"

# Find default credentials documentation
site:chemicalplant.com "default password"
site:chemicalplant.com "admin admin"
site:chemicalplant.com "getting started guide"
```

**Findings from ChemicalPlant.com:**
- Network diagram accidentally published on GitHub
- Backup files on anonymous FTP server
- Default credentials in documentation
- Meeting notes with security vulnerabilities

### 2. Shodan/Censys Search

**Finding Exposed ICS Systems:**

```bash
# Shodan queries
shodan search "chemicalplant.com"
shodan search "port:502 modbus"
shodan search "http.title:PLC"
shodan search "http.title:HMI"
shodan search "port:502 country:US"

# Specific to our target
shodan host 203.0.113.50
```

**What Shodan Reveals:**
- Modbus TCP directly exposed (port 502)
- HTTP interfaces with default configurations
- SSL certificates (including expired ones)
- Service banners revealing software versions
- Anonymous FTP access enabled

**Example Output:**
```
IP: 203.0.113.50
Ports: 80, 443, 502, 5000, 21
Services:
  - HTTP (nginx 1.18.0)
  - Modbus (VulnPLC Corp)
  - FTP (vsftpd 3.0.3, anonymous login)

Vulnerabilities:
  - CVE-2021-44228 (Log4Shell) possible
  - Weak SSL configuration
  - Default credentials likely
```

### 3. Domain/DNS Intelligence

**DNS Enumeration:**

```bash
# DNS records
dig chemicalplant.com ANY
dig -x 203.0.113.50  # Reverse DNS

# Subdomain discovery
dig portal.chemicalplant.com
dig vpn.chemicalplant.com
dig ftp.chemicalplant.com
dig hmi.chemicalplant.com
```

**SSL Certificate Analysis:**

```bash
# Certificate transparency logs
crt.sh search for "chemicalplant.com"

# Reveals subdomains:
# - portal.chemicalplant.com
# - vpn.chemicalplant.com
# - hmi.chemicalplant.com
# - remote.chemicalplant.com
```

### 4. GitHub/Code Repository Mining

**Finding Leaked Credentials and Configs:**

```bash
# GitHub search
site:github.com "chemicalplant"
site:github.com "chemicalplant" "password"
site:github.com "192.168.100"

# Discovered repository:
# https://github.com/chemicalplant-ops/docs (deleted)
# But archived on web.archive.org!
```

**What Was Found:**
```
chemicalplant-ops/docs (archived)
├── network_topology.pdf
├── firewall_config.txt
├── default_passwords.xlsx
├── meeting_notes/ (multiple files with sensitive info)
├── vendor_access_guide.pdf
└── plc_backups/ (configuration files!)
```

**Commit History Reveals:**
```bash
git log --all --full-history --source
# Shows deleted files, old passwords, network changes
```

### 5. Social Media Intelligence

**LinkedIn Mining:**

Target employees:
- Mike Johnson - Plant Manager
  - Posts about "upgrading our Rockwell PLCs"
  - Connected to automation vendors

- Sarah Chen - Control Systems Engineer
  - Profile mentions "Modbus TCP/IP, SCADA systems"
  - Previously worked at "Rockwell Automation"
  - Skills: "PLC Programming, RSLogix 5000"

- Dave Miller - IT Security Manager
  - Recent post: "Working on network segmentation project"
  - Comment: "Anyone recommend good ICS firewalls?"

**Twitter/X Posts:**
```
@ChemPlantOps: "Scheduled maintenance today 2-4 PM.
Tank control system will be offline."
# Reveals: Maintenance window, system downtime
```

### 6. Job Postings

**Indeed/LinkedIn Job Listings:**

```
Position: SCADA Administrator
Company: Chemical Plant Operations LLC

Requirements:
- Experience with Rockwell Automation PLCs
- Knowledge of Modbus TCP/IP protocol
- Familiarity with Windows Server 2019
- Network experience (192.168.x.x)

Software:
- RSLogix 5000
- FactoryTalk View
- OSIsoft PI Historian
```

**Intel Gathered:**
- Specific PLC vendor (Rockwell)
- Network addressing scheme
- Software versions
- IT infrastructure details

---

## Active Scanning

### 1. Port Scanning

```bash
# Basic scan
nmap -sV 203.0.113.50

# ICS-specific scan
nmap --script modbus-discover 203.0.113.50 -p 502
nmap --script http-title 203.0.113.50 -p 80,443,5000

# Results:
PORT     STATE SERVICE     VERSION
21/tcp   open  ftp         vsftpd 3.0.3
80/tcp   open  http        nginx 1.18.0
443/tcp  open  https       nginx 1.18.0
502/tcp  open  modbus      Modbus/TCP
5000/tcp open  http        Werkzeug 2.0.1
```

### 2. Modbus Scanning

```bash
# Enumerate Modbus devices
nmap --script modbus-discover -p 502 203.0.113.50

# Read registers (if no auth)
modbus-cli read 203.0.113.50:502 0 10

# Results show:
# - Device ID: VulnPLC-1
# - Registers accessible
# - No authentication required
```

### 3. Web Application Fingerprinting

```bash
# Technology detection
whatweb http://portal.chemicalplant.com

# Results:
# Flask 2.0.1
# Python 3.9
# nginx 1.18.0
# No WAF detected
```

---

## Social Engineering Intel

### 1. Phishing Intelligence

**Credential Harvesting:**
- Spear phishing targeting employees
- Fake vendor update notifications
- Clone legitimate Rockwell Automation emails

**Example Phishing Email:**
```
From: support@rockwe11automation.com (note the '1' instead of 'l')
Subject: URGENT: PLC Firmware Security Update Required

Dear Sarah Chen,

A critical security vulnerability (CVE-2024-XXXX) has been
discovered in VulnPLC firmware v1.0.0. Please download and
install the patch immediately.

Click here: [malicious link]

Rockwell Automation Support Team
```

### 2. Vendor Impersonation

**Pretexting Scenarios:**
- Call helpdesk claiming to be Rockwell support
- Request VPN credentials for "emergency maintenance"
- Use information from OSINT to sound legitimate

**Example Call Script:**
```
"Hi, this is Alex from Rockwell Automation. I'm calling
about the firmware update scheduled for PLC-1 (serial
VPL-001-2023-0042). Sarah Chen opened a ticket yesterday
about the pressure control issue. Can I get VPN access
to push the patch?"
```

---

## Data Breach Intelligence

### 1. Breach Databases

```bash
# Check Have I Been Pwned
https://haveibeenpwned.com/
Search: jsmith@chemicalplant.com

Result: Found in 2023 data breach
Password: ChemPlant2023!

# Likely reused with pattern:
# ChemPlant2024! (current year)
```

### 2. Pastebin/Dark Web

```bash
# Search paste sites
site:pastebin.com "chemicalplant.com"
site:ghostbin.com "192.168.100"

# Dark web forum search
"chemical plant" "PLC" "access"
```

### 3. Password Pattern Analysis

**Observed Patterns:**
```
Common Pattern: [CompanyName][Year]!
Examples:
- ChemPlant2024!
- ChemicalPlant2024
- Sarah2024! (Firstname+Year)
```

---

## Physical Security

### 1. Google Maps/Street View

**Physical Reconnaissance:**
- Facility layout from satellite imagery
- Parking lot (employee vehicles, contractor vans)
- Visible security cameras
- Entry points and access control

**Vendor Vehicles Spotted:**
- "Rockwell Automation" service van
- "AutomationCorp" contractor trucks
- Implies trusted vendors with site access

### 2. Dumpster Diving

**Documents Found:**
- Printed network diagrams
- Old configuration printouts
- Sticky notes with passwords
- Vendor invoices showing equipment details

### 3. Badge Cloning

**Physical Access Badges:**
- Mag stripe readers detected (easier to clone)
- Badge IDs visible in photos: BADGE-001, BADGE-002
- Pattern: BADGE-[XXX] format

---

## Putting It All Together

### Attack Timeline

**Phase 1: Passive OSINT (Day 1-3)**
1. Google dorking reveals network diagram on GitHub
2. Shodan shows exposed Modbus on port 502
3. LinkedIn profiles identified key personnel
4. Job postings reveal technology stack

**Phase 2: Active Reconnaissance (Day 4-5)**
5. Port scanning confirms open services
6. Anonymous FTP access discovered
7. Downloaded backup configurations
8. Found default credentials in multiple places

**Phase 3: Initial Access (Day 6)**
9. Used default credentials: admin/admin
10. Accessed HMI web interface
11. Connected to PLCs via Modbus (no auth)
12. Read process values and control logic

**Phase 4: Persistence (Day 7)**
13. Created backdoor account on HMI
14. Modified PLC logic to hide changes
15. Accessed engineering workstation
16. Planted remote access tools

**Phase 5: Impact (Day 8+)**
17. Manipulate process values
18. Trigger safety incidents
19. Evade detection using ICS-specific techniques
20. Maintain long-term access

### OSINT to Exploitation Flow

```
1. Shodan/Google
   ↓
2. Find exposed services (Modbus, HTTP, FTP)
   ↓
3. GitHub/FTP for configs
   ↓
4. Extract credentials and network topology
   ↓
5. Access HMI with default creds
   ↓
6. Connect to PLCs via Modbus
   ↓
7. Manipulate industrial process
   ↓
8. Real-world impact
```

---

## Defense Recommendations

### 1. Eliminate OSINT Footprint

- [ ] Remove sensitive documents from public repos
- [ ] Secure FTP servers (disable anonymous access)
- [ ] Remove indexed pages from search engines (robots.txt)
- [ ] Monitor for leaked credentials in breaches
- [ ] Train employees on OPSEC

### 2. Secure Exposed Services

- [ ] Do NOT expose Modbus directly to internet
- [ ] Implement VPN for remote access
- [ ] Change all default credentials
- [ ] Enable authentication on PLCs (if supported)
- [ ] Use strong, unique passwords

### 3. Network Segmentation

- [ ] Implement proper firewall between Corp and OT networks
- [ ] Use VLANs for network separation
- [ ] Restrict historian access
- [ ] Monitor all cross-zone traffic

### 4. Monitoring & Detection

- [ ] Deploy IDS on OT network (Zeek, Suricata)
- [ ] Log all Modbus transactions
- [ ] Alert on suspicious access patterns
- [ ] Monitor for unauthorized devices

### 5. Employee Training

- [ ] Security awareness training
- [ ] Phishing simulation exercises
- [ ] Incident response procedures
- [ ] Vendor verification protocols

---

## Tools Used

**OSINT Tools:**
- Shodan / Censys / ZoomEye
- Google Dorking
- theHarvester
- Maltego
- Recon-ng
- SpiderFoot

**Scanning Tools:**
- Nmap with ICS scripts
- Metasploit ICS modules
- modbus-cli
- PLCscan

**Analysis Tools:**
- Wireshark (Modbus dissector)
- GitRob (GitHub secrets scanner)
- FOCA (metadata extraction)
- Metagoofil

---

## Real-World Case Studies

### Case Study 1: Ukrainian Power Grid (2015)
- OSINT revealed network topology
- Spear phishing using employee info
- BlackEnergy malware deployed
- Power outage affecting 225,000 people

### Case Study 2: Triton/Trisis (2017)
- Targeted Schneider Electric safety systems
- Extensive reconnaissance phase
- Custom malware for Triconex controllers
- Could have caused physical damage

### Case Study 3: Colonial Pipeline (2021)
- Compromised VPN credentials
- Ransomware deployment
- Major fuel pipeline shutdown
- $4.4 million ransom paid

---

## Conclusion

OSINT provides attackers with a wealth of information about ICS/SCADA systems without ever touching the target network. The combination of:

1. Exposed services (Shodan)
2. Leaked documents (GitHub, FTP)
3. Employee information (LinkedIn, social media)
4. Breach databases (previous compromises)
5. Physical reconnaissance (Google Maps)

Creates a complete attack blueprint.

**Key Takeaway:** If an attacker can discover it through OSINT, so can defenders. Regular OSINT audits of your own infrastructure are essential for security.

---

## Practice Exercises

### Exercise 1: OSINT Your Own Organization
Use the techniques in this guide to discover what information about your organization is publicly available.

### Exercise 2: Shodan Search
Search for Modbus devices in your region. How many are exposed?

### Exercise 3: GitHub Secrets Scanning
Check your organization's GitHub repos for accidentally committed credentials.

### Exercise 4: Employee Training
Show employees their own digital footprint and train on OPSEC.

---

**Remember:** All techniques shown are for authorized testing and educational purposes only. Unauthorized access to computer systems is illegal.

---

## References

- SANS ICS Security
- NIST Cybersecurity Framework
- ICS-CERT Advisories
- OWASP IoT Top 10
- Shodan ICS Research

