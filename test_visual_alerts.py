#!/usr/bin/env python3
"""
Test script to verify visual security alerts are working
"""
import socket
import struct
import time
import requests

print("""
╔══════════════════════════════════════════════════════════════╗
║         Testing Visual Security Alert System                 ║
╚══════════════════════════════════════════════════════════════╝
""")

def modbus_attack(port, coil, value, description):
    """Execute a Modbus attack"""
    try:
        sock = socket.socket()
        sock.settimeout(3)
        sock.connect(('127.0.0.1', port))

        # Write Single Coil
        coil_value = 0xFF00 if value else 0x0000
        request = struct.pack('>HHHB', 1, 0, 6, 1) + struct.pack('>BHH', 0x05, coil, coil_value)
        sock.send(request)
        response = sock.recv(1024)
        sock.close()

        return True
    except Exception as e:
        print(f"✗ Attack failed: {e}")
        return False

# Test 1: Check if alert API is accessible
print("\n[Test 1] Checking alert API endpoint...")
try:
    response = requests.get('http://127.0.0.1:5000/api/security/alerts', timeout=3)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Alert API is accessible")
        print(f"  Current alerts: {data.get('total', 0)}")
    else:
        print(f"✗ Alert API returned status {response.status_code}")
except Exception as e:
    print(f"✗ Cannot access alert API: {e}")
    print("  Make sure containers are running!")
    exit(1)

# Test 2: Execute attacks and check if alerts are generated
print("\n[Test 2] Executing attacks to trigger alerts...")

attacks = [
    {'port': 5502, 'coil': 0, 'value': True, 'desc': 'Turn pump ON'},
    {'port': 5502, 'coil': 3, 'value': False, 'desc': 'Close valve'},
    {'port': 5505, 'coil': 0, 'value': False, 'desc': 'Disable emergency stop (CRITICAL!)'},
]

for i, attack in enumerate(attacks, 1):
    print(f"\n  [{i}/3] {attack['desc']}...")
    success = modbus_attack(attack['port'], attack['coil'], attack['value'], attack['desc'])
    if success:
        print(f"       ✓ Attack executed")
    time.sleep(1)

# Test 3: Check if alerts were generated
print("\n[Test 3] Checking if alerts were generated...")
time.sleep(2)  # Wait for alerts to be processed

try:
    response = requests.get('http://127.0.0.1:5000/api/security/alerts', timeout=3)
    data = response.json()

    if data['success'] and len(data['alerts']) > 0:
        print(f"✓ {len(data['alerts'])} alerts generated!")

        print("\n  Recent alerts:")
        for alert in data['alerts'][-3:]:
            severity_icon = {
                'CRITICAL': '🚨🚨',
                'HIGH': '⚠️ ',
                'WARNING': '⚠️ '
            }.get(alert['severity'], '  ')

            print(f"  {severity_icon} [{alert['timestamp']}] {alert['severity']}: {alert['message']}")

    else:
        print("✗ No alerts generated")
        print("  This might mean attack detection is not working")

except Exception as e:
    print(f"✗ Error checking alerts: {e}")

# Test 4: Instructions for visual verification
print("\n" + "="*70)
print("  VISUAL VERIFICATION")
print("="*70)
print("""
1. Open browser to: http://localhost:5000/process
2. Login with: admin / admin
3. You should see:

   ┌─────────────────────────────────────────────────────────────┐
   │ 🚨 SAFETY SYSTEM TAMPER                                     │
   │ [12:34:56] 🚨 CRITICAL: Safety system tampered!            │
   │ Write to coil 0 from 127.0.0.1                             │
   │                                                        [×]  │
   └─────────────────────────────────────────────────────────────┘

   Below the banner, you'll see "Recent Security Events" with a list
   of all detected attacks!

4. The alert banner features:
   - 🚨 Animated icon (bouncing)
   - Red pulsing background for CRITICAL alerts
   - Orange background for WARNING/HIGH alerts
   - Smooth slide-down animation
   - Dismissable with [×] button
   - Alert history showing last 5 events

5. Try running more attacks:
   sudo modbus write-coil 127.0.0.1:5502 0 1

   You'll see a new alert pop up in real-time!

6. To clear alerts:
   POST to http://localhost:5000/api/security/alerts/clear

""")

print("="*70)
print("  Test complete! Check the web UI to see visual alerts.")
print("="*70)
