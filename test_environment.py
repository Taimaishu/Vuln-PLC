#!/usr/bin/env python3
"""
Test script to verify the vulnerable PLC environment is working
"""

import requests
import time
import sys

def test_web_interface():
    """Test web interface"""
    print("[1/5] Testing web interface...")
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("  ✓ Web interface is accessible")
            return True
        else:
            print(f"  ✗ Web interface returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ Cannot connect to web interface: {e}")
        return False

def test_login():
    """Test login functionality"""
    print("[2/5] Testing login...")
    try:
        session = requests.Session()
        response = session.post('http://localhost:5000/login',
                               data={'username': 'admin', 'password': 'admin'},
                               timeout=5,
                               allow_redirects=False)
        if response.status_code in [200, 302]:
            print("  ✓ Login successful")
            return True, session
        else:
            print(f"  ✗ Login failed with status {response.status_code}")
            return False, None
    except Exception as e:
        print(f"  ✗ Login test failed: {e}")
        return False, None

def test_sql_injection():
    """Test SQL injection vulnerability"""
    print("[3/5] Testing SQL injection vulnerability...")
    try:
        session = requests.Session()
        response = session.post('http://localhost:5000/login',
                               data={'username': "admin' OR '1'='1", 'password': 'anything'},
                               timeout=5,
                               allow_redirects=False)
        if response.status_code in [200, 302]:
            print("  ✓ SQL injection vulnerability confirmed")
            return True
        else:
            print(f"  ✗ SQL injection test returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ SQL injection test failed: {e}")
        return False

def test_modbus():
    """Test Modbus TCP server"""
    print("[4/5] Testing Modbus TCP server...")
    try:
        from pymodbus.client.sync import ModbusTcpClient
        client = ModbusTcpClient('localhost', port=5502, timeout=5)
        if client.connect():
            result = client.read_holding_registers(0, 5)
            if result:
                print(f"  ✓ Modbus server responding (registers: {result.registers})")
                client.close()
                return True
            else:
                print("  ✗ Modbus read failed")
                client.close()
                return False
        else:
            print("  ✗ Cannot connect to Modbus server")
            return False
    except ImportError:
        print("  ⚠ pymodbus not installed (optional for web testing)")
        return True
    except Exception as e:
        print(f"  ✗ Modbus test failed: {e}")
        return False

def test_command_injection(session):
    """Test command injection vulnerability"""
    print("[5/5] Testing command injection...")
    if not session:
        print("  ⚠ Skipped (no authenticated session)")
        return True

    try:
        response = session.post('http://localhost:5000/admin/exec',
                               data={'command': 'echo "test"'},
                               timeout=5)
        data = response.json()
        if 'output' in data and 'test' in data['output']:
            print("  ✓ Command injection vulnerability confirmed")
            return True
        else:
            print("  ✗ Command injection test failed")
            return False
    except Exception as e:
        print(f"  ✗ Command injection test failed: {e}")
        return False

def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║  Vulnerable PLC Environment Test                          ║
╚═══════════════════════════════════════════════════════════╝

Testing all components...
    """)

    results = []

    # Test web interface
    results.append(test_web_interface())

    # Test login
    login_ok, session = test_login()
    results.append(login_ok)

    # Test SQL injection
    results.append(test_sql_injection())

    # Test Modbus
    results.append(test_modbus())

    # Test command injection
    results.append(test_command_injection(session))

    # Summary
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✓ ALL TESTS PASSED ({passed}/{total})")
        print("\n╔═══════════════════════════════════════════════════════════╗")
        print("║  Environment is ready for security testing!               ║")
        print("╚═══════════════════════════════════════════════════════════╝")
        print("\nWeb Interface: http://localhost:5000")
        print("Modbus TCP:    localhost:5502")
        print("\nDefault credentials: admin / admin")
        return 0
    else:
        print(f"✗ SOME TESTS FAILED ({passed}/{total} passed)")
        print("\nPlease ensure the environment is running:")
        print("  python start.py")
        return 1

if __name__ == '__main__':
    sys.exit(main())
