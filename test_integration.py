#!/usr/bin/env python3
"""
Integration Test Suite
Tests actual running services (requires Docker or manual service start)
"""

import socket
import struct
import time
import requests
import sys

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name):
    print(f"\n{BLUE}[TEST]{RESET} {name}")

def print_pass(msg):
    print(f"  {GREEN}✓{RESET} {msg}")

def print_fail(msg):
    print(f"  {RED}✗{RESET} {msg}")

def print_warn(msg):
    print(f"  {YELLOW}⚠{RESET} {msg}")

def test_modbus_connection():
    """Test actual Modbus TCP connection stability"""
    print_test("Modbus TCP Connection Stability")

    try:
        # Try to connect to Modbus server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('127.0.0.1', 5502))
        print_pass("Connected to Modbus server on port 5502")

        # Build Modbus read holding registers request
        # MBAP Header: Trans ID (2), Proto ID (2), Length (2), Unit ID (1)
        # PDU: Function Code (1), Start Addr (2), Quantity (2)
        transaction_id = 1
        protocol_id = 0
        length = 6  # 1 unit_id + 5 PDU bytes
        unit_id = 1
        function_code = 0x03  # Read Holding Registers
        start_addr = 0
        quantity = 10

        # Build request
        mbap_header = struct.pack('>HHHB', transaction_id, protocol_id, length, unit_id)
        pdu = struct.pack('>BHH', function_code, start_addr, quantity)
        request = mbap_header + pdu

        # Send request
        sock.send(request)
        print_pass("Sent read holding registers request (addr=0, count=10)")

        # Receive response with timeout (should not hang)
        response = sock.recv(1024)
        if len(response) > 0:
            print_pass(f"Received response without hanging ({len(response)} bytes)")

            # Parse response
            resp_trans, resp_proto, resp_len, resp_unit = struct.unpack('>HHHB', response[:7])
            resp_func = response[7]

            if resp_func == function_code:
                print_pass("Response has correct function code (0x03)")
            elif resp_func == (function_code | 0x80):
                print_warn(f"Received Modbus exception response: {response[8]:02x}")
            else:
                print_warn(f"Unexpected function code: {resp_func:02x}")
        else:
            print_fail("No response received")

        sock.close()
        return True

    except socket.timeout:
        print_fail("Connection timed out (server may not be running)")
        return False
    except ConnectionRefusedError:
        print_warn("Connection refused - Modbus server not running on port 5502")
        print_warn("Start services with: docker-compose up -d")
        return False
    except Exception as e:
        print_fail(f"Modbus connection test failed: {e}")
        return False

def test_modbus_write_coil():
    """Test write coil operation doesn't hang"""
    print_test("Modbus Write Coil (No Hang Test)")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('127.0.0.1', 5502))

        # Build write single coil request (FC 0x05)
        transaction_id = 2
        protocol_id = 0
        length = 6
        unit_id = 1
        function_code = 0x05  # Write Single Coil
        coil_addr = 0  # Pump 1
        coil_value = 0xFF00  # ON

        mbap_header = struct.pack('>HHHB', transaction_id, protocol_id, length, unit_id)
        pdu = struct.pack('>BHH', function_code, coil_addr, coil_value)
        request = mbap_header + pdu

        start_time = time.time()
        sock.send(request)
        response = sock.recv(1024)
        elapsed = time.time() - start_time

        if elapsed < 2.0:
            print_pass(f"Write coil completed without hanging ({elapsed:.3f}s)")
        else:
            print_warn(f"Write coil took longer than expected ({elapsed:.3f}s)")

        sock.close()
        return True

    except socket.timeout:
        print_fail("Write coil request timed out (HANG DETECTED)")
        return False
    except ConnectionRefusedError:
        print_warn("Modbus server not running")
        return False
    except Exception as e:
        print_fail(f"Write coil test failed: {e}")
        return False

def test_web_interface():
    """Test web interface availability"""
    print_test("Web Interface Availability")

    try:
        # Test login page
        response = requests.get('http://127.0.0.1:5000/login', timeout=5)
        if response.status_code == 200:
            print_pass("Web interface accessible on port 5000")

            # Test SQL injection still works
            payload = {
                'username': "admin' OR '1'='1' --",
                'password': "anything"
            }
            response = requests.post('http://127.0.0.1:5000/login', data=payload, timeout=5, allow_redirects=False)

            if response.status_code == 302:  # Redirect after successful login
                print_pass("SQL Injection vulnerability still functional")
            else:
                print_warn(f"SQL Injection may not work (status: {response.status_code})")

            return True
        else:
            print_fail(f"Unexpected status code: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print_warn("Web interface not running on port 5000")
        print_warn("Start services with: docker-compose up -d")
        return False
    except Exception as e:
        print_fail(f"Web interface test failed: {e}")
        return False

def test_rapid_modbus_requests():
    """Test server stability under rapid requests"""
    print_test("Rapid Modbus Requests (Stability Test)")

    try:
        success_count = 0
        fail_count = 0

        for i in range(10):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect(('127.0.0.1', 5502))

                # Quick read request
                transaction_id = 100 + i
                mbap_header = struct.pack('>HHHB', transaction_id, 0, 6, 1)
                pdu = struct.pack('>BHH', 0x03, 0, 5)
                sock.send(mbap_header + pdu)

                response = sock.recv(1024)
                if len(response) > 0:
                    success_count += 1

                sock.close()
            except Exception as e:
                fail_count += 1

        if success_count == 10:
            print_pass(f"All 10 rapid requests succeeded ({success_count}/10)")
        elif success_count >= 8:
            print_pass(f"Most requests succeeded ({success_count}/10)")
        else:
            print_warn(f"Only {success_count}/10 requests succeeded")

        return success_count >= 8

    except ConnectionRefusedError:
        print_warn("Modbus server not running")
        return False
    except Exception as e:
        print_fail(f"Rapid request test failed: {e}")
        return False

def main():
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}  Vuln-PLC Integration Test Suite{RESET}")
    print(f"{BLUE}  Tests actual running services{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

    print(f"{YELLOW}Note: These tests require services to be running.{RESET}")
    print(f"{YELLOW}Start with: docker-compose up -d{RESET}\n")

    results = []

    # Run integration tests
    results.append(("Modbus Connection", test_modbus_connection()))
    results.append(("Modbus Write Coil", test_modbus_write_coil()))
    results.append(("Rapid Modbus Requests", test_rapid_modbus_requests()))
    results.append(("Web Interface", test_web_interface()))

    # Summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}  Integration Test Summary{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        if result is None:
            status = f"{YELLOW}SKIP{RESET}"
        elif result:
            status = f"{GREEN}PASS{RESET}"
        else:
            status = f"{RED}FAIL{RESET}"
        print(f"  {status}  {test_name}")

    print(f"\n{BLUE}{'='*70}{RESET}")
    if passed == total:
        print(f"{GREEN}  ALL INTEGRATION TESTS PASSED ({passed}/{total}){RESET}")
    elif passed > 0:
        print(f"{YELLOW}  {passed}/{total} integration tests passed{RESET}")
        print(f"{YELLOW}  Some services may not be running{RESET}")
    else:
        print(f"{YELLOW}  Services not running - start with docker-compose up -d{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

    return passed > 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
