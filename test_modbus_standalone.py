#!/usr/bin/env python3
"""
Standalone test for Modbus TCP Server
Tests the Modbus implementation without requiring Flask
"""

import socket
import struct
import sys
import os

# Add the core directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

def test_modbus_read():
    """Test reading holding registers"""
    print("\n[TEST] Reading Holding Registers (Function Code 0x03)...")

    # Connect to Modbus server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5502))

    # Build Modbus TCP request
    # MBAP Header
    transaction_id = 0x0001
    protocol_id = 0x0000
    unit_id = 0x01

    # PDU: Function Code 0x03, Start Address 0, Count 10
    pdu = struct.pack('>BHH', 0x03, 0x0000, 10)
    length = len(pdu) + 1  # +1 for unit_id

    # Complete request
    request = struct.pack('>HHHB', transaction_id, protocol_id, length, unit_id) + pdu

    print(f"  Request: {request.hex()}")
    sock.send(request)

    # Read response
    response = sock.recv(1024)
    print(f"  Response: {response.hex()}")

    # Parse response
    resp_trans_id, resp_proto_id, resp_length, resp_unit_id = struct.unpack('>HHHB', response[:7])
    function_code = response[7]
    byte_count = response[8]

    print(f"  Transaction ID: {resp_trans_id}")
    print(f"  Function Code: {function_code:#04x}")
    print(f"  Byte Count: {byte_count}")

    # Parse register values
    values = []
    for i in range(byte_count // 2):
        offset = 9 + (i * 2)
        value = struct.unpack('>H', response[offset:offset+2])[0]
        values.append(value)

    print(f"  Register Values: {values}")

    sock.close()
    return True

def test_modbus_write():
    """Test writing single register"""
    print("\n[TEST] Writing Single Register (Function Code 0x06)...")

    # Connect to Modbus server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5502))

    # Build Modbus TCP request
    transaction_id = 0x0002
    protocol_id = 0x0000
    unit_id = 0x01

    # PDU: Function Code 0x06, Address 0, Value 1000 (100.0 scaled)
    pdu = struct.pack('>BHH', 0x06, 0x0000, 1000)
    length = len(pdu) + 1

    # Complete request
    request = struct.pack('>HHHB', transaction_id, protocol_id, length, unit_id) + pdu

    print(f"  Request: {request.hex()}")
    sock.send(request)

    # Read response
    response = sock.recv(1024)
    print(f"  Response: {response.hex()}")

    # Parse response
    resp_trans_id, resp_proto_id, resp_length, resp_unit_id = struct.unpack('>HHHB', response[:7])
    function_code = response[7]
    addr, value = struct.unpack('>HH', response[8:12])

    print(f"  Function Code: {function_code:#04x}")
    print(f"  Address: {addr}")
    print(f"  Value: {value}")

    sock.close()
    return True

def test_modbus_write_multiple():
    """Test writing multiple registers"""
    print("\n[TEST] Writing Multiple Registers (Function Code 0x10)...")

    # Connect to Modbus server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5502))

    # Build Modbus TCP request
    transaction_id = 0x0003
    protocol_id = 0x0000
    unit_id = 0x01

    # PDU: Function Code 0x10, Start Address 0, Count 3, Byte Count 6, Values [500, 250, 1013]
    values = [500, 250, 1013]
    byte_count = len(values) * 2
    pdu = struct.pack('>BHHB', 0x10, 0x0000, len(values), byte_count)
    for value in values:
        pdu += struct.pack('>H', value)

    length = len(pdu) + 1

    # Complete request
    request = struct.pack('>HHHB', transaction_id, protocol_id, length, unit_id) + pdu

    print(f"  Request: {request.hex()}")
    sock.send(request)

    # Read response
    response = sock.recv(1024)
    print(f"  Response: {response.hex()}")

    # Parse response
    resp_trans_id, resp_proto_id, resp_length, resp_unit_id = struct.unpack('>HHHB', response[:7])
    function_code = response[7]
    start_addr, count = struct.unpack('>HH', response[8:12])

    print(f"  Function Code: {function_code:#04x}")
    print(f"  Start Address: {start_addr}")
    print(f"  Count: {count}")

    sock.close()
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("Modbus TCP Server Test Suite")
    print("=" * 60)

    try:
        # Test if server is running
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5502))
        sock.close()

        if result != 0:
            print("\n[ERROR] Modbus server is not running on localhost:5502")
            print("Please start the server first with: python core/app.py")
            sys.exit(1)

        print("\n[OK] Modbus server is running")

        # Run tests
        test_modbus_read()
        test_modbus_write()
        test_modbus_write_multiple()

        print("\n" + "=" * 60)
        print("[SUCCESS] All tests passed!")
        print("=" * 60)

    except ConnectionRefusedError:
        print("\n[ERROR] Connection refused - server not running")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
