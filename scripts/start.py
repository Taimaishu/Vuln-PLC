#!/usr/bin/env python3
"""
Startup script for Vulnerable PLC Simulator
Starts both the web interface and Modbus TCP server
"""

import subprocess
import sys
import time
from multiprocessing import Process

def start_modbus_server():
    """Start Modbus TCP server"""
    subprocess.run([sys.executable, 'modbus_server.py'])

def start_web_server():
    """Start Flask web server"""
    subprocess.run([sys.executable, 'app.py'])

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  Vulnerable PLC Simulator v1.0                            ║
    ║  FOR SECURITY TESTING AND EDUCATION ONLY                  ║
    ╚═══════════════════════════════════════════════════════════╝

    Starting services...
    """)

    # Start Modbus server in background
    modbus_process = Process(target=start_modbus_server)
    modbus_process.start()

    time.sleep(2)  # Give Modbus server time to start

    # Start web server in foreground
    web_process = Process(target=start_web_server)
    web_process.start()

    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  Services Started Successfully                            ║
    ╚═══════════════════════════════════════════════════════════╝

    Web Interface:  http://localhost:5000
    Modbus TCP:     localhost:5502

    Default Credentials:
      admin / admin
      operator / operator123
      guest / guest

    Press Ctrl+C to stop all services
    """)

    try:
        modbus_process.join()
        web_process.join()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        modbus_process.terminate()
        web_process.terminate()
        modbus_process.join()
        web_process.join()
        print("All services stopped.")

if __name__ == '__main__':
    main()
