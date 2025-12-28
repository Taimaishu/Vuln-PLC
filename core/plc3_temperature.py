#!/usr/bin/env python3
"""
PLC-3: Temperature Control System - Web Interface
Port 5012

INTENTIONALLY VULNERABLE - For security testing only
Vulnerabilities: Firmware upload bypass, insecure deserialization, race conditions
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pickle
import base64
import os
import sys
import hashlib
import time
import socket
import struct
import threading
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import shared_state

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'plc3-insecure-key-777'

shared_state.init_state()

USERS = {
    'engineer': 'temp123',
    'technician': 'control456',
    'admin': 'admin'
}

def get_plc3_state():
    state = shared_state.load_state()
    plc3_state = {}
    for key, value in state.items():
        if key.startswith('plc3_'):
            plc3_state[key.replace('plc3_', '')] = value
    return plc3_state

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if username in USERS and USERS[username] == password:
            session['username'] = username
            session['plc_id'] = 3
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid credentials'

    return render_template('plc3_login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    plc_state = get_plc3_state()
    return render_template('plc3_dashboard.html',
                          username=session['username'],
                          state=plc_state)

@app.route('/api/status')
def api_status():
    plc_state = get_plc3_state()
    return jsonify({
        'plc_id': 3,
        'name': 'Temperature Control System',
        'status': 'running',
        'state': plc_state
    })

@app.route('/api/control', methods=['POST'])
def api_control():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or request.form.to_dict()
    action = data.get('action')
    value = data.get('value')

    # Temperature controls
    if action.startswith('heater') and action.endswith('_status'):
        shared_state.update_state(f'plc3_{action}', value in ['true', 'True', True, 1, '1'])
    elif action.startswith('cooler') and action.endswith('_status'):
        shared_state.update_state(f'plc3_{action}', value in ['true', 'True', True, 1, '1'])
    elif action.startswith('heater') and action.endswith('_power'):
        shared_state.update_state(f'plc3_{action}', int(value))
    elif action.startswith('cooler') and action.endswith('_power'):
        shared_state.update_state(f'plc3_{action}', int(value))
    elif action.startswith('setpoint'):
        shared_state.update_state(f'plc3_{action}', float(value))
    elif action == 'thermal_runaway':
        # VULNERABILITY: Race condition - can be triggered by multiple requests
        shared_state.update_state('plc3_thermal_runaway', value in ['true', 'True', True, 1, '1'])

    return jsonify({'success': True, 'action': action, 'value': value})

@app.route('/api/firmware/upload', methods=['POST'])
def firmware_upload():
    """VULNERABILITY: Insecure firmware upload"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'firmware' not in request.files:
        return jsonify({'error': 'No firmware file'}), 400

    firmware = request.files['firmware']

    # VULNERABILITY: No signature verification, no file type checking
    if firmware.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save firmware directly without validation
    firmware_dir = 'firmwares'
    os.makedirs(firmware_dir, exist_ok=True)

    filepath = os.path.join(firmware_dir, firmware.filename)
    firmware.save(filepath)

    # VULNERABILITY: Execute firmware without verification
    # (Simulated - doesn't actually execute)
    return jsonify({
        'success': True,
        'message': 'Firmware uploaded successfully (unverified)',
        'filename': firmware.filename,
        'path': filepath,
        'warning': 'No signature check performed'
    })

@app.route('/api/config/export', methods=['POST'])
def config_export():
    """VULNERABILITY: Insecure deserialization"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    config = {
        'zones': {
            'zone1': {'setpoint': shared_state.get_state('plc3_setpoint1', 25.0)},
            'zone2': {'setpoint': shared_state.get_state('plc3_setpoint2', 25.0)},
            'zone3': {'setpoint': shared_state.get_state('plc3_setpoint3', 25.0)},
        },
        'safety': {
            'high_limit': shared_state.get_state('plc3_safety_limit_high', 100.0),
            'low_limit': shared_state.get_state('plc3_safety_limit_low', 0.0),
        }
    }

    # VULNERABILITY: Using pickle for serialization
    pickled = pickle.dumps(config)
    encoded = base64.b64encode(pickled).decode('utf-8')

    return jsonify({
        'success': True,
        'config': encoded,
        'format': 'base64-pickle'
    })

@app.route('/api/config/import', methods=['POST'])
def config_import():
    """VULNERABILITY: Insecure deserialization - RCE vector"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    encoded_config = request.form.get('config', '')

    try:
        # VULNERABILITY: Unpickling user data - RCE!
        decoded = base64.b64decode(encoded_config)
        config = pickle.loads(decoded)

        # Apply configuration
        if 'zones' in config:
            for zone, settings in config['zones'].items():
                if 'setpoint' in settings:
                    shared_state.update_state(f'plc3_setpoint{zone[-1]}', settings['setpoint'])

        return jsonify({
            'success': True,
            'message': 'Configuration imported'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/race_test', methods=['POST'])
def race_test():
    """VULNERABILITY: Race condition testing endpoint"""
    # VULNERABILITY: No locking mechanism
    action = request.form.get('action', 'increment')

    if action == 'increment':
        counter = shared_state.get_state('plc3_race_counter', 0)
        time.sleep(0.01)  # Deliberate delay to make race condition easier to exploit
        shared_state.update_state('plc3_race_counter', counter + 1)
        return jsonify({'counter': counter + 1})

    elif action == 'reset':
        shared_state.update_state('plc3_race_counter', 0)
        return jsonify({'counter': 0})

    return jsonify({'error': 'Invalid action'}), 400


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

    def __init__(self, host='0.0.0.0', port=5504, max_connections=50):
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

            print(f"[MODBUS] PLC3 Server started on {self.host}:{self.port}")

            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"[MODBUS] PLC3 Client connected from {address}")

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
                        print(f"[MODBUS] PLC3 Error accepting connection: {e}")

        except Exception as e:
            print(f"[MODBUS] PLC3 Failed to start server: {e}")

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
                    print(f"[MODBUS] PLC3 WARNING: Non-standard protocol ID {protocol_id} from {address}")

                pdu = self.recv_exact(client_socket, length - 1)
                print(f"[MODBUS] PLC3 Request from {address}: Trans={transaction_id}, Unit={unit_id}, PDU={pdu.hex()}")

                function_code = pdu[0]
                response_pdu = self.process_request(function_code, pdu[1:])

                response_length = len(response_pdu) + 1
                response_header = struct.pack('>HHHB', transaction_id, protocol_id, response_length, unit_id)

                response = response_header + response_pdu
                client_socket.send(response)
                print(f"[MODBUS] PLC3 Response: {response.hex()}")

        except Exception as e:
            print(f"[MODBUS] PLC3 Error handling client {address}: {e}")
        finally:
            client_socket.close()
            print(f"[MODBUS] PLC3 Client {address} disconnected")

    def process_request(self, function_code, data):
        """Process Modbus request and return response PDU"""
        try:
            if function_code == 0x03:
                return self.read_holding_registers(data)
            elif function_code == 0x06:
                return self.write_single_register(data)
            elif function_code == 0x10:
                return self.write_multiple_registers(data)
            else:
                return struct.pack('B', function_code | 0x80) + struct.pack('B', 0x01)

        except Exception as e:
            print(f"[MODBUS] PLC3 Error processing request: {e}")
            return struct.pack('B', function_code | 0x80) + struct.pack('B', 0x04)

    def read_holding_registers(self, data):
        """Function Code 0x03: Read Holding Registers"""
        start_addr, count = struct.unpack('>HH', data[:4])
        print(f"[MODBUS] PLC3 Read Holding Registers: addr={start_addr}, count={count}")

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
        print(f"[MODBUS] PLC3 Write Single Register: addr={addr}, value={value}")

        key, converted_value = shared_state.register_to_state(addr, value)
        if key:
            shared_state.update_state(key, converted_value)
            print(f"[MODBUS] PLC3 Updated {key} = {converted_value}")

        return struct.pack('B', 0x06) + data[:4]

    def write_multiple_registers(self, data):
        """Function Code 0x10: Write Multiple Registers"""
        start_addr, count, byte_count = struct.unpack('>HHB', data[:5])
        print(f"[MODBUS] PLC3 Write Multiple Registers: addr={start_addr}, count={count}")

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
                print(f"[MODBUS] PLC3 Updated {key} = {converted_value}")

        return struct.pack('>BHH', 0x10, start_addr, count)


def start_modbus_server():
    """Start Modbus TCP server in background thread"""
    modbus_server = ModbusTCPServer(host='0.0.0.0', port=5504)
    server_thread = threading.Thread(target=modbus_server.start, daemon=True)
    server_thread.start()
    print("[STARTUP] PLC3 Modbus server thread started")


if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  PLC-3: Temperature Control System                        ║
    ║  FOR SECURITY TESTING AND EDUCATION ONLY                  ║
    ╚═══════════════════════════════════════════════════════════╝

    Default Credentials:
      engineer / temp123
      technician / control456
      admin / admin

    Web Interface: http://localhost:5012
    Modbus TCP:    localhost:5504

    Known Vulnerabilities:
      • Insecure firmware upload (no verification)
      • Insecure deserialization (pickle RCE)
      • Race conditions in thermal control
      • No safety interlock verification

    WARNING: DO NOT EXPOSE TO INTERNET
    """)

    # Start Modbus server in background
    start_modbus_server()

    app.run(host='0.0.0.0', port=5012, debug=True)
