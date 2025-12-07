# Screenshot Gallery Guide

This guide helps you capture and organize screenshots for GitHub, documentation, and promotional materials.

## Priority Screenshots Needed

### 1. HMI Dashboard - Normal Operations ⭐⭐⭐
**Filename:** `hmi_dashboard.png`
**What to show:**
- Full HMI interface at 1920x1080
- Tank at 50%, green color
- Pressure at 80 PSI
- Temperature at 20°C
- All indicators showing normal (green)
- "No active alarms" in alarm panel
- Clean, professional look

**How to capture:**
```bash
./start_all.sh
# Wait 30 seconds
# Open http://localhost:8000
# Wait for data to stabilize
# Take screenshot
```

---

### 2. HMI - Tank Overflow Attack ⭐⭐⭐
**Filename:** `hmi_tank_overflow.png`
**What to show:**
- Tank at 100%, RED color
- "TANK OVERFLOW" alarm visible
- Emergency banner showing
- Multiple alarms in panel
- System status RED

**How to capture:**
```bash
# With HMI open at http://localhost:8000
sudo modbus 127.0.0.1:5502 write 0 1    # Pump ON
sudo modbus 127.0.0.1:5502 write 1 0    # Valve CLOSED
# Wait 30 seconds for tank to fill
# Take screenshot when tank hits 100%
```

---

### 3. System Monitor Dashboard ⭐⭐
**Filename:** `system_monitor.png`
**What to show:**
- Console dashboard from system_monitor.py
- All PLC engines running
- IDS statistics
- Network traffic metrics
- Security status: NORMAL

**How to capture:**
```bash
python3 system_monitor.py
# Wait for first update cycle
# Take terminal screenshot
```

---

### 4. Modbus IDS Alerts ⭐⭐
**Filename:** `ids_alerts.png`
**What to show:**
- Terminal showing IDS alerts
- Various severity levels
- Alert types (UNAUTHORIZED_WRITE, RATE_LIMIT, etc.)
- Timestamps

**How to capture:**
```bash
python3 modbus_ids.py &
# Generate attacks
for i in {1..100}; do sudo modbus 127.0.0.1:5502 read $i 1; done
sudo modbus 127.0.0.1:5502 write 10 9999
# Take screenshot of alerts
```

---

### 5. PCAP in Wireshark ⭐⭐
**Filename:** `wireshark_pcap.png`
**What to show:**
- Wireshark with captured Modbus traffic
- Filter: `modbus` applied
- Packet list showing function codes
- Packet details expanded
- Highlighted suspicious write command

**How to capture:**
```bash
# Run attacks with IDS capturing
docker-compose --profile full up -d
# Generate traffic
sleep 60
# Copy PCAP
docker cp vuln-modbus-ids:/app/pcaps/modbus_*.pcap ./
# Open in Wireshark
wireshark modbus_*.pcap
# Apply filter, expand packet, screenshot
```

---

### 6. Docker Deployment ⭐
**Filename:** `docker_compose.png`
**What to show:**
- Terminal with `docker-compose ps` output
- All 8 services running
- Status showing "Up"
- Port mappings visible

**How to capture:**
```bash
docker-compose --profile full up -d
docker-compose ps
# Take terminal screenshot
```

---

### 7. Attack Terminal Commands ⭐
**Filename:** `attack_commands.png`
**What to show:**
- Terminal with various attack commands
- Modbus writes
- SQL injection
- S7 commands
- Color-coded syntax

**How to capture:**
```bash
# In nice terminal (iTerm2/Hyper with theme)
# Show command history or execute live
sudo modbus 127.0.0.1:5502 write 10 9999
curl -X POST http://localhost:5000/login -d "username=admin' OR '1'='1..."
python3 -c "import snap7; ..."
```

---

### 8. HMI - Multiple Alarms ⭐
**Filename:** `hmi_multiple_alarms.png`
**What to show:**
- Several alarms in the alarm panel
- Different severity levels (Critical, High, Medium)
- Tank overflow
- High pressure
- Thermal runaway

**How to capture:**
```bash
# Trigger multiple issues simultaneously
sudo modbus 127.0.0.1:5502 write 0 1    # Tank pump on
sudo modbus 127.0.0.1:5502 write 1 0    # Valve closed
sudo modbus 127.0.0.1:5503 write 0 1    # Compressor on
sudo modbus 127.0.0.1:5503 write 1 0    # Relief closed
sudo modbus 127.0.0.1:5504 write 0 1    # Heater on
sudo modbus 127.0.0.1:5504 write 1 0    # Cooling off
# Wait for cascading alarms
```

---

### 9. Physical Process Simulation ⭐
**Filename:** `physical_process.png`
**What to show:**
- Terminal output from physical_process.py
- Real-time process values updating
- Alarm messages appearing

**How to capture:**
```bash
python3 physical_process.py
# Let it run for 30 seconds
# Take screenshot showing live updates
```

---

### 10. Architecture Diagram
**Filename:** `architecture.png`
**What to show:**
- Network diagram from ARCHITECTURE.md
- OT Network + DMZ
- All components labeled
- IP addresses visible

**How to create:**
- Use draw.io, Lucidchart, or similar
- Or render markdown diagram
- Export as high-res PNG

---

## Screenshot Requirements

### Technical Specs:
- **Resolution:** 1920x1080 (Full HD) minimum
- **Format:** PNG (lossless)
- **File size:** <2 MB each
- **DPI:** 72 for web, 300 for print

### Aesthetic:
- **Clean interface:** Close unnecessary windows
- **Good contrast:** Dark theme preferred
- **Readable text:** Zoom if needed
- **Professional:** No personal info visible

### Tools:
**macOS:**
- Cmd+Shift+4 (selection)
- Cmd+Shift+5 (options)
- Preview for editing

**Linux:**
- Flameshot (recommended)
- GNOME Screenshot
- Shutter

**Windows:**
- Snip & Sketch (Win+Shift+S)
- Greenshot
- ShareX

---

## Screenshot Editing

### Crop & Resize:
```bash
# Using ImageMagick
convert input.png -resize 1920x1080 -quality 95 output.png

# Crop to specific area
convert input.png -crop 1920x1080+0+0 output.png
```

### Annotate:
Add arrows, boxes, text to highlight important features:
- Use GIMP, Photoshop, or Pixelmator
- Red arrows for critical items
- Yellow boxes for important areas
- Add callout text if needed

### Optimize:
```bash
# Reduce file size without quality loss
pngcrush -brute input.png output.png

# Or use online tools
# - TinyPNG.com
# - Squoosh.app
```

---

## Organization

### Directory Structure:
```
screenshots/
├── hmi_dashboard.png
├── hmi_tank_overflow.png
├── hmi_multiple_alarms.png
├── system_monitor.png
├── ids_alerts.png
├── wireshark_pcap.png
├── docker_compose.png
├── attack_commands.png
├── physical_process.png
└── architecture.png
```

### GitHub Usage:

**In README.md:**
```markdown
## Screenshots

### HMI Interface
![HMI Dashboard](screenshots/hmi_dashboard.png)

### Tank Overflow Attack
![Tank Overflow](screenshots/hmi_tank_overflow.png)
```

**In Issues/PRs:**
```markdown
![Description](https://raw.githubusercontent.com/Taimaishu/Vuln-PLC/main/screenshots/image.png)
```

---

## Quick Capture Script

Save this as `capture_screenshots.sh`:

```bash
#!/bin/bash
# Screenshot capture automation

mkdir -p screenshots

echo "Starting services..."
./start_all.sh
sleep 30

echo "1. Capture normal HMI..."
open http://localhost:8000
echo "Press ENTER after capturing screenshot 1..."
read

echo "2. Triggering tank overflow..."
sudo modbus 127.0.0.1:5502 write 0 1
sudo modbus 127.0.0.1:5502 write 1 0
sleep 30
echo "Press ENTER after capturing screenshot 2..."
read

echo "3. Opening system monitor..."
# Open in new terminal
osascript -e 'tell app "Terminal" to do script "cd $(pwd) && python3 system_monitor.py"'
sleep 5
echo "Press ENTER after capturing screenshot 3..."
read

echo "Done! Check screenshots/ directory"
```

---

## GIF Creation

For animated demos in README:

### Using ffmpeg:
```bash
# Convert video to GIF
ffmpeg -i demo_video.mp4 -vf "fps=10,scale=800:-1:flags=lanczos" \
  -gifflags +transdiff -y demo.gif

# Optimize
gifsicle -O3 --lossy=80 demo.gif -o demo_optimized.gif
```

### Using Screentogifor similar:
1. Record screen (10-15 seconds max)
2. Export as GIF
3. Optimize to <5 MB

### What to show in GIFs:
- Tank level rising to overflow
- Alarm panel updating
- Gauge changing colors
- Emergency banner appearing

---

## Usage in Documentation

### README.md:
Place 2-3 key screenshots prominently:
- HMI dashboard (top of features section)
- Tank overflow (in demo section)
- Architecture diagram (in architecture section)

### BLOG_POST.md:
Embed screenshots throughout:
- Before/after comparisons
- Step-by-step attack progression
- Feature highlights

### Social Media:
Create collages:
- 4-panel grid showing attack progression
- Before/after split screen
- Animated GIF for Twitter/LinkedIn

---

## Example Screenshot Captions

```markdown
**Figure 1:** Normal operations on the SCADA HMI showing tank at 50%, all systems green.

**Figure 2:** Tank overflow triggered by Modbus attack. Note the cascading alarms and emergency shutdown activation.

**Figure 3:** System Monitor dashboard displaying real-time metrics for all 4 PLCs, IDS statistics, and network traffic.

**Figure 4:** Modbus IDS detecting unauthorized write attempts with varying severity levels.

**Figure 5:** Wireshark analysis of captured Modbus traffic showing function code 6 (Write Single Register) commands.
```

---

## Checklist

Before publishing:
- [ ] All 10 priority screenshots captured
- [ ] Images cropped and optimized
- [ ] Files named consistently
- [ ] Organized in screenshots/ directory
- [ ] Added to README.md
- [ ] Added to BLOG_POST.md
- [ ] Tested links work
- [ ] Total size reasonable (<15 MB)
- [ ] No sensitive information visible
- [ ] Professional appearance

---

## Tips

1. **Consistency:** Use same terminal theme for all screenshots
2. **Timing:** Capture at interesting moments (tank at 95%, not 0%)
3. **Context:** Show enough UI to understand what's happening
4. **Quality:** Better to retake than use blurry screenshot
5. **Variety:** Mix terminals, browsers, tools for visual interest

---

*Last Updated: 2024-12-07*
