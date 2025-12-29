#!/usr/bin/env python3
"""
Generate 50 attacks across all 4 PLCs to test filtering system
"""
import socket
import struct
import time
import random

def modbus_attack(port, coil, value, desc):
    """Execute a Modbus write attack"""
    try:
        sock = socket.socket()
        sock.settimeout(2)
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
║  Generating 50 Attacks to Test Filtering System             ║
╚══════════════════════════════════════════════════════════════╝
''')

attacks = [
    # PLC-1 attacks (Tank) - Mix of CRITICAL and WARNING
    {'plc': 'PLC-1', 'port': 5502, 'coil': 0, 'value': True, 'desc': 'Pump ON', 'severity': 'CRITICAL'},
    {'plc': 'PLC-1', 'port': 5502, 'coil': 3, 'value': False, 'desc': 'Valve closed', 'severity': 'WARNING'},
    {'plc': 'PLC-1', 'port': 5502, 'coil': 0, 'value': False, 'desc': 'Pump OFF', 'severity': 'CRITICAL'},
    {'plc': 'PLC-1', 'port': 5502, 'coil': 3, 'value': True, 'desc': 'Valve open', 'severity': 'WARNING'},

    # PLC-2 attacks (Pressure) - Mostly CRITICAL
    {'plc': 'PLC-2', 'port': 5503, 'coil': 0, 'value': True, 'desc': 'Compressor ON', 'severity': 'CRITICAL'},
    {'plc': 'PLC-2', 'port': 5503, 'coil': 4, 'value': False, 'desc': 'Relief valve closed', 'severity': 'CRITICAL'},
    {'plc': 'PLC-2', 'port': 5503, 'coil': 0, 'value': False, 'desc': 'Compressor OFF', 'severity': 'CRITICAL'},
    {'plc': 'PLC-2', 'port': 5503, 'coil': 4, 'value': True, 'desc': 'Relief valve open', 'severity': 'CRITICAL'},
    {'plc': 'PLC-2', 'port': 5503, 'coil': 5, 'value': True, 'desc': 'Pressure sensor', 'severity': 'WARNING'},

    # PLC-3 attacks (Temperature) - Mix
    {'plc': 'PLC-3', 'port': 5504, 'coil': 0, 'value': True, 'desc': 'Heater ON', 'severity': 'CRITICAL'},
    {'plc': 'PLC-3', 'port': 5504, 'coil': 2, 'value': False, 'desc': 'Cooler OFF', 'severity': 'CRITICAL'},
    {'plc': 'PLC-3', 'port': 5504, 'coil': 0, 'value': False, 'desc': 'Heater OFF', 'severity': 'CRITICAL'},
    {'plc': 'PLC-3', 'port': 5504, 'coil': 2, 'value': True, 'desc': 'Cooler ON', 'severity': 'CRITICAL'},
    {'plc': 'PLC-3', 'port': 5504, 'coil': 5, 'value': True, 'desc': 'Temp sensor', 'severity': 'WARNING'},

    # PLC-4 attacks (Safety) - ALL CRITICAL
    {'plc': 'PLC-4', 'port': 5505, 'coil': 0, 'value': False, 'desc': 'E-stop disabled', 'severity': 'CRITICAL'},
    {'plc': 'PLC-4', 'port': 5505, 'coil': 1, 'value': False, 'desc': 'Interlock disabled', 'severity': 'CRITICAL'},
    {'plc': 'PLC-4', 'port': 5505, 'coil': 0, 'value': True, 'desc': 'E-stop enabled', 'severity': 'CRITICAL'},
    {'plc': 'PLC-4', 'port': 5505, 'coil': 1, 'value': True, 'desc': 'Interlock enabled', 'severity': 'CRITICAL'},
]

# Repeat attacks to reach 50 total
attack_list = []
for i in range(3):
    attack_list.extend(attacks)

# Add a few more to reach exactly 50
attack_list.extend(attacks[:2])

print(f'Executing {len(attack_list)} attacks across all 4 PLCs...\n')

success_count = 0
plc_counts = {'PLC-1': 0, 'PLC-2': 0, 'PLC-3': 0, 'PLC-4': 0}
severity_counts = {'CRITICAL': 0, 'WARNING': 0}

for i, attack in enumerate(attack_list, 1):
    severity_icon = '🚨🚨' if attack['severity'] == 'CRITICAL' else '⚠️ '
    print(f"[{i}/50] {severity_icon} {attack['plc']}: {attack['desc']}", end=' ')

    success = modbus_attack(attack['port'], attack['coil'], attack['value'], attack['desc'])

    if success:
        print('✓')
        success_count += 1
        plc_counts[attack['plc']] += 1
        severity_counts[attack['severity']] += 1
    else:
        print('✗')

    # Small delay to avoid overwhelming the system
    time.sleep(0.1)

print('\n' + '='*70)
print('ATTACK SUMMARY:')
print('='*70)
print(f'Total attacks executed: {success_count}/50')
print()
print('Attacks by PLC:')
for plc, count in sorted(plc_counts.items()):
    print(f'  {plc}: {count} attacks')
print()
print('Attacks by Severity:')
for sev, count in sorted(severity_counts.items()):
    icon = '🚨' if sev == 'CRITICAL' else '⚠️'
    print(f'  {icon} {sev}: {count} attacks')
print()
print('='*70)
print()

print('''
╔══════════════════════════════════════════════════════════════╗
║  Testing Alert Filtering                                     ║
╚══════════════════════════════════════════════════════════════╝

Open: http://localhost:5000/process (admin/admin)

Now test these filter combinations:

1. Filter by PLC-4 only:
   → Uncheck PLC-1, PLC-2, PLC-3
   → Should show ~16 PLC-4 alerts
   → All should be CRITICAL

2. Filter by CRITICAL only:
   → Uncheck WARNING
   → Should show ~42 CRITICAL alerts

3. Filter by WARNING only:
   → Uncheck CRITICAL
   → Should show ~8 WARNING alerts

4. Filter PLC-1 + WARNING:
   → Check only PLC-1 and WARNING
   → Should show ~4 PLC-1 WARNING alerts

5. Export filtered data:
   → Set filters, click "Export to CSV"
   → Verify CSV contains only filtered alerts

6. Clear filters:
   → Click "Clear Filters"
   → Should show all ~50 alerts

Alert count should update in real-time!
''')
