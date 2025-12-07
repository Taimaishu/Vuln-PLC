# 🎉 Vuln-PLC v2.0 - Major Release

## Visual SCADA HMI, Physics Simulation, and Complete Docker Deployment

We're excited to announce **Vuln-PLC v2.0** - the most comprehensive open-source ICS/SCADA security training platform available!

---

## 🌟 Highlights

### Visual SCADA HMI Interface
The game-changing feature: a **real-time P&ID dashboard** showing industrial processes with:
- Animated tank levels, pressure gauges, temperature displays
- Live equipment status (pumps, valves, compressors)
- Color-coded alarms and emergency warnings
- Operator control buttons
- **See attacks happen in real-time!**

![HMI Dashboard](https://raw.githubusercontent.com/Taimaishu/Vuln-PLC/main/screenshots/hmi_dashboard.png)

### Physics-Based Simulation
Not just fake numbers - **actual industrial physics**:
- Tank overflow with cavitation
- Pressure vessel rupture
- Thermal runaway
- Safety interlocks and emergency shutdown

### PCAP Capture & Forensics
Built-in Modbus IDS with:
- Real-time packet capture
- Automatic file rotation
- Wireshark-ready PCAPs
- Timeline reconstruction for incident response training

### One-Command Docker Deployment
```bash
docker-compose up -d
```
That's it. 8 services, proper network segmentation, ready in seconds.

---

## 📦 What's Included

- **4 PLCs** with realistic vulnerabilities
- **Modbus + S7 protocols**
- **Visual HMI** (http://localhost:8000)
- **System Monitor** dashboard
- **Historian** service
- **Modbus IDS** with PCAP
- **Physical process simulator**
- **Network traffic generator**
- **400+ pages documentation**

---

## 🚀 Quick Start

### Docker (Recommended):
```bash
git clone https://github.com/Taimaishu/Vuln-PLC.git
cd Vuln-PLC
docker-compose up -d
```

### Local Install:
```bash
git clone https://github.com/Taimaishu/Vuln-PLC.git
cd Vuln-PLC
./install.sh
vuln-plc start
```

### Access:
- **HMI:** http://localhost:8000 (Visual SCADA interface)
- **System Monitor:** http://localhost:5999
- **PLC-1:** http://localhost:5000 (admin/admin)
- **Historian:** http://localhost:8888

---

## 🎯 Demo: Tank Overflow Attack

Watch what happens when an attacker overrides safety controls:

```bash
# Force pump ON + valve CLOSED
modbus write localhost:5502 0 1
modbus write localhost:5502 1 0
```

**Result on HMI:**
1. Tank level rises rapidly
2. Color changes: Blue → Yellow → Red
3. Tank overflows at 100%
4. Alarms cascade
5. Emergency shutdown activates

**This is what real ICS attacks look like.**

---

## 📊 What's New in v2.0

### Major Features:
- ✨ **HMI Visualization** - P&ID-style SCADA interface with live data
- ⚗️ **Physics Simulation** - Realistic tank/pressure/temperature dynamics
- 📦 **PCAP Capture** - Packet logging for forensics
- 🐳 **Docker Deployment** - One-command setup with network segmentation
- 📚 **Enhanced Docs** - 150+ pages added (400+ total)

### New Files:
- `hmi_server.py` - Visual SCADA server
- `physical_process.py` - Physics-based simulation
- `templates/hmi_dashboard.html` - HMI interface
- `README-DOCKER.md` - Docker guide
- `ROADMAP.md` - Development roadmap
- Docker attack scenarios in docs

### Enhanced Features:
- Modbus IDS with PCAP capture
- System monitor web dashboard
- Physical process integration
- Start script improvements
- Comprehensive training exercises

---

## 🎓 Use Cases

### Red Team / Penetration Testers
- Practice Modbus/S7 exploitation
- Develop attack tools and techniques
- Test IDS evasion methods
- Demonstrate impact with visual HMI

### Blue Team / Defenders
- IDS tuning and alert validation
- Incident response drills
- PCAP forensics training
- Baseline traffic analysis

### Educators / Trainers
- Teach ICS security concepts
- Visual attack demonstrations
- Hands-on lab exercises
- CTF challenge development

### Researchers
- Test detection algorithms
- Evaluate security tools
- Publish research findings
- Contribute improvements

---

## 📚 Documentation

Comprehensive training materials included:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design (30 pages)
- **[ATTACK_SCENARIOS.md](docs/ATTACK_SCENARIOS.md)** - Exploits (50 pages)
- **[BLUE_TEAM_GUIDE.md](docs/BLUE_TEAM_GUIDE.md)** - Defense (40 pages)
- **[DETECTION_PLAYBOOK.md](docs/DETECTION_PLAYBOOK.md)** - IOCs (45 pages)
- **[ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)** - PLC engine, IDS (50 pages)
- **[README-DOCKER.md](README-DOCKER.md)** - Docker deployment (20 pages)
- **[ROADMAP.md](ROADMAP.md)** - Future plans (20 pages)

Plus training exercises, CTF scenarios, and video tutorials (coming soon).

---

## 🗺️ Roadmap

### Q1 2025: Additional Protocols
- EtherNet/IP (CIP) - Allen-Bradley/Rockwell
- DNP3 - Power utility SCADA
- OPC UA - Industry 4.0

### Q2 2025: Enhanced Realism
- HMI trend charts
- VNC-based Windows HMI
- Vendor-specific CVE emulation

### Q3 2025: Advanced Features
- ML-based anomaly detection
- Automated attack scenarios
- Honeypot capabilities

See [ROADMAP.md](ROADMAP.md) for complete timeline.

---

## 🤝 Contributing

We welcome contributions! Priority areas:

- **High Priority:**
  - EtherNet/IP (CIP) protocol
  - HMI trend charts
  - ML-based IDS

- **Medium Priority:**
  - DNP3, OPC UA protocols
  - Vendor CVE scenarios
  - Advanced persistence

- **Documentation:**
  - Video tutorials
  - CTF challenges
  - Training materials

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 🆚 Comparison

| Feature | Vuln-PLC v2.0 | Other Tools | Real PLCs |
|---------|---------------|-------------|-----------|
| Visual HMI | ✅ | ❌ | ✅ |
| Physics Sim | ✅ | ❌ | ✅ |
| PCAP/IDS | ✅ | ❌ | ❌ |
| Docker | ✅ | ⚠️ | N/A |
| Docs | 400+ pages | Basic | Vendor |
| Cost | **FREE** | FREE | $5K-$50K |
| Setup | **5 min** | 15-60 min | Days |

**Verdict:** Best free ICS training platform available.

---

## ⚠️ Security Notice

**This is intentionally vulnerable software for educational purposes.**

**DO:**
- ✅ Use in isolated lab environments
- ✅ Authorized security testing only
- ✅ Learn ICS security principles

**DON'T:**
- ❌ Deploy on production networks
- ❌ Expose to the internet
- ❌ Use for malicious purposes

Use responsibly. Get authorization. Follow the law.

---

## 🙏 Acknowledgments

Thank you to:
- All contributors and testers
- ICS security community
- Open-source maintainers
- Security researchers worldwide

Special thanks to everyone who provided feedback and feature requests.

---

## 📝 Changelog

### v2.0.0 (2024-12-07)

**Added:**
- Visual SCADA HMI interface with P&ID diagrams
- Physics-based process simulation (tank/pressure/temperature)
- PCAP capture in Modbus IDS
- Complete Docker deployment with network segmentation
- System monitor web dashboard
- Physical process simulator
- 150+ pages new documentation
- Docker attack scenarios
- PCAP forensics exercises

**Enhanced:**
- Modbus IDS with packet capture
- Start script with all services
- README with new features
- Attack scenarios documentation
- Blue team training guide

**Fixed:**
- PLC-1 Modbus sync issues
- Network traffic log optimization
- Documentation formatting

### v1.5.0 (2024-11-XX)

- Added blue team documentation
- Detection playbook
- Evasion techniques guide

### v1.0.0 (2024-10-XX)

- Initial release
- 4 PLCs with vulnerabilities
- Modbus TCP support
- Basic documentation

---

## 📦 Assets

### Download Options:

- **Source Code (zip):** [vuln-plc-v2.0.zip](../../archive/refs/tags/v2.0.zip)
- **Source Code (tar.gz):** [vuln-plc-v2.0.tar.gz](../../archive/refs/tags/v2.0.tar.gz)

### Docker Image:
```bash
docker pull taimaishu/vuln-plc:v2.0
```

### Requirements:
- Python 3.9+
- Docker + Docker Compose (recommended)
- 4GB RAM, 10GB disk
- Linux/macOS (Windows via WSL2)

---

## 🔗 Links

- **GitHub:** https://github.com/Taimaishu/Vuln-PLC
- **Documentation:** [README.md](README.md)
- **Demo Video:** [Coming Soon]
- **Blog Post:** [BLOG_POST.md](BLOG_POST.md)
- **Issues:** https://github.com/Taimaishu/Vuln-PLC/issues

---

## 📣 Spread the Word

If you find Vuln-PLC useful:
- ⭐ **Star the repo**
- 🔄 **Share on social media**
- 📝 **Write about your experience**
- 🎓 **Use in your training**
- 🤝 **Contribute improvements**

---

## 🎬 What's Next?

1. **Try it:** `docker-compose up -d`
2. **Attack it:** Execute Modbus attacks
3. **Watch it:** See consequences on HMI
4. **Defend it:** Practice blue team response
5. **Learn from it:** Study PCAPs and alerts

**Start your ICS security journey today!**

---

*Released: December 7, 2024*
*Version: 2.0.0*
*License: MIT*

**Happy hacking! 🏭🔐**
