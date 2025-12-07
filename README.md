# Vuln-PLC v2.0
### The Complete ICS/SCADA Security Training Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](docs/media/CONTRIBUTING.md)

> **A comprehensive, intentionally vulnerable industrial control system environment for security training, penetration testing practice, and ICS/SCADA research.**

---

## ⚡ Quick Start

```bash
# Clone the repository
git clone https://github.com/Taimaishu/Vuln-PLC.git
cd Vuln-PLC

# Option 1: Local Installation
./scripts/install.sh
./scripts/start_all.sh

# Option 2: Docker (Recommended)
docker-compose up -d

# Access the HMI Dashboard
firefox http://localhost:8000
```

**Try your first attack:**
```bash
# Force tank overflow
sudo modbus 127.0.0.1:5502 write 0 1   # Pump ON
sudo modbus 127.0.0.1:5502 write 1 0   # Valve CLOSED

# Watch the consequences on HMI: http://localhost:8000
```

---

## 🌟 What's New in v2.0?

### 🎨 Visual SCADA HMI Interface
Real-time P&ID dashboard showing industrial processes:
- Animated tank levels, pressure gauges, temperature displays
- Color-coded alarms (green → yellow → red)
- Live equipment status indicators
- Emergency shutdown warnings
- **See attacks happen visually!**

### ⚗️ Physics-Based Process Simulation
Not just fake numbers - actual industrial physics:
- Tank overflow with pump cavitation
- Pressure vessel rupture
- Thermal runaway scenarios
- Safety interlocks and emergency shutdown

### 📦 PCAP Capture & Forensics
Built-in Modbus IDS with packet capture:
- Real-time intrusion detection
- Automatic PCAP file rotation
- Wireshark-ready for analysis
- Timeline reconstruction for incident response

### 🐳 One-Command Docker Deployment
```bash
docker-compose up -d
```
That's it. 8 services, proper network segmentation, ready in seconds.

---

## 🎯 Features

### 🔴 Red Team / Penetration Testing
- **4 Vulnerable PLCs** with realistic exploits
- **Modbus TCP** protocol manipulation
- **Siemens S7** protocol support
- **Web exploits**: SQL injection, command injection, XSS
- **Authentication bypasses**
- **Session hijacking**
- **Privilege escalation paths**

### 🔵 Blue Team / Defenders
- **Modbus IDS** with signature & anomaly detection
- **PCAP capture** for forensics training
- **System Monitor** dashboard
- **Detection playbooks** with IOCs
- **Incident response exercises**

### 🎓 Educators / Trainers
- **Visual HMI** for engaging demonstrations
- **400+ pages documentation**
- **Step-by-step attack scenarios**
- **Blue team defense guides**
- **CTF-ready challenges**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  DMZ (192.168.50.0/24)                  │
│  ├─ HMI Interface (Visual SCADA)        │
│  ├─ System Monitor (Dashboard)          │
│  └─ Historian (Data Collection)         │
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
- Docker + Docker Compose

---

## 📚 Documentation

### Getting Started
- **[Quick Start Guide](docs/getting-started/QUICK_START.md)** - Get running in 5 minutes
- **[Installation Guide](docs/getting-started/INSTALL_GUIDE.md)** - Detailed setup
- **[Docker Deployment](docs/getting-started/DOCKER_DEPLOYMENT.md)** - Container setup

### Attack Documentation
- **[Attack Scenarios](docs/attack/ATTACK_SCENARIOS.md)** - Step-by-step exploits
- **[Evasion Techniques](docs/attack/EVASION_TECHNIQUES.md)** - Advanced tactics
- **[Modbus CLI Reference](docs/attack/MODBUS_CLI_REFERENCE.md)** - Command syntax
- **[Privilege Escalation](docs/attack/PRIVILEGE_ESCALATION.md)** - Exploit chains

### Defense Documentation
- **[Blue Team Guide](docs/defense/BLUE_TEAM_GUIDE.md)** - Defense strategies
- **[Detection Playbook](docs/defense/DETECTION_PLAYBOOK.md)** - IOCs & alerts
- **[PCAP Analysis](docs/defense/)** - Forensics exercises

### Architecture & Advanced
- **[Architecture Overview](docs/architecture/ARCHITECTURE.md)** - System design
- **[Advanced Features](docs/architecture/ADVANCED_FEATURES.md)** - PLC engine, IDS
- **[Development Roadmap](docs/architecture/ROADMAP.md)** - Future plans

---

## 🚀 Usage

### Access Interfaces

**Main Dashboards:**
- **HMI Dashboard:** http://localhost:8000 🎨
- **System Monitor:** http://localhost:5999 📊
- **Historian:** http://localhost:8888 (historian/data123) 📈

**PLC Web Interfaces:**
- **PLC-1 (Tank):** http://localhost:5000 (admin/admin)
- **PLC-2 (Pressure):** http://localhost:5011 (engineer/plc2pass)
- **PLC-3 (Temperature):** http://localhost:5012 (engineer/temp123)
- **PLC-4 (Safety):** http://localhost:5013 (safety_eng/safe123)

**Modbus TCP Endpoints:**
- PLC-1: `127.0.0.1:5502`
- PLC-2: `127.0.0.1:5503`
- PLC-3: `127.0.0.1:5504`
- PLC-4: `127.0.0.1:5505`

### Example Attacks

**Tank Overflow (Visual Impact):**
```bash
# Open HMI: http://localhost:8000
sudo modbus 127.0.0.1:5502 write 0 1   # Force pump ON
sudo modbus 127.0.0.1:5502 write 1 0   # Force valve CLOSED
# Watch tank overflow in real-time!
```

**Pressure Spike:**
```bash
sudo modbus 127.0.0.1:5503 write 0 1   # Compressor ON
sudo modbus 127.0.0.1:5503 write 1 0   # Relief valve CLOSED
# Pressure rises until rupture
```

**SQL Injection:**
```bash
curl -X POST http://localhost:5000/login \
  -d "username=admin' OR '1'='1&password=x"
```

**More scenarios:** See [docs/attack/ATTACK_SCENARIOS.md](docs/attack/ATTACK_SCENARIOS.md)

---

## ⚙️ Installation

### Requirements
- Python 3.9+
- pip
- (Optional) Docker + Docker Compose

### Local Installation
```bash
git clone https://github.com/Taimaishu/Vuln-PLC.git
cd Vuln-PLC

# Install dependencies
./scripts/install.sh

# Start all services
./scripts/start_all.sh

# Stop all services
./scripts/stop_all.sh

# Check status
./scripts/status.sh
```

### Docker Installation
```bash
# Basic deployment (4 PLCs + Historian)
docker-compose up -d

# Full deployment (includes IDS, Monitor, Network Sim)
docker-compose --profile full up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🗺️ Roadmap

### Q1 2025: Additional Protocols
- ✨ EtherNet/IP (CIP) - Allen-Bradley/Rockwell
- ✨ DNP3 - Power utility SCADA
- ✨ OPC UA - Industry 4.0

### Q2 2025: Enhanced Realism
- 📈 HMI trend charts (historian views)
- 🖥️ VNC-based Windows HMI
- 🔧 Vendor-specific CVE emulation

### Q3 2025: Advanced Features
- 🤖 ML-based anomaly detection
- 🔁 Automated attack scenarios
- 🍯 Honeypot capabilities

See **[ROADMAP.md](docs/architecture/ROADMAP.md)** for complete timeline.

---

## 🤝 Contributing

We welcome contributions! Areas of interest:

**High Priority:**
- EtherNet/IP (CIP) protocol implementation
- HMI trend charts and historian integration
- ML-based IDS enhancements

**Documentation:**
- Video tutorials
- CTF challenges
- Training materials

See **CONTRIBUTING.md** for guidelines.

---

## ⚠️ Security Notice

**THIS IS INTENTIONALLY VULNERABLE SOFTWARE FOR EDUCATIONAL PURPOSES.**

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

**Use responsibly. Get authorization. Follow the law.**

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- ICS security community
- Open-source contributors
- Security researchers worldwide

Special thanks to all who provided feedback and feature requests.

---

## 📞 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/Taimaishu/Vuln-PLC/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Taimaishu/Vuln-PLC/discussions)
- **Pull Requests:** Always welcome!

---

## 🔗 Related Projects

- **[Conpot](https://github.com/mushorg/conpot)** - ICS honeypot
- **[SCADABR](https://github.com/SCADA-LTS/Scada-LTS)** - Open source SCADA
- **[PLCSimulator](https://github.com/automaticserver/plc4j)** - PLC communication library

---

## ⭐ Star History

If you find Vuln-PLC useful, please consider starring the repository!

---

**Built with ❤️ for the ICS security community**

*Last Updated: 2024-12-07*
*Version: 2.0.0*
