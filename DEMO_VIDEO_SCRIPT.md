# Vuln-PLC Demo Video Script (45 seconds)

## Title Slide (3 seconds)
**Text on screen:**
```
Vuln-PLC v2.0
The Complete ICS/SCADA Security Training Platform
```

**Voiceover:** "Introducing Vuln-PLC - the most comprehensive free ICS security training environment."

---

## Scene 1: HMI Overview (7 seconds)
**Show:** Full HMI dashboard at http://localhost:8000
- Tank system on left (50% full, normal green)
- Pressure gauge in middle (80 PSI, green)
- Temperature on right (20°C, green)
- Alarm panel showing "No active alarms"

**Voiceover:** "A realistic SCADA HMI interface showing a water treatment plant with live process data."

---

## Scene 2: Normal Operation (5 seconds)
**Show:**
- Click "START PUMP" button
- Watch pump indicator light turn green
- Tank level slowly rises from 50% to 55%

**Voiceover:** "Under normal operation, everything runs smoothly."

---

## Scene 3: Attack Execution (8 seconds)
**Show:** Split screen or quick switch:
- Left: Terminal with commands
- Right: HMI dashboard

**Terminal commands (type these):**
```bash
# Force pump ON
sudo modbus 127.0.0.1:5502 write 0 1

# Force valve CLOSED
sudo modbus 127.0.0.1:5502 write 1 0
```

**Voiceover:** "But watch what happens when an attacker uses Modbus to override safety controls."

---

## Scene 4: Consequences Unfold (12 seconds)
**Show:** HMI dashboard
- Tank level rising rapidly: 60%... 70%... 80%... 90%...
- Tank color changing from blue → yellow → orange → RED
- Tank reaches 100% - OVERFLOW!
- Multiple alarms flash in alarm panel:
  - "TANK OVERFLOW"
  - "HIGH LEVEL ALARM"
  - "PUMP CAVITATION"
- Emergency banner appears: "🚨 EMERGENCY SHUTDOWN ACTIVE 🚨"
- System status changes from green to RED
- Pump automatically stops

**Voiceover:** "The tank overflows. Alarms cascade. Emergency shutdown activates. This is what real ICS attacks look like."

---

## Scene 5: Feature Highlights (7 seconds)
**Show:** Quick cuts of:
1. Docker compose up command (1 sec)
2. System monitor dashboard (2 sec)
3. PCAP file in Wireshark (2 sec)
4. Code editor showing physical_process.py (2 sec)

**Text overlay:**
```
✓ Docker deployment
✓ Real-time monitoring
✓ PCAP forensics
✓ Physics-based simulation
```

**Voiceover:** "Complete with Docker deployment, real-time monitoring, packet capture, and physics-based consequences."

---

## Scene 6: Call to Action (3 seconds)
**Text on screen:**
```
github.com/Taimaishu/Vuln-PLC

⭐ Free & Open Source
📚 400+ Pages Documentation
🐳 One-Command Setup

Start Learning ICS Security Today
```

**Voiceover:** "Free, open-source, and ready to deploy. Start your ICS security journey today."

---

## Recording Notes

### Setup Before Recording:
```bash
# Start all services
./start_all.sh

# Wait 10 seconds for everything to initialize

# Open browser to HMI
http://localhost:8000

# Open terminal for Modbus commands
# Have commands ready to paste
```

### Tools Needed:
- **Screen recorder:** OBS Studio (free) or QuickTime (Mac)
- **Video editor:** DaVinci Resolve (free) or iMovie
- **Screen resolution:** 1920x1080 (Full HD)
- **Frame rate:** 30 FPS minimum

### Recording Tips:
1. **Clear your desktop** - close unnecessary windows
2. **Zoom in on HMI** - make gauges clearly visible
3. **Use smooth mouse movements** - no shaky cursor
4. **Record terminal separately** - easier to time with voiceover
5. **Capture alarm moment** - slow down for impact (can edit in post)

### Post-Production:
1. Speed up tank filling initially (time-lapse)
2. Slow down overflow moment for dramatic effect
3. Add subtle background music (industrial/tech theme)
4. Add sound effects for alarms (optional)
5. Fade between scenes
6. Add text overlays with fade-in/out

### Audio:
- Record voiceover separately with good microphone
- Remove background noise
- Normalize audio levels
- Add slight compression

### Export Settings:
- **Format:** MP4 (H.264)
- **Resolution:** 1920x1080
- **Bitrate:** 5-8 Mbps
- **Audio:** AAC, 192 kbps
- **Target size:** <20 MB for easy sharing

---

## Alternative: GIF Version (for README)

For a quick animated GIF:
1. Record just Scene 4 (tank overflow)
2. 10-15 seconds maximum
3. Convert to GIF with high quality
4. Optimize to <5 MB
5. Embed in README.md

**Command to create GIF:**
```bash
# Using ffmpeg
ffmpeg -i demo_video.mp4 -ss 00:00:15 -t 00:00:12 \
  -vf "fps=10,scale=800:-1:flags=lanczos" \
  -gifflags +transdiff -y demo.gif

# Optimize
gifsicle -O3 --lossy=80 demo.gif -o demo_optimized.gif
```

---

## YouTube Description Template

```
🏭 Vuln-PLC: The Complete ICS/SCADA Security Training Platform

This is Vuln-PLC v2.0 - a comprehensive, intentionally vulnerable industrial control system environment for security training, penetration testing, and ICS/SCADA research.

🎯 What You're Seeing:
- Real-time SCADA HMI interface
- Modbus TCP attack causing tank overflow
- Emergency shutdown system activation
- Live process visualization

✨ Features:
✓ 4 PLCs with real vulnerabilities
✓ Modbus + S7 protocol support
✓ Visual HMI with P&ID diagrams
✓ Physics-based process simulation
✓ Modbus IDS with PCAP capture
✓ Docker deployment (one command!)
✓ 400+ pages documentation

🚀 Get Started:
GitHub: https://github.com/Taimaishu/Vuln-PLC
Documentation: See README.md

⚠️ Educational Use Only
For authorized security testing and training in isolated environments.

#ICS #SCADA #CyberSecurity #ICSsecurity #PenetrationTesting #HMI #Modbus #IndustrialSecurity #RedTeam #BlueTeam #SecurityTraining
```

---

## Social Media Versions

### Twitter/X (280 chars):
```
🚨 Just released Vuln-PLC v2.0 - the most complete free ICS/SCADA training platform!

✅ Visual HMI
✅ Real consequences
✅ PCAP forensics
✅ Docker deployment

Watch a Modbus attack cause real-time tank overflow 👇

[VIDEO]

#ICSsecurity #SCADA
```

### LinkedIn:
```
Excited to share Vuln-PLC v2.0 - A Comprehensive ICS/SCADA Security Training Platform

After months of development, I'm releasing what may be the most complete open-source ICS security training environment available.

🎯 What's New in v2.0:
• Visual SCADA HMI with real-time process data
• Physics-based industrial process simulation
• Modbus IDS with packet capture
• Complete Docker deployment
• 400+ pages of documentation

This video demonstrates a Modbus TCP attack causing tank overflow, triggering emergency shutdowns - exactly how real ICS attacks unfold.

Perfect for:
🔹 Security researchers
🔹 ICS penetration testers
🔹 Blue team defenders
🔹 Educators and students
🔹 CTF challenge creators

100% free and open source. Link in comments.

#CyberSecurity #ICS #SCADA #IndustrialSecurity #PenetrationTesting
```

---

## Reddit Post Title & Body

**Title:**
```
[Tool Release] Vuln-PLC v2.0: Complete ICS/SCADA Security Training Platform with Visual HMI
```

**Body:**
```markdown
Hey r/netsec,

I've been working on a comprehensive ICS/SCADA security training environment and just released v2.0 with some major enhancements.

## What is Vuln-PLC?

An intentionally vulnerable industrial control system environment featuring:
- 4 PLCs with realistic vulnerabilities (SQL injection, command injection, Modbus manipulation)
- Visual SCADA HMI with P&ID diagrams
- Physics-based process simulation (tank levels, pressure, temperature)
- Modbus IDS with packet capture
- Complete Docker deployment

## What's New in v2.0?

The big addition is a **visual HMI interface** that shows attacks happening in real-time. In the demo video, you can see:
1. Normal operation with tank at 50%
2. Modbus attack forces pump on + valve closed
3. Tank overflows (with color changes red)
4. Emergency alarms cascade
5. Safety system activates

## Why This Matters

Most ICS training tools are command-line only. This gives you **visual feedback** - you can actually *see* what happens when you override safety controls. Perfect for:
- Demos and presentations
- Training non-technical stakeholders
- Understanding attack consequences
- Blue team defense practice

## Tech Stack

- Python 3.9 + Flask
- PyModbus for protocol simulation
- Scapy for packet capture
- Docker for easy deployment
- 400+ pages of documentation

## Get Started

```bash
git clone https://github.com/Taimaishu/Vuln-PLC
cd vulnerable_plc
docker-compose up -d
# Open http://localhost:8000 for HMI
```

Full documentation and attack scenarios included.

**Demo Video:** [YouTube link]

**GitHub:** https://github.com/Taimaishu/Vuln-PLC

⚠️ **Warning:** Intentionally vulnerable. Only use in isolated lab environments.

Happy hacking! Questions and feedback welcome.
```

---

*Last Updated: 2024-12-07*
