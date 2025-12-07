# Installation and Setup Guide

## Quick Installation

```bash
cd vulnerable_plc
./install.sh
```

That's it! The script will:
- ✓ Install to `~/.local/share/vulnerable_plc`
- ✓ Create `vuln-plc` command in `~/.local/bin`
- ✓ Add to your PATH
- ✓ Create desktop launcher icon
- ✓ Install Python dependencies

## Usage After Installation

### Command Line

```bash
# Start the simulator
vuln-plc start

# Stop the simulator
vuln-plc stop

# Check status
vuln-plc status

# Run tests
vuln-plc test

# Clean database
vuln-plc clean

# Uninstall
vuln-plc uninstall
```

### Desktop Icon

Just double-click the **"Vulnerable PLC Simulator"** icon on your desktop!

## Access

**Web Interface:** http://localhost:5000
**Modbus TCP:** localhost:5502

**Default Credentials:**
- `admin` / `admin` - Full admin access
- `operator` / `operator123` - Process control access
- `guest` / `guest` - Read-only access

## Features by Role

### Guest (Read-Only)
- ✓ View all dashboards
- ✓ View HMI, SCADA, process status
- ✓ View alarms and trends
- ✓ Read PLC registers
- ✗ **Cannot control anything**

### Operator
- ✓ All guest permissions
- ✓ Control equipment (pump, valve, motor)
- ✓ Write to PLC registers
- ✓ Acknowledge alarms
- ✓ View logs
- ✗ **Cannot access admin panel**

### Admin
- ✓ All operator permissions
- ✓ Access admin panel
- ✓ Execute system commands
- ✓ Manage users
- ✓ Full system access

## Privilege Escalation Practice

As a guest user, you **cannot** control the system. This is intentional for practicing privilege escalation!

See **PRIVILEGE_ESCALATION.md** for:
- 10+ escalation paths
- Step-by-step guides
- Practice scenarios
- Detection tips
- Mitigation exercises

## Pentest Scenarios

### Scenario 1: Guest Reconnaissance
```bash
# Login as guest
curl -X POST http://localhost:5000/login \
  -d "username=guest&password=guest" \
  -c cookies.txt

# What can you discover?
# What endpoints are accessible?
# What information is leaked?
```

### Scenario 2: Escalate to Operator
```bash
# Can you gain control access?
# Try SQL injection, session manipulation, etc.
```

### Scenario 3: Gain Admin Shell
```bash
# Ultimate goal: Execute commands
# Requires admin privileges
```

## Testing Tools

### Port Scanning
```bash
nmap -sV -p 5000,5502 localhost
nmap --script modbus-discover -p 5502 localhost
```

### SQL Injection
```bash
sqlmap -u "http://localhost:5000/login" \
  --data "username=admin&password=admin" \
  --method POST --level=5 --risk=3
```

### Modbus Testing
```bash
sudo modbus 127.0.0.1:5502 read 0 10
sudo modbus 127.0.0.1:5502 write 0 1234
```

### Metasploit
```bash
msfconsole
use auxiliary/scanner/scada/modbusdetect
set RHOSTS localhost
set RPORT 5502
run
```

## Troubleshooting

### Command not found
```bash
# Restart your terminal or run:
source ~/.bashrc
```

### Port already in use
```bash
vuln-plc stop
# Or manually kill:
pkill -f "python.*app.py"
```

### Desktop icon not working
```bash
# Make it executable:
chmod +x ~/Desktop/vuln-plc.desktop

# Trust it (Ubuntu/GNOME):
gio set ~/Desktop/vuln-plc.desktop metadata::trusted true
```

### Reset everything
```bash
vuln-plc stop
vuln-plc clean
vuln-plc start
```

## Uninstall

```bash
vuln-plc uninstall
```

This removes:
- Application files
- Command launcher
- Desktop icon
- PATH entries (need to remove manually from ~/.bashrc)

## Advanced Usage

### Run web server only
```bash
vuln-plc web
```

### Run Modbus server only
```bash
vuln-plc modbus
```

### Background operation
```bash
vuln-plc start &
```

### Custom port (modify app.py)
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```

## Security Notes

**DO NOT:**
- ✗ Expose to internet
- ✗ Use on production networks
- ✗ Test against unauthorized systems
- ✗ Use real passwords that you use elsewhere

**DO:**
- ✓ Use in isolated lab environment
- ✓ Practice ethical hacking
- ✓ Learn to defend systems
- ✓ Document your findings

## Files and Directories

After installation:
```
~/.local/share/vulnerable_plc/    # Application files
~/.local/bin/vuln-plc             # Command launcher
~/.local/share/applications/      # Desktop file
~/Desktop/vuln-plc.desktop        # Desktop shortcut
```

## Support

This is a training tool for educational purposes. For issues:
1. Check PRIVILEGE_ESCALATION.md
2. Check README.md
3. Review logs in installation directory
4. Try `vuln-plc clean` and restart

## What's Next?

1. **Read PRIVILEGE_ESCALATION.md** - Learn all the escalation paths
2. **Practice as guest** - Try to gain control
3. **Use pentesting tools** - Nmap, Metasploit, SQLMap
4. **Learn to defend** - Fix the vulnerabilities
5. **Document findings** - Write a pentest report

Happy hacking! 🔐
