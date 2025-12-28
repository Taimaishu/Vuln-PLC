#!/usr/bin/env python3
"""Quick test to check if Modbus server is responding"""
import socket
import struct
import sys

def test_connection(port=5555):
    """Test if port is accepting connections"""
    print(f"[TEST 1] Checking if port {port} is open...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', port))
        sock.close()

        if result == 0:
            print(f"  ✓ Port {port} is OPEN and accepting connections")
            return True
        else:
            print(f"  ✗ Port {port} is CLOSED")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_modbus_read(port=5555):
    """Test reading Modbus holding registers"""
    print("\n[TEST 2] Sending Modbus Read Holding Registers request...")
    try:
        # Connect to Modbus server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('localhost', port))
        print(f"  ✓ Connected to localhost:{port}")

        # Build Modbus TCP request
        # MBAP Header: Trans ID=1, Proto ID=0, Length=6, Unit ID=1
        # PDU: Function Code 0x03, Start Address=0, Count=5
        transaction_id = 0x0001
        protocol_id = 0x0000
        unit_id = 0x01

        # PDU: Read 5 registers starting at address 0
        pdu = struct.pack('>BHH', 0x03, 0x0000, 5)
        length = len(pdu) + 1  # +1 for unit_id

        # Complete request
        request = struct.pack('>HHHB', transaction_id, protocol_id, length, unit_id) + pdu

        print(f"  → Request (hex): {request.hex()}")
        print(f"  → Request breakdown:")
        print(f"     Transaction ID: {transaction_id}")
        print(f"     Protocol ID: {protocol_id}")
        print(f"     Length: {length}")
        print(f"     Unit ID: {unit_id}")
        print(f"     Function Code: 0x03 (Read Holding Registers)")
        print(f"     Start Address: 0")
        print(f"     Count: 5 registers")

        # Send request
        sock.send(request)
        print("  ✓ Request sent")

        # Read response
        response = sock.recv(1024)
        print(f"  ← Response (hex): {response.hex()}")
        print(f"  ← Response length: {len(response)} bytes")

        if len(response) < 9:
            print("  ✗ Response too short - not valid Modbus")
            sock.close()
            return False

        # Parse response header
        resp_trans_id, resp_proto_id, resp_length, resp_unit_id = struct.unpack('>HHHB', response[:7])
        function_code = response[7]

        print(f"  ← Response breakdown:")
        print(f"     Transaction ID: {resp_trans_id}")
        print(f"     Protocol ID: {resp_proto_id}")
        print(f"     Length: {resp_length}")
        print(f"     Unit ID: {resp_unit_id}")
        print(f"     Function Code: {function_code:#04x}")

        if function_code == 0x03:
            # Valid read response
            byte_count = response[8]
            print(f"     Byte Count: {byte_count}")

            # Parse register values
            values = []
            for i in range(byte_count // 2):
                offset = 9 + (i * 2)
                value = struct.unpack('>H', response[offset:offset+2])[0]
                values.append(value)

            print(f"     Register Values: {values}")
            print(f"     Decoded values:")
            print(f"       Register 0 (tank1_level): {values[0] / 10.0}%")
            print(f"       Register 1 (tank1_temp): {values[1] / 10.0}°C")
            print(f"       Register 2 (tank1_pressure): {values[2] / 10.0} kPa")
            print(f"       Register 3 (tank2_level): {values[3] / 10.0}%")
            print(f"       Register 4 (tank2_temp): {values[4] / 10.0}°C")

            print("\n  ✓ SUCCESS! Modbus server is responding correctly!")
            sock.close()
            return True
        else:
            print(f"  ✗ Unexpected function code: {function_code:#04x}")
            sock.close()
            return False

    except socket.timeout:
        print("  ✗ Timeout - server not responding")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_modbus_write(port=5555):
    """Test writing a Modbus register"""
    print("\n[TEST 3] Sending Modbus Write Single Register request...")
    try:
        # Connect to Modbus server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('localhost', port))

        # Build Modbus TCP write request
        transaction_id = 0x0002
        protocol_id = 0x0000
        unit_id = 0x01

        # PDU: Function Code 0x06, Address=0, Value=750 (75.0%)
        pdu = struct.pack('>BHH', 0x06, 0x0000, 750)
        length = len(pdu) + 1

        # Complete request
        request = struct.pack('>HHHB', transaction_id, protocol_id, length, unit_id) + pdu

        print(f"  → Request (hex): {request.hex()}")
        print(f"     Function Code: 0x06 (Write Single Register)")
        print(f"     Address: 0 (tank1_level)")
        print(f"     Value: 750 (75.0%)")

        # Send request
        sock.send(request)

        # Read response
        response = sock.recv(1024)
        print(f"  ← Response (hex): {response.hex()}")

        function_code = response[7]
        if function_code == 0x06:
            addr, value = struct.unpack('>HH', response[8:12])
            print(f"     Address echoed: {addr}")
            print(f"     Value echoed: {value}")
            print("\n  ✓ SUCCESS! Write register works!")
            sock.close()
            return True
        else:
            print(f"  ✗ Unexpected function code: {function_code:#04x}")
            sock.close()
            return False

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

if __name__ == '__main__':
    # Allow specifying port as command line argument
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5555

    print("=" * 70)
    print("  MODBUS TCP SERVER TEST")
    print(f"  Testing port: {port}")
    print("=" * 70)

    # Test 1: Connection
    if not test_connection(port):
        print(f"\n❌ Port {port} is not open. Start the server first:")
        if port == 5555:
            print("   python3 standalone_modbus.py")
        else:
            print("   python3 core/app.py")
        sys.exit(1)

    # Test 2: Read registers
    if not test_modbus_read(port):
        print("\n❌ Modbus read failed - server might not be implementing the protocol")
        sys.exit(1)

    # Test 3: Write register
    if not test_modbus_write(port):
        print("\n❌ Modbus write failed")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("  ✅ ALL TESTS PASSED!")
    print("  The Modbus TCP server is working correctly!")
    print("=" * 70)
    print("\nYou can now use real Modbus tools:")
    print(f"  • modbus-cli: modbus read localhost:{port} 0 10")
    print("  • pymodbus: See MODBUS_IMPLEMENTATION.md")
    print("  • Metasploit: SCADA modules will work")
