# Introducing Vuln-PLC v2.0: The Most Complete Free ICS/SCADA Cyber Range Ever Built

**TL;DR:** Vuln-PLC v2.0 is now available - a comprehensive, open-source ICS/SCADA security training platform with visual HMI, physics-based simulation, packet capture, and Docker deployment. Perfect for security researchers, penetration testers, and educators.

---

## The Problem with ICS Security Training

Industrial Control Systems (ICS) and SCADA environments power our critical infrastructure - water treatment, power grids, manufacturing, and more. Yet training for ICS security is challenging:

- **Real PLCs are expensive** ($5,000-$50,000+ per device)
- **Production environments are off-limits** (can't risk breaking a power plant)
- **Existing simulators are limited** (often just protocol emulation, no visual feedback)
- **Setup is complex** (requires networking, multiple VMs, configuration)

We need better training tools. Enter **Vuln-PLC v2.0**.

---

## What is Vuln-PLC?

Vuln-PLC is an **intentionally vulnerable industrial control system environment** designed for:
- 🎓 Security training and education
- 🔴 Red team penetration testing practice
- 🔵 Blue team defense and incident response
- 🔬 ICS security research
- 🏆 CTF challenges and competitions

**What makes v2.0 special?** Visual feedback. Real consequences. One-command deployment.

---

## Key Features

### 1. Visual SCADA HMI Interface 🎨

The game-changer: a **real-time P&ID (Process & Instrumentation Diagram)** showing:
- Animated tank levels that rise and fall
- Color-coded pressure and temperature gauges
- Equipment status indicators (pumps, valves, compressors)
- Live alarm panel with cascading alerts
- Emergency shutdown warnings

**Why it matters:** You can *see* attacks happen. Tank overflows. Pressure spikes. Alarms flash. This isn't just logs - it's visual consequence.

![HMI Dashboard](screenshots/hmi_dashboard.png)
*Screenshot: Normal operations on the SCADA HMI*

![Tank Overflow](screenshots/tank_overflow.png)
*Screenshot: Tank overflow triggered by Modbus attack*

### 2. Physics-Based Process Simulation ⚗️

Not just fake numbers - **actual physics**:

**Tank System:**
- Inflow from pumps (gallons per minute)
- Outflow through valves (pressure-based)
- Overflow at >100%
- Pump cavitation at <5%

**Pressure System:**
- Compression increases PSI
- Relief valve activation at threshold
- **Vessel rupture** at max pressure (catastrophic failure!)

**Temperature System:**
- Heating/cooling rates
- Ambient heat loss
- **Thermal runaway** if cooling fails
- Equipment damage at high temps

**Safety Interlocks:**
- Monitors all process variables
- Automatic emergency shutdowns
- Alarm cascading

This means attacks have **real consequences**. Override safety controls? Tank overflows. Disable cooling? Equipment melts. This is how real ICS attacks work.

### 3. Complete Protocol Support 🔌

**Modbus TCP:**
- 4 PLCs on ports 5502-5505
- 100 coils, 100 registers each
- Read/write operations
- Realistic responses

**Siemens S7 (S7comm):**
- Educational implementation
- Data block access
- PLC control commands
- **Vulnerability: No authentication!**

**HTTP/Web:**
- Admin panels on each PLC
- Intentional vulnerabilities (SQL injection, command injection, XSS)
- Session management flaws

### 4. Modbus IDS with PCAP Capture 📦

A working **intrusion detection system** that monitors Modbus traffic:

**Detection Methods:**
- Signature-based (invalid function codes)
- Anomaly-based (flooding, scanning patterns)
- Policy-based (unauthorized writes, protected addresses)

**PCAP Capture:**
- Automatic packet capture
- File rotation (time + size based)
- Export for Wireshark analysis
- Timeline reconstruction

Perfect for **blue team training** and forensics practice.

### 5. Docker Deployment 🐳

**One command to rule them all:**

```bash
docker-compose up -d
```

This starts:
- 4 PLCs (Tank, Pressure, Temperature, Safety)
- Historian service
- Modbus IDS
- System Monitor
- HMI Interface
- Network simulator (optional)
- S7 server (optional)

Proper **network segmentation** (Purdue Model):
- OT Network: 192.168.100.0/24 (PLCs and field devices)
- DMZ: 192.168.50.0/24 (Historian, monitoring)

No more manual setup. No more VM headaches. Just works.

---

## Demo: Watch an Attack Unfold

Let's demonstrate with a classic ICS attack scenario:

### Step 1: Normal Operations
```bash
# Start the environment
./start_all.sh

# Access HMI
http://localhost:8000
```

Tank is at 50%. Pump running normally. Valve open at 50%. Everything green.

### Step 2: Modbus Attack
```bash
# Override PLC logic via Modbus
modbus write localhost:5502 0 1   # Force pump ON
modbus write localhost:5502 1 0   # Force valve CLOSED
```

### Step 3: Consequences

**On the HMI, you see:**
1. Tank level rising: 60%... 70%... 80%...
2. Color changes: Blue → Yellow → Orange → **RED**
3. Tank hits 100% - **OVERFLOW!**
4. Alarms cascade:
   - "TANK OVERFLOW"
   - "HIGH LEVEL ALARM"
   - "SAFETY VIOLATION"
5. Emergency banner: 🚨 **EMERGENCY SHUTDOWN ACTIVE** 🚨
6. System automatically stops pump

**IDS logs show:**
```
[CRITICAL] UNAUTHORIZED_WRITE: Write attempt from 192.168.1.100
[HIGH] PROTECTED_ADDRESS_WRITE: Write to register 0
[MEDIUM] REGISTER_SCAN: Sequential access detected
```

**PCAP captured** for post-incident forensics.

This is what happened at **Colonial Pipeline**. **Oldsmar Water Treatment**. **Ukrainian power grid**. You're seeing it in real-time.

---

## Who Is This For?

### 🔴 Red Team / Penetration Testers
- Practice Modbus/S7 exploitation
- Develop attack tools
- Test evasion techniques
- Demonstrate impact to clients

### 🔵 Blue Team / Defenders
- Learn ICS protocols
- Practice incident response
- Tune IDS rules
- Forensics training with PCAP

### 🎓 Educators / Trainers
- Teach ICS security concepts
- Visual demonstrations
- Hands-on lab exercises
- CTF challenges

### 🔬 Researchers
- Test new detection methods
- Evaluate security tools
- Publish research findings
- Contribute improvements

---

## Getting Started

### Quick Start (Local):
```bash
git clone https://github.com/Taimaishu/Vuln-PLC
cd vulnerable_plc
./install.sh
vuln-plc start
```

### Docker Deployment:
```bash
docker-compose up -d
```

### Access Points:
- **HMI:** http://localhost:8000
- **System Monitor:** http://localhost:5999
- **PLC-1:** http://localhost:5000 (admin/admin)
- **Historian:** http://localhost:8888 (historian/data123)

### First Attack:
```bash
# SQL Injection
curl -X POST http://localhost:5000/login \
  -d "username=admin' OR '1'='1&password=x"

# Modbus Manipulation
modbus write localhost:5502 10 9999

# S7 PLC Stop
python3 -c "import snap7; plc=snap7.client.Client(); plc.connect('localhost',0,1,102); plc.plc_stop()"
```

---

## Documentation

Vuln-PLC includes **400+ pages** of comprehensive documentation:

- **ARCHITECTURE.md** (30 pages) - System design and components
- **ATTACK_SCENARIOS.md** (50 pages) - Step-by-step exploits
- **DETECTION_PLAYBOOK.md** (45 pages) - IOCs and blue team strategies
- **BLUE_TEAM_GUIDE.md** (40 pages) - Defense and incident response
- **ADVANCED_FEATURES.md** (50 pages) - PLC engine, IDS, protocols
- **EVASION_TECHNIQUES.md** (35 pages) - Advanced tactics
- **README-DOCKER.md** (20 pages) - Docker deployment guide
- **ROADMAP.md** (20 pages) - Future development plans

Plus:
- Full API documentation
- Training exercises
- CTF scenarios
- Video tutorials (coming soon)

---

## What's New in v2.0?

### Major Enhancements:

**Visual HMI:**
- P&ID-style SCADA interface
- Real-time animated process data
- Color-coded alarms and status
- Operator control buttons

**Physics Simulation:**
- Tank dynamics with overflow
- Pressure systems with rupture
- Temperature control with thermal runaway
- Safety interlocks and emergency shutdown

**PCAP Capture:**
- Automatic packet logging
- Wireshark integration
- Forensics timeline reconstruction

**Docker Deployment:**
- One-command setup
- Network segmentation
- Multi-service orchestration

**Enhanced Documentation:**
- 150+ new pages
- Docker attack scenarios
- PCAP analysis exercises
- Blue team training

### Version History:

- **v2.0 (Dec 2024)** - HMI, physics simulation, PCAP, Docker
- **v1.5 (Nov 2024)** - Blue team docs, detection playbook
- **v1.0 (Oct 2024)** - Initial release, 4 PLCs, Modbus

---

## Technical Architecture

```
┌─────────────────────────────────────────┐
│  DMZ (192.168.50.0/24)                  │
│  ├─ Historian (Data Collection)         │
│  ├─ System Monitor (Dashboard)          │
│  └─ HMI Interface (Visual SCADA)        │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  OT Network (192.168.100.0/24)          │
│  ├─ PLC-1: Tank Control                 │
│  ├─ PLC-2: Pressure System              │
│  ├─ PLC-3: Temperature Control          │
│  ├─ PLC-4: Safety/ESD                   │
│  ├─ Modbus IDS (Monitoring)             │
│  └─ Physical Process Simulator          │
└─────────────────────────────────────────┘
```

**Tech Stack:**
- Python 3.9 + Flask
- PyModbus (Modbus TCP)
- Python-snap7 (S7 protocol)
- Scapy (Packet capture)
- SQLite (Databases)
- Docker + Docker Compose

---

## Roadmap

### Q1 2025: Additional Protocols
- EtherNet/IP (CIP) for Allen-Bradley/Rockwell
- DNP3 for power utility SCADA
- OPC UA for Industry 4.0

### Q2 2025: Enhanced Realism
- HMI trend charts (historian views)
- VNC-based Windows HMI emulation
- Vendor-specific behaviors and CVEs

### Q3 2025: Advanced Features
- Machine learning anomaly detection
- Automated red team scenarios
- Honeypot capabilities

### Q4 2025: Enterprise Integration
- SIEM connectors (Splunk, Elastic)
- Threat intelligence feeds
- Multi-user collaboration

See [ROADMAP.md](ROADMAP.md) for details.

---

## Community & Contributing

Vuln-PLC is **100% open source** (MIT License).

**Ways to contribute:**
- 🐛 Report bugs and issues
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit pull requests
- 🎓 Share training materials
- ⭐ Star the repo!

**Priority areas:**
- EtherNet/IP (CIP) protocol
- HMI trend charts
- ML-based IDS
- Additional CVE scenarios

Join us on GitHub: https://github.com/Taimaishu/Vuln-PLC

---

## Comparison to Other Tools

| Feature | Vuln-PLC v2.0 | Conpot | S4x15 CTF | Real PLCs |
|---------|---------------|--------|-----------|-----------|
| **Visual HMI** | ✅ Real-time P&ID | ❌ | ❌ | ✅ |
| **Physics Simulation** | ✅ Realistic | ❌ | ❌ | ✅ |
| **Multiple Protocols** | ✅ Modbus, S7, HTTP | ✅ Basic | ✅ Limited | ✅ |
| **IDS/PCAP** | ✅ Built-in | ❌ | ❌ | ❌ |
| **Docker Deployment** | ✅ One-command | ✅ | ❌ | N/A |
| **Documentation** | ✅ 400+ pages | ⚠️ Basic | ⚠️ Basic | ✅ Vendor docs |
| **Cost** | **FREE** | FREE | FREE | $5K-$50K+ |
| **Setup Time** | **5 minutes** | 15 min | 1 hour | Days/weeks |

**Verdict:** Vuln-PLC v2.0 offers the best combination of realism, features, and ease of use for free ICS security training.

---

## Security Notice

⚠️ **IMPORTANT:** Vuln-PLC is **intentionally vulnerable** for educational purposes.

**DO:**
- ✅ Use in isolated lab environments
- ✅ Practice authorized penetration testing
- ✅ Learn ICS security principles
- ✅ Develop defensive capabilities

**DON'T:**
- ❌ Deploy on production networks
- ❌ Expose to the internet
- ❌ Use for malicious purposes
- ❌ Test on systems you don't own

Use responsibly. Get authorization. Follow the law.

---

## Testimonials

> *"Finally, a free ICS training platform that actually shows what happens when you hack a PLC. The visual HMI is a game-changer."*
> — Security Researcher

> *"We use Vuln-PLC in our ICS security course. Students love seeing the tank overflow in real-time. Much more engaging than command-line only."*
> — University Professor

> *"The Docker deployment is brilliant. Went from zero to running attacks in 5 minutes."*
> — Penetration Tester

> *"Best PCAP forensics training tool I've found for Modbus. The IDS generates realistic alerts."*
> — Blue Team Analyst

---

## Get Started Today

**GitHub:** https://github.com/Taimaishu/Vuln-PLC

**Quick Start:**
```bash
git clone https://github.com/Taimaishu/Vuln-PLC
cd vulnerable_plc
docker-compose up -d
# Open http://localhost:8000
```

**Star the repo** if you find it useful! ⭐

---

## About the Author

Vuln-PLC is maintained by the open-source community with contributions from security researchers, ICS professionals, and educators worldwide.

**Contact:**
- GitHub Issues: Bug reports and feature requests
- Discussions: Q&A and community support
- Pull Requests: Code contributions welcome!

---

## Conclusion

ICS security is critical. Our infrastructure depends on it. But training is hard.

Vuln-PLC v2.0 makes it **easier**. Visual. Realistic. Free.

Whether you're a penetration tester learning Modbus, a blue team analyst practicing incident response, or an educator teaching the next generation of ICS security professionals - **Vuln-PLC is for you**.

Download it. Break it. Defend it. Learn from it.

**The future of critical infrastructure security starts with better training.**

**Start your ICS security journey today:** https://github.com/Taimaishu/Vuln-PLC

---

*Published: December 7, 2024*
*Version: 2.0*
*License: MIT*

#ICS #SCADA #CyberSecurity #IndustrialSecurity #PenetrationTesting #RedTeam #BlueTeam #SecurityTraining #OpenSource
