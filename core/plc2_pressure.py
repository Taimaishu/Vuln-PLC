#!/usr/bin/env python3
"""
PLC-2: Pressure Control System - Web Interface
Port 5011

INTENTIONALLY VULNERABLE - For security testing only
Vulnerabilities: Authentication bypass, buffer overflow simulation, replay attacks
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import hashlib
import time
from datetime import datetime
import os
import sys
import socket
import struct
import threading
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import shared_state

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'plc2-weak-secret-999'  # Intentionally weak

# Initialize shared state
shared_state.init_state()

# VULNERABILITY: Weak authentication
HARDCODED_CREDS = {
    'engineer': 'plc2pass',
    'operator': 'pressure123',
    'admin': 'admin'
}

def get_plc2_state():
    """Get PLC-2 state from shared storage"""
    state = shared_state.load_state()
    plc2_state = {}
    for key, value in state.items():
        if key.startswith('plc2_'):
            plc2_state[key.replace('plc2_', '')] = value
    return plc2_state

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """VULNERABILITY: Authentication bypass via timing attack"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # VULNERABILITY: Timing attack - check username first
        if username in HARDCODED_CREDS:
            time.sleep(0.1)  # Intentional delay reveals valid usernames
            if HARDCODED_CREDS[username] == password:
                session['username'] = username
                session['plc_id'] = 2
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid password'
        else:
            error = 'Invalid credentials'

        # VULNERABILITY: Weak session - can be bypassed
        # Try authentication bypass via header injection
        auth_bypass = request.headers.get('X-PLC-Auth-Override')
        if auth_bypass == 'bypass-plc2-auth':
            session['username'] = 'admin'
            session['plc_id'] = 2
            return redirect(url_for('dashboard'))

    return render_template('plc2_login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    plc_state = get_plc2_state()
    return render_template('plc2_dashboard.html',
                          username=session['username'],
                          state=plc_state)

@app.route('/api/status')
def api_status():
    """Get current PLC-2 status"""
    plc_state = get_plc2_state()
    return jsonify({
        'plc_id': 2,
        'name': 'Pressure Control System',
        'status': 'running',
        'state': plc_state
    })

@app.route('/api/control', methods=['POST'])
def api_control():
    """VULNERABILITY: No authentication check on control endpoint"""
    # VULNERABILITY: Missing authentication
    # if 'username' not in session:
    #     return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or request.form.to_dict()
    action = data.get('action')
    value = data.get('value')

    # Update state in shared storage
    if action == 'compressor_1_status':
        shared_state.update_state('plc2_compressor_1_status', value in ['true', 'True', True, 1, '1'])
    elif action == 'compressor_2_status':
        shared_state.update_state('plc2_compressor_2_status', value in ['true', 'True', True, 1, '1'])
    elif action == 'compressor_1_speed':
        shared_state.update_state('plc2_compressor_1_speed', int(value))
    elif action == 'compressor_2_speed':
        shared_state.update_state('plc2_compressor_2_speed', int(value))
    elif action == 'relief_valve_1':
        shared_state.update_state('plc2_relief_valve_1', value in ['true', 'True', True, 1, '1'])
    elif action == 'relief_valve_2':
        shared_state.update_state('plc2_relief_valve_2', value in ['true', 'True', True, 1, '1'])
    elif action == 'emergency_vent':
        shared_state.update_state('plc2_emergency_vent', value in ['true', 'True', True, 1, '1'])

    return jsonify({'success': True, 'action': action, 'value': value})

@app.route('/api/replay', methods=['POST'])
def api_replay():
    """VULNERABILITY: Replay attack endpoint - stores and replays commands"""
    data = request.get_json()
    mode = data.get('mode', 'record')

    if mode == 'record':
        # Record a command sequence
        commands = data.get('commands', [])
        replay_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        shared_state.update_state(f'replay_{replay_id}', commands)
        return jsonify({'success': True, 'replay_id': replay_id})

    elif mode == 'playback':
        # Playback recorded commands (VULNERABILITY: No validation)
        replay_id = data.get('replay_id')
        commands = shared_state.get_state(f'replay_{replay_id}', [])

        for cmd in commands:
            # Execute each command without validation
            shared_state.update_state(f'plc2_{cmd["action"]}', cmd['value'])

        return jsonify({'success': True, 'commands_executed': len(commands)})

    return jsonify({'error': 'Invalid mode'}), 400

@app.route('/api/buffer', methods=['POST'])
def api_buffer():
    """VULNERABILITY: Simulated buffer overflow"""
    data = request.form.get('data', '')

    # VULNERABILITY: No size checking (simulated overflow)
    if len(data) > 256:
        # Simulate memory corruption
        return jsonify({
            'error': 'Buffer overflow detected',
            'message': 'Memory corruption - safety systems disabled',
            'corrupted_registers': [0, 1, 2, 3, 4, 5],
            'vulnerability': 'CVE-2024-FAKE-OVERFLOW'
        }), 500

    return jsonify({'success': True, 'data_length': len(data)})

@app.route('/api/firmware/info')
def firmware_info():
    """VULNERABILITY: Information disclosure"""
    return jsonify({
        'firmware_version': '1.2.3',
        'build_date': '2024-01-15',
        'checksum': 'abc123def456',  # Weak checksum
        'debug_enabled': True,
        'backdoor_port': 5555,  # Easter egg
        'encryption': 'none',
        'vendor': 'VulnPLC Corp',
        'secret_key': app.secret_key
    })

@app.route('/api/diagnostic', methods=['POST'])
def diagnostic():
    """VULNERABILITY: Command injection via diagnostic interface"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    command = request.form.get('command', '')

    # VULNERABILITY: Limited command injection
    allowed_commands = ['status', 'version', 'uptime', 'config']

    if command in allowed_commands:
        # Simulate command output
        outputs = {
            'status': 'PLC-2 Online - Pressure System Nominal',
            'version': 'VulnPLC v1.2.3',
            'uptime': '42 days, 13 hours',
            'config': 'Config: pressure_max=150, safety_override=enabled'
        }
        return jsonify({'output': outputs.get(command, 'Unknown command')})

    # VULNERABILITY: Special commands with side effects
    if command == 'reset_safety':
        shared_state.update_state('plc2_safety_disabled', True)
        return jsonify({'output': 'WARNING: Safety systems disabled!'})

    if command.startswith('set_'):
        # VULNERABILITY: Arbitrary state modification
        parts = command.split('_', 2)
        if len(parts) >= 3:
            key = parts[1]
            value = parts[2]
            shared_state.update_state(f'plc2_{key}', value)
            return jsonify({'output': f'Set {key} = {value}'})

    return jsonify({'error': 'Invalid command'}), 400

@app.route('/api/logs')
def api_logs():
    """Get PLC-2 logs (limited history)"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Simulate log entries
    logs = [
        {'timestamp': '2024-12-07 10:15:32', 'level': 'INFO', 'message': 'Compressor 1 started'},
        {'timestamp': '2024-12-07 10:16:45', 'level': 'WARN', 'message': 'Pressure vessel 1 approaching limit'},
        {'timestamp': '2024-12-07 10:17:12', 'level': 'INFO', 'message': 'Relief valve 1 opened'},
        {'timestamp': '2024-12-07 10:18:00', 'level': 'INFO', 'message': 'Pressure normalized'},
    ]

    return jsonify({'logs': logs})

# Create necessary templates directory
import os
os.makedirs('templates', exist_ok=True)


class ModbusTCPServer:
    """
    Minimal Modbus TCP Server - Intentionally Vulnerable

    Implements only basic function codes:
    - 0x03: Read Holding Registers
    - 0x06: Write Single Register
    - 0x10: Write Multiple Registers

    VULNERABILITIES (INTENTIONAL):
    - No authentication
    - No bounds checking
    - No input validation
    - Allows writing to any register
    - No rate limiting (connection limit exists but is bypassable)
    - No logging of malicious activity
    """

    def __init__(self, host='0.0.0.0', port=5503, max_connections=50):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.connection_semaphore = threading.Semaphore(max_connections)

    def start(self):
        """Start the Modbus TCP server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.settimeout(1.0)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True

            print(f"[MODBUS] PLC2 Server started on {self.host}:{self.port}")

            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"[MODBUS] PLC2 Client connected from {address}")

                    client_thread = threading.Thread(
                        target=self._handle_client_with_semaphore,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()

                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[MODBUS] PLC2 Error accepting connection: {e}")

        except Exception as e:
            print(f"[MODBUS] PLC2 Failed to start server: {e}")

    def stop(self):
        """Stop the Modbus TCP server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

    def recv_exact(self, sock, size):
        """Receive exactly 'size' bytes from socket"""
        data = b''
        while len(data) < size:
            chunk = sock.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Socket closed before receiving all data")
            data += chunk
        return data

    def _handle_client_with_semaphore(self, client_socket, address):
        """Wrapper to handle client with connection semaphore"""
        with self.connection_semaphore:
            self.handle_client(client_socket, address)

    def handle_client(self, client_socket, address):
        """Handle a client connection"""
        try:
            while True:
                header = self.recv_exact(client_socket, 7)
                transaction_id, protocol_id, length, unit_id = struct.unpack('>HHHB', header)

                if protocol_id != 0:
                    print(f"[MODBUS] PLC2 WARNING: Non-standard protocol ID {protocol_id} from {address}")

                pdu = self.recv_exact(client_socket, length - 1)
                print(f"[MODBUS] PLC2 Request from {address}: Trans={transaction_id}, Unit={unit_id}, PDU={pdu.hex()}")

                function_code = pdu[0]
                response_pdu = self.process_request(function_code, pdu[1:])

                response_length = len(response_pdu) + 1
                response_header = struct.pack('>HHHB', transaction_id, protocol_id, response_length, unit_id)

                response = response_header + response_pdu
                client_socket.send(response)
                print(f"[MODBUS] PLC2 Response: {response.hex()}")

        except Exception as e:
            print(f"[MODBUS] PLC2 Error handling client {address}: {e}")
        finally:
            client_socket.close()
            print(f"[MODBUS] PLC2 Client {address} disconnected")

    def process_request(self, function_code, data):
        """Process Modbus request and return response PDU"""
        try:
            if function_code == 0x01:
                return self.read_coils(data)
            elif function_code == 0x03:
                return self.read_holding_registers(data)
            elif function_code == 0x05:
                return self.write_single_coil(data)
            elif function_code == 0x06:
                return self.write_single_register(data)
            elif function_code == 0x0F:
                return self.write_multiple_coils(data)
            elif function_code == 0x10:
                return self.write_multiple_registers(data)
            else:
                return struct.pack('B', function_code | 0x80) + struct.pack('B', 0x01)

        except Exception as e:
            print(f"[MODBUS] PLC2 Error processing request: {e}")
            return struct.pack('B', function_code | 0x80) + struct.pack('B', 0x04)

    def read_holding_registers(self, data):
        """Function Code 0x03: Read Holding Registers"""
        start_addr, count = struct.unpack('>HH', data[:4])
        print(f"[MODBUS] PLC2 Read Holding Registers: addr={start_addr}, count={count}")

        values = []
        for i in range(count):
            register = start_addr + i
            value = shared_state.state_to_register(register)
            values.append(value)

        byte_count = count * 2
        response = struct.pack('BB', 0x03, byte_count)
        for value in values:
            response += struct.pack('>H', value)

        return response

    def write_single_register(self, data):
        """Function Code 0x06: Write Single Register"""
        addr, value = struct.unpack('>HH', data[:4])
        print(f"[MODBUS] PLC2 Write Single Register: addr={addr}, value={value}")

        key, converted_value = shared_state.register_to_state(addr, value)
        if key:
            shared_state.update_state(key, converted_value)
            print(f"[MODBUS] PLC2 Updated {key} = {converted_value}")

        return struct.pack('B', 0x06) + data[:4]

    def write_multiple_registers(self, data):
        """Function Code 0x10: Write Multiple Registers"""
        start_addr, count, byte_count = struct.unpack('>HHB', data[:5])
        print(f"[MODBUS] PLC2 Write Multiple Registers: addr={start_addr}, count={count}")

        values_data = data[5:5+byte_count]
        values = []
        for i in range(count):
            value = struct.unpack('>H', values_data[i*2:(i+1)*2])[0]
            values.append(value)

        for i, value in enumerate(values):
            register = start_addr + i
            key, converted_value = shared_state.register_to_state(register, value)
            if key:
                shared_state.update_state(key, converted_value)
                print(f"[MODBUS] PLC2 Updated {key} = {converted_value}")

        return struct.pack('>BHH', 0x10, start_addr, count)

    def read_coils(self, data):
        """Function Code 0x01: Read Coils"""
        start_addr, count = struct.unpack('>HH', data[:4])
        print(f"[MODBUS] PLC2 Read Coils: addr={start_addr}, count={count}")

        coil_values = []
        for i in range(count):
            coil = start_addr + i
            value = shared_state.state_to_coil(coil)
            coil_values.append(value)

        byte_count = (count + 7) // 8
        packed_bytes = []

        for byte_idx in range(byte_count):
            byte_val = 0
            for bit_idx in range(8):
                coil_idx = byte_idx * 8 + bit_idx
                if coil_idx < count and coil_values[coil_idx]:
                    byte_val |= (1 << bit_idx)
            packed_bytes.append(byte_val)

        response = struct.pack('BB', 0x01, byte_count)
        for byte_val in packed_bytes:
            response += struct.pack('B', byte_val)

        return response

    def write_single_coil(self, data):
        """Function Code 0x05: Write Single Coil"""
        addr, value = struct.unpack('>HH', data[:4])
        coil_state = (value == 0xFF00)
        print(f"[MODBUS] PLC2 Write Single Coil: addr={addr}, value={coil_state}")

        key, bool_value = shared_state.coil_to_state(addr, coil_state)
        if key:
            shared_state.update_state(key, bool_value)
            print(f"[MODBUS] PLC2 Updated {key} = {bool_value}")

        return struct.pack('B', 0x05) + data[:4]

    def write_multiple_coils(self, data):
        """Function Code 0x0F: Write Multiple Coils"""
        start_addr, count, byte_count = struct.unpack('>HHB', data[:5])
        print(f"[MODBUS] PLC2 Write Multiple Coils: addr={start_addr}, count={count}")

        coil_bytes = data[5:5+byte_count]
        coil_values = []

        for byte_idx in range(byte_count):
            byte_val = coil_bytes[byte_idx]
            for bit_idx in range(8):
                if len(coil_values) < count:
                    coil_values.append(bool(byte_val & (1 << bit_idx)))

        for i, value in enumerate(coil_values[:count]):
            coil = start_addr + i
            key, bool_value = shared_state.coil_to_state(coil, value)
            if key:
                shared_state.update_state(key, bool_value)
                print(f"[MODBUS] PLC2 Updated {key} = {bool_value}")

        return struct.pack('>BHH', 0x0F, start_addr, count)


def start_modbus_server():
    """Start Modbus TCP server in background thread"""
    modbus_server = ModbusTCPServer(host='0.0.0.0', port=5503)
    server_thread = threading.Thread(target=modbus_server.start, daemon=True)
    server_thread.start()
    print("[STARTUP] PLC2 Modbus server thread started")


if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  PLC-2: Pressure Control System                           ║
    ║  FOR SECURITY TESTING AND EDUCATION ONLY                  ║
    ╚═══════════════════════════════════════════════════════════╝

    Default Credentials:
      engineer / plc2pass
      operator / pressure123
      admin / admin

    Web Interface: http://localhost:5011
    Modbus TCP:    localhost:5503

    Known Vulnerabilities:
      • Timing attack in authentication
      • Authentication bypass via header injection
      • Replay attack vulnerability
      • Buffer overflow (simulated)
      • Information disclosure
      • Missing authentication on control endpoints
      • Command injection in diagnostic interface

    WARNING: DO NOT EXPOSE TO INTERNET
    """)

    # Start Modbus server in background
    start_modbus_server()

    app.run(host='0.0.0.0', port=5011, debug=True)
