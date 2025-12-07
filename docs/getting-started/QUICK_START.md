# Quick Start Guide

## Fastest Way to Start

```bash
cd vulnerable_plc
python start.py
```

Then open: **http://localhost:5000**

Login with: **admin / admin**

---

## With Docker

```bash
cd vulnerable_plc
docker-compose up
```

---

## Test Immediately

### Web Interface
1. Open http://localhost:5000
2. Login: admin / admin
3. Click "Admin Panel" > "System Control"
4. Try command: `whoami`

### SQL Injection
1. Logout
2. Login with:
   - Username: `admin' OR '1'='1`
   - Password: `anything`
3. You're in!

### Modbus Testing

```bash
# Install modbus-cli
pip install modbus-cli

# Read registers
sudo modbus 127.0.0.1:5502 read 0 10

# Write register
sudo modbus 127.0.0.1:5502 write 0 1234
```

### Port Scan

```bash
nmap -sV -p 5000,5502 localhost
```

---

## Default Credentials

- admin / admin
- operator / operator123
- guest / guest

---

## Ports

- **5000** - Web Interface
- **5502** - Modbus TCP

---

See **README.md** for detailed testing guide!
