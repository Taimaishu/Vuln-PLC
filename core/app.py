#!/usr/bin/env python3
"""
Vulnerable Modbus PLC Simulator with Web Interface
For security testing and educational purposes only

INTENTIONALLY VULNERABLE - DO NOT USE IN PRODUCTION
Contains: SQL Injection, Default Creds, Command Injection, etc.
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
import sqlite3
import os
import sys
import subprocess
import hashlib
from datetime import datetime, timedelta
import secrets
import random
import json
import socket
import threading
import struct
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import shared_state

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'insecure-secret-key-12345'  # Intentionally weak

# Role-based access control decorator
def require_role(*allowed_roles):
    """Decorator to require specific roles for access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                return redirect(url_for('login'))

            user_role = session.get('role', 'guest')

            # VULNERABILITY: Check can be bypassed by manipulating session
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'Access Denied',
                    'message': f'Insufficient privileges. Required: {", ".join(allowed_roles)}. Your role: {user_role}',
                    'required_role': list(allowed_roles),
                    'current_role': user_role
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Initialize shared state on startup
shared_state.init_state()

# Backward compatibility - PROCESS_STATE now reads from shared state
class ProcessStateProxy:
    """Proxy object that reads/writes from shared state"""

    def __getitem__(self, key):
        return shared_state.get_state(key)

    def __setitem__(self, key, value):
        shared_state.update_state(key, value)

    def get(self, key, default=None):
        return shared_state.get_state(key, default)

    def __contains__(self, key):
        state = shared_state.load_state()
        return key in state

    def items(self):
        state = shared_state.load_state()
        return state.items()

    def keys(self):
        state = shared_state.load_state()
        return state.keys()

    def values(self):
        state = shared_state.load_state()
        return state.values()

    def update(self, other):
        state = shared_state.load_state()
        state.update(other)
        for key, value in other.items():
            shared_state.update_state(key, value)

# Global state for simulated process - now backed by shared storage
PROCESS_STATE = ProcessStateProxy()

# ============================================
# MODBUS TCP SERVER IMPLEMENTATION
# ============================================

class ModbusTCPServer:
    """
    Minimal Modbus TCP Server - Intentionally Vulnerable

    Implements realistic PLC function codes:
    - 0x01: Read Coils (digital outputs - pumps, valves, motors)
    - 0x03: Read Holding Registers (analog values - levels, temps, pressures)
    - 0x05: Write Single Coil (control single digital output)
    - 0x06: Write Single Register (set single analog value)
    - 0x0F: Write Multiple Coils (control multiple digital outputs)
    - 0x10: Write Multiple Registers (set multiple analog values)

    VULNERABILITIES (INTENTIONAL):
    - No authentication
    - No bounds checking
    - No input validation
    - Allows writing to any coil or register
    - No rate limiting (connection limit exists but is bypassable)
    - No logging of malicious activity
    """

    def __init__(self, host='0.0.0.0', port=5502, max_connections=50):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        # Connection semaphore - still DoS-able but requires more effort
        self.connection_semaphore = threading.Semaphore(max_connections)

    def start(self):
        """Start the Modbus TCP server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.settimeout(1.0)  # Allow graceful shutdown
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True

            print(f"[MODBUS] Server started on {self.host}:{self.port}")

            while self.running:
                try:
                    # Accept client connections
                    client_socket, address = self.server_socket.accept()
                    print(f"[MODBUS] Client connected from {address}")

                    # Use semaphore to limit concurrent connections
                    # Still vulnerable to DoS but requires more sophistication
                    client_thread = threading.Thread(
                        target=self._handle_client_with_semaphore,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()

                except socket.timeout:
                    # Expected - allows checking self.running
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[MODBUS] Error accepting connection: {e}")

        except Exception as e:
            print(f"[MODBUS] Failed to start server: {e}")

    def stop(self):
        """Stop the Modbus TCP server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()

    def recv_exact(self, sock, size):
        """
        Receive exactly 'size' bytes from socket.
        recv() does not guarantee all bytes in one call - this fixes that.
        Prevents broken pipes and hangs with real Modbus tools.
        """
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
                # Read MBAP header (7 bytes) - use recv_exact for message safety
                header = self.recv_exact(client_socket, 7)

                # Parse MBAP header
                transaction_id, protocol_id, length, unit_id = struct.unpack('>HHHB', header)

                # VULNERABILITY: No protocol validation - we accept invalid protocol IDs
                # Log for educational purposes (helps students learn the protocol)
                if protocol_id != 0:
                    print(f"[MODBUS] WARNING: Non-standard protocol ID {protocol_id} from {address} (expected 0)")

                # Read PDU (Protocol Data Unit) - use recv_exact for message safety
                pdu = self.recv_exact(client_socket, length - 1)  # -1 because unit_id already read

                print(f"[MODBUS] Request from {address}: Trans={transaction_id}, Unit={unit_id}, PDU={pdu.hex()}")

                # Parse function code
                function_code = pdu[0]

                # Process request and generate response
                response_pdu = self.process_request(function_code, pdu[1:])

                # Build MBAP response header
                response_length = len(response_pdu) + 1  # +1 for unit_id
                response_header = struct.pack('>HHHB', transaction_id, protocol_id, response_length, unit_id)

                # Send response
                response = response_header + response_pdu
                client_socket.send(response)
                print(f"[MODBUS] Response: {response.hex()}")

        except Exception as e:
            print(f"[MODBUS] Error handling client {address}: {e}")
        finally:
            client_socket.close()
            print(f"[MODBUS] Client {address} disconnected")

    def process_request(self, function_code, data):
        """Process Modbus request and return response PDU"""
        try:
            if function_code == 0x01:
                # Read Coils
                return self.read_coils(data)
            elif function_code == 0x03:
                # Read Holding Registers
                return self.read_holding_registers(data)
            elif function_code == 0x05:
                # Write Single Coil
                return self.write_single_coil(data)
            elif function_code == 0x06:
                # Write Single Register
                return self.write_single_register(data)
            elif function_code == 0x0F:
                # Write Multiple Coils
                return self.write_multiple_coils(data)
            elif function_code == 0x10:
                # Write Multiple Registers
                return self.write_multiple_registers(data)
            else:
                # Unsupported function code
                # VULNERABILITY: Should return proper exception, but we just echo
                return struct.pack('B', function_code | 0x80) + struct.pack('B', 0x01)

        except Exception as e:
            print(f"[MODBUS] Error processing request: {e}")
            # Return exception response
            return struct.pack('B', function_code | 0x80) + struct.pack('B', 0x04)

    def read_holding_registers(self, data):
        """
        Function Code 0x03: Read Holding Registers
        Request: [start_addr(2)] [count(2)]
        Response: [0x03] [byte_count(1)] [values(2*count)]
        """
        # VULNERABILITY: No bounds checking on data length
        start_addr, count = struct.unpack('>HH', data[:4])

        print(f"[MODBUS] Read Holding Registers: addr={start_addr}, count={count}")

        # VULNERABILITY: No bounds checking on register range
        # Should validate count <= 125 and addresses exist

        # Read values from shared state
        values = []
        for i in range(count):
            register = start_addr + i
            value = shared_state.state_to_register(register)
            values.append(value)

        # Build response
        byte_count = count * 2
        response = struct.pack('BB', 0x03, byte_count)
        for value in values:
            response += struct.pack('>H', value)

        return response

    def write_single_register(self, data):
        """
        Function Code 0x06: Write Single Register
        Request: [addr(2)] [value(2)]
        Response: [0x06] [addr(2)] [value(2)] (echo)
        """
        # VULNERABILITY: No bounds checking
        addr, value = struct.unpack('>HH', data[:4])

        print(f"[MODBUS] Write Single Register: addr={addr}, value={value}")

        # VULNERABILITY: No authentication or authorization
        # Anyone can write any value to any register

        # Convert register to state and update
        key, converted_value = shared_state.register_to_state(addr, value)
        if key:
            shared_state.update_state(key, converted_value)
            print(f"[MODBUS] Updated {key} = {converted_value}")

        # Echo request as response
        return struct.pack('B', 0x06) + data[:4]

    def write_multiple_registers(self, data):
        """
        Function Code 0x10: Write Multiple Registers
        Request: [start_addr(2)] [count(2)] [byte_count(1)] [values(2*count)]
        Response: [0x10] [start_addr(2)] [count(2)]
        """
        # VULNERABILITY: No bounds checking
        start_addr, count, byte_count = struct.unpack('>HHB', data[:5])

        print(f"[MODBUS] Write Multiple Registers: addr={start_addr}, count={count}")

        # VULNERABILITY: No validation of byte_count == count*2
        # VULNERABILITY: No authentication

        # Parse values
        values_data = data[5:5+byte_count]
        values = []
        for i in range(count):
            value = struct.unpack('>H', values_data[i*2:(i+1)*2])[0]
            values.append(value)

        # Write to state
        for i, value in enumerate(values):
            register = start_addr + i
            key, converted_value = shared_state.register_to_state(register, value)
            if key:
                shared_state.update_state(key, converted_value)
                print(f"[MODBUS] Updated {key} = {converted_value}")

        # Build response
        return struct.pack('>BHH', 0x10, start_addr, count)

    def read_coils(self, data):
        """
        Function Code 0x01: Read Coils
        Request: [start_addr(2)] [count(2)]
        Response: [0x01] [byte_count(1)] [coil_values(packed bits)]
        """
        start_addr, count = struct.unpack('>HH', data[:4])

        print(f"[MODBUS] Read Coils: addr={start_addr}, count={count}")

        # VULNERABILITY: No bounds checking
        # Read coil values from shared state
        coil_values = []
        for i in range(count):
            coil = start_addr + i
            value = shared_state.coil_to_state(coil)
            coil_values.append(value)

        # Pack coils into bytes (8 coils per byte)
        byte_count = (count + 7) // 8  # Round up to nearest byte
        packed_bytes = []

        for byte_idx in range(byte_count):
            byte_val = 0
            for bit_idx in range(8):
                coil_idx = byte_idx * 8 + bit_idx
                if coil_idx < count and coil_values[coil_idx]:
                    byte_val |= (1 << bit_idx)
            packed_bytes.append(byte_val)

        # Build response
        response = struct.pack('BB', 0x01, byte_count)
        for byte_val in packed_bytes:
            response += struct.pack('B', byte_val)

        return response

    def write_single_coil(self, data):
        """
        Function Code 0x05: Write Single Coil
        Request: [addr(2)] [value(2)] - value is 0xFF00 (ON) or 0x0000 (OFF)
        Response: [0x05] [addr(2)] [value(2)] (echo)
        """
        addr, value = struct.unpack('>HH', data[:4])

        # Value should be 0xFF00 (ON) or 0x0000 (OFF)
        coil_state = (value == 0xFF00)

        print(f"[MODBUS] Write Single Coil: addr={addr}, value={coil_state}")

        # VULNERABILITY: No authentication or authorization
        # Convert coil to state and update
        key, bool_value = shared_state.coil_to_state(addr, coil_state)
        if key:
            shared_state.update_state(key, bool_value)
            print(f"[MODBUS] Updated {key} = {bool_value}")

        # Echo request as response
        return struct.pack('B', 0x05) + data[:4]

    def write_multiple_coils(self, data):
        """
        Function Code 0x0F: Write Multiple Coils
        Request: [start_addr(2)] [count(2)] [byte_count(1)] [coil_values(packed bits)]
        Response: [0x0F] [start_addr(2)] [count(2)]
        """
        start_addr, count, byte_count = struct.unpack('>HHB', data[:5])

        print(f"[MODBUS] Write Multiple Coils: addr={start_addr}, count={count}")

        # VULNERABILITY: No validation of byte_count
        # VULNERABILITY: No authentication

        # Parse packed coil values
        coil_bytes = data[5:5+byte_count]
        coil_values = []

        for byte_idx in range(byte_count):
            byte_val = coil_bytes[byte_idx]
            for bit_idx in range(8):
                if len(coil_values) < count:
                    coil_values.append(bool(byte_val & (1 << bit_idx)))

        # Write to state
        for i, value in enumerate(coil_values[:count]):
            coil = start_addr + i
            key, bool_value = shared_state.coil_to_state(coil, value)
            if key:
                shared_state.update_state(key, bool_value)
                print(f"[MODBUS] Updated {key} = {bool_value}")

        # Build response
        return struct.pack('>BHH', 0x0F, start_addr, count)

# Global Modbus server instance
modbus_server = None

def start_modbus_server():
    """Start Modbus TCP server in background thread"""
    global modbus_server
    modbus_server = ModbusTCPServer(host='0.0.0.0', port=5502)
    server_thread = threading.Thread(target=modbus_server.start, daemon=True)
    server_thread.start()
    print("[MODBUS] Background thread started")

# Initialize database
def init_db():
    conn = sqlite3.connect('plc.db')
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')

    # Insert default users (intentionally vulnerable)
    c.execute("DELETE FROM users")
    c.execute("INSERT INTO users VALUES (1, 'admin', 'admin', 'admin')")
    c.execute("INSERT INTO users VALUES (2, 'operator', 'operator123', 'operator')")
    c.execute("INSERT INTO users VALUES (3, 'guest', 'guest', 'guest')")

    # PLC data table
    c.execute('''CREATE TABLE IF NOT EXISTS plc_data
                 (id INTEGER PRIMARY KEY, register TEXT, value INTEGER, timestamp TEXT)''')

    # Logs table
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY, timestamp TEXT, user TEXT, action TEXT, details TEXT)''')

    conn.commit()
    conn.close()

def log_action(user, action, details):
    """Log user actions"""
    conn = sqlite3.connect('plc.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO logs (timestamp, user, action, details) VALUES (?, ?, ?, ?)",
              (timestamp, user, action, details))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # VULNERABILITY: SQL Injection
        # Intentionally vulnerable query - no parameterization
        # Multiple ways to exploit:
        # 1. admin' OR '1'='1' --
        # 2. admin' OR 1=1 --
        # 3. ' OR ''='
        # 4. admin'--
        conn = sqlite3.connect('plc.db')
        c = conn.cursor()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"

        try:
            print(f"[SQL] Executing: {query}")  # Debug output
            c.execute(query)
            user = c.fetchone()
            print(f"[SQL] Result: {user}")  # Debug output

            if user:
                session['username'] = user[1]
                session['role'] = user[3]
                session['user_id'] = user[0]
                log_action(user[1], 'login', 'Successful login')
                conn.close()
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid credentials'
                if username:
                    log_action(username, 'login_failed', 'Failed login attempt')

            conn.close()
        except Exception as e:
            error = f'Database error: {str(e)}'
            print(f"[SQL] Error: {str(e)}")
            conn.close()

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    user = session.get('username', 'unknown')
    log_action(user, 'logout', 'User logged out')
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html',
                          username=session['username'],
                          role=session['role'])

@app.route('/admin')
@require_role('admin')
def admin():
    """Admin panel - requires admin role"""
    return render_template('admin.html',
                          username=session['username'],
                          role=session['role'])

@app.route('/admin/users')
@require_role('admin')
def admin_users():
    """View users - admin only"""
    conn = sqlite3.connect('plc.db')
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users")
    users = c.fetchall()
    conn.close()

    return render_template('users.html', users=users)

@app.route('/admin/users/add', methods=['POST'])
@require_role('admin')
def admin_add_user():
    """Add new user - admin only"""
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    role = request.form.get('role', 'guest')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    conn = sqlite3.connect('plc.db')
    c = conn.cursor()

    try:
        # VULNERABILITY: Password stored in plaintext
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                 (username, password, role))
        conn.commit()
        log_action(session['username'], 'add_user', f'Added user: {username} with role: {role}')
        conn.close()
        return jsonify({'success': True, 'message': f'User {username} added successfully'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username already exists'}), 400
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@require_role('admin')
def admin_delete_user(user_id):
    """Delete user - admin only"""
    conn = sqlite3.connect('plc.db')
    c = conn.cursor()

    # Get username before deleting
    c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()

    if not result:
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    username = result[0]

    # VULNERABILITY: No check to prevent deleting own account
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    log_action(session['username'], 'delete_user', f'Deleted user: {username}')
    return jsonify({'success': True, 'message': f'User {username} deleted'})

@app.route('/admin/users/edit/<int:user_id>', methods=['POST'])
@require_role('admin')
def admin_edit_user(user_id):
    """Edit user role - admin only"""
    new_role = request.form.get('role', '')

    if new_role not in ['admin', 'operator', 'guest']:
        return jsonify({'error': 'Invalid role'}), 400

    conn = sqlite3.connect('plc.db')
    c = conn.cursor()

    # Get username before editing
    c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()

    if not result:
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    username = result[0]

    # VULNERABILITY: No check to prevent demoting own admin account
    c.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()

    log_action(session['username'], 'edit_user', f'Changed {username} role to {new_role}')
    return jsonify({'success': True, 'message': f'User {username} updated to {new_role}'})

@app.route('/admin/logs')
@require_role('admin')
def admin_logs():
    """View all logs - admin only"""
    conn = sqlite3.connect('plc.db')
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 100")
    logs = c.fetchall()
    conn.close()

    return render_template('logs.html', logs=logs)

@app.route('/operator/logs')
@require_role('admin', 'operator')
def operator_logs():
    """View own logs - operator can only see their own actions"""
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('plc.db')
    c = conn.cursor()

    # VULNERABILITY: SQL Injection in user filter (blind SQLi)
    username = session.get('username', '')
    query = f"SELECT * FROM logs WHERE user='{username}' ORDER BY id DESC LIMIT 100"

    try:
        c.execute(query)
        logs = c.fetchall()
    except:
        logs = []

    conn.close()

    return render_template('operator_logs.html',
                          logs=logs,
                          username=session.get('username'),
                          role=session.get('role'))

@app.route('/admin/system')
@require_role('admin')
def admin_system():
    """System control - admin only"""
    return render_template('system.html')

@app.route('/admin/exec', methods=['POST'])
@require_role('admin')
def admin_exec():
    """VULNERABILITY: Command Injection - admin only"""
    command = request.form.get('command', '')

    try:
        # VULNERABILITY: No input validation - direct command execution
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=5)
        output = result.decode('utf-8')
        log_action(session['username'], 'exec_command', command)
        return jsonify({'output': output})
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Command timed out'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/plc/status')
def plc_status():
    """Get PLC status"""
    return jsonify({
        'status': 'running',
        'model': 'VulnPLC-3000',
        'firmware': '1.0.0',
        'uptime': '42 days',
        'modbus_port': 5502,
        'registers': 100
    })

@app.route('/api/plc/read/<int:register>')
def plc_read(register):
    """Read PLC register"""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    # Simulate reading from Modbus
    conn = sqlite3.connect('plc.db')
    c = conn.cursor()
    c.execute("SELECT value FROM plc_data WHERE register=?", (str(register),))
    result = c.fetchone()
    conn.close()

    if result:
        value = result[0]
    else:
        value = 0

    return jsonify({'register': register, 'value': value})

@app.route('/api/plc/write/<int:register>/<int:value>')
@require_role('admin', 'operator')
def plc_write(register, value):
    """Write to PLC register - operator and admin only"""
    conn = sqlite3.connect('plc.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT OR REPLACE INTO plc_data VALUES (?, ?, ?, ?)",
              (register, str(register), value, timestamp))
    conn.commit()
    conn.close()

    log_action(session['username'], 'write_register', f'Register {register} = {value}')

    return jsonify({'success': True, 'register': register, 'value': value})

@app.route('/debug')
def debug():
    """VULNERABILITY: Information disclosure"""
    info = {
        'session': dict(session),
        'environment': dict(os.environ),
        'secret_key': app.secret_key,
        'debug_mode': app.debug
    }
    return jsonify(info)

@app.route('/backup/<path:filename>')
def backup(filename):
    """VULNERABILITY: Directory traversal"""
    # No path validation - allows reading arbitrary files
    try:
        with open(filename, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error: {str(e)}", 404

@app.route('/hmi')
def hmi():
    """HMI (Human-Machine Interface) - Real-time monitoring"""
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('hmi.html',
                          username=session['username'],
                          role=session['role'])

@app.route('/scada')
def scada():
    """SCADA Dashboard with process overview"""
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('scada.html',
                          username=session['username'],
                          role=session['role'])

@app.route('/process')
def process():
    """Process control interface"""
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('process.html',
                          username=session['username'],
                          role=session['role'])

@app.route('/alarms')
def alarms():
    """Alarm management interface"""
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('alarms.html',
                          username=session['username'],
                          role=session['role'])

@app.route('/trending')
def trending():
    """Historical data trending"""
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('trending.html',
                          username=session['username'],
                          role=session['role'])

@app.route('/api/process/status')
def process_status():
    """Get current process status"""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    # Simulate Tank 1 changes
    PROCESS_STATE['tank1_level'] += random.uniform(-2, 2)
    PROCESS_STATE['tank1_level'] = max(0, min(100, PROCESS_STATE['tank1_level']))

    PROCESS_STATE['tank1_temp'] += random.uniform(-0.5, 0.5)
    PROCESS_STATE['tank1_temp'] = max(20, min(100, PROCESS_STATE['tank1_temp']))

    PROCESS_STATE['tank1_pressure'] += random.uniform(-1, 1)
    PROCESS_STATE['tank1_pressure'] = max(90, min(150, PROCESS_STATE['tank1_pressure']))

    # Simulate Tank 2 changes
    PROCESS_STATE['tank2_level'] += random.uniform(-1.5, 1.5)
    PROCESS_STATE['tank2_level'] = max(0, min(100, PROCESS_STATE['tank2_level']))

    PROCESS_STATE['tank2_temp'] += random.uniform(-0.3, 0.3)
    PROCESS_STATE['tank2_temp'] = max(20, min(100, PROCESS_STATE['tank2_temp']))

    # Simulate sensor changes
    PROCESS_STATE['flow_rate'] += random.uniform(-2, 2)
    PROCESS_STATE['flow_rate'] = max(0, min(50, PROCESS_STATE['flow_rate']))

    PROCESS_STATE['vibration'] += random.uniform(-0.5, 0.5)
    PROCESS_STATE['vibration'] = max(0, min(10, PROCESS_STATE['vibration']))

    PROCESS_STATE['ph_level'] += random.uniform(-0.2, 0.2)
    PROCESS_STATE['ph_level'] = max(0, min(14, PROCESS_STATE['ph_level']))

    # Check for alarm conditions
    if PROCESS_STATE['tank1_level'] > 90:
        add_alarm('HIGH', 'Tank 1 level critically high')
    if PROCESS_STATE['tank1_level'] < 10:
        add_alarm('HIGH', 'Tank 1 level critically low')
    if PROCESS_STATE['tank1_temp'] > 80:
        add_alarm('MEDIUM', 'Tank 1 temperature high')
    if PROCESS_STATE['tank1_pressure'] > 140:
        add_alarm('HIGH', 'Tank 1 pressure too high')
    if PROCESS_STATE['tank2_level'] > 95:
        add_alarm('HIGH', 'Tank 2 overflow risk')
    if PROCESS_STATE['vibration'] > 8:
        add_alarm('MEDIUM', 'High vibration detected')
    if PROCESS_STATE['emergency_stop']:
        add_alarm('HIGH', 'EMERGENCY STOP ACTIVATED')

    # Return formatted data for HMI
    response = {
        'tank_level': PROCESS_STATE['tank1_level'],
        'temperature': PROCESS_STATE['tank1_temp'],
        'pressure': PROCESS_STATE['tank1_pressure'],
        'flow_rate': PROCESS_STATE['flow_rate'],
        'pump_status': PROCESS_STATE['pump1_status'],
        'valve_status': PROCESS_STATE['valve1_status'],
        # Include full state for advanced access (convert proxy to dict)
        'full_state': shared_state.load_state()
    }

    return jsonify(response)

@app.route('/api/process/control', methods=['POST'])
@require_role('admin', 'operator')
def process_control():
    """Control process equipment - operator and admin only"""
    data = request.get_json()
    action = data.get('action')
    value = data.get('value')

    # HMI simplified controls
    if action == 'pump':
        PROCESS_STATE['pump1_status'] = value
        log_action(session['username'], 'control_pump', f'Pump set to {value}')
    elif action == 'valve':
        PROCESS_STATE['valve1_status'] = value
        log_action(session['username'], 'control_valve', f'Valve set to {value}')
    elif action == 'reset_tank':
        PROCESS_STATE['tank1_level'] = 50.0
        PROCESS_STATE['tank1_temp'] = 25.0
        PROCESS_STATE['tank1_pressure'] = 101.3
        log_action(session['username'], 'reset_tank', 'Tank reset to defaults')

    # Pumps
    elif action == 'pump1_status':
        PROCESS_STATE['pump1_status'] = value
        log_action(session['username'], 'control_pump1', f'Pump 1 set to {value}')
    elif action == 'pump2_status':
        PROCESS_STATE['pump2_status'] = value
        log_action(session['username'], 'control_pump2', f'Pump 2 set to {value}')
    elif action == 'pump3_status':
        PROCESS_STATE['pump3_status'] = value
        log_action(session['username'], 'control_pump3', f'Pump 3 set to {value}')

    # Pump speeds
    elif action == 'pump1_speed':
        PROCESS_STATE['pump1_speed'] = int(value)
        log_action(session['username'], 'control_pump1_speed', f'Pump 1 speed set to {value}')
    elif action == 'pump2_speed':
        PROCESS_STATE['pump2_speed'] = int(value)
        log_action(session['username'], 'control_pump2_speed', f'Pump 2 speed set to {value}')

    # Valves
    elif action == 'valve1_status':
        PROCESS_STATE['valve1_status'] = value
        log_action(session['username'], 'control_valve1', f'Valve 1 set to {value}')
    elif action == 'valve2_status':
        PROCESS_STATE['valve2_status'] = value
        log_action(session['username'], 'control_valve2', f'Valve 2 set to {value}')
    elif action == 'valve3_status':
        PROCESS_STATE['valve3_status'] = value
        log_action(session['username'], 'control_valve3', f'Valve 3 (Emergency) set to {value}')
    elif action == 'valve4_status':
        PROCESS_STATE['valve4_status'] = value
        log_action(session['username'], 'control_valve4', f'Valve 4 (Bypass) set to {value}')

    # Motors
    elif action == 'motor1_speed':
        PROCESS_STATE['motor1_speed'] = int(value)
        log_action(session['username'], 'control_motor1', f'Motor 1 speed set to {value}')
    elif action == 'motor2_speed':
        PROCESS_STATE['motor2_speed'] = int(value)
        log_action(session['username'], 'control_motor2', f'Motor 2 speed set to {value}')

    # Heaters/Coolers
    elif action == 'heater1_status':
        PROCESS_STATE['heater1_status'] = value
        log_action(session['username'], 'control_heater', f'Heater set to {value}')
    elif action == 'cooler1_status':
        PROCESS_STATE['cooler1_status'] = value
        log_action(session['username'], 'control_cooler', f'Cooler set to {value}')

    # Conveyor
    elif action == 'conveyor_status':
        PROCESS_STATE['conveyor_status'] = value
        log_action(session['username'], 'control_conveyor', f'Conveyor set to {value}')
    elif action == 'conveyor_speed':
        PROCESS_STATE['conveyor_speed'] = int(value)
        log_action(session['username'], 'control_conveyor_speed', f'Conveyor speed set to {value}')

    # Safety
    elif action == 'emergency_stop':
        PROCESS_STATE['emergency_stop'] = value
        log_action(session['username'], 'emergency_stop', f'Emergency stop set to {value}')
    elif action == 'safety_interlock':
        PROCESS_STATE['safety_interlock'] = value
        log_action(session['username'], 'safety_interlock', f'Safety interlock set to {value}')

    # Tank reset
    elif action == 'reset_tank1':
        PROCESS_STATE['tank1_level'] = 50.0
        log_action(session['username'], 'reset_tank1', 'Tank 1 level reset')
    elif action == 'reset_tank2':
        PROCESS_STATE['tank2_level'] = 50.0
        log_action(session['username'], 'reset_tank2', 'Tank 2 level reset')

    return jsonify({'success': True, 'state': shared_state.load_state()})

@app.route('/api/alarms/list')
def alarms_list():
    """Get active alarms"""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    return jsonify({'alarms': PROCESS_STATE['alarms']})

@app.route('/api/alarms/acknowledge', methods=['POST'])
@require_role('admin', 'operator')
def alarms_acknowledge():
    """Acknowledge an alarm - operator and admin only"""
    data = request.get_json()
    alarm_id = data.get('id')

    # Remove alarm
    PROCESS_STATE['alarms'] = [a for a in PROCESS_STATE['alarms'] if a['id'] != alarm_id]
    log_action(session['username'], 'ack_alarm', f'Acknowledged alarm {alarm_id}')

    return jsonify({'success': True})

@app.route('/api/trending/data')
def trending_data():
    """Get historical trending data"""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    # Generate fake historical data
    hours = 24
    data = {
        'timestamps': [],
        'tank_level': [],
        'temperature': [],
        'pressure': [],
        'flow_rate': []
    }

    now = datetime.now()
    for i in range(hours * 6):  # Every 10 minutes
        time = now - timedelta(minutes=i*10)
        data['timestamps'].insert(0, time.strftime('%H:%M'))
        data['tank_level'].insert(0, 50 + random.uniform(-20, 20))
        data['temperature'].insert(0, 25 + random.uniform(-5, 15))
        data['pressure'].insert(0, 101 + random.uniform(-10, 10))
        data['flow_rate'].insert(0, 15 + random.uniform(-5, 10))

    return jsonify(data)

def add_alarm(severity, message):
    """Add an alarm to the system"""
    # Get current alarms list
    current_alarms = PROCESS_STATE.get('alarms', [])

    alarm = {
        'id': len(current_alarms) + 1,
        'severity': severity,
        'message': message,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'acknowledged': False
    }

    # Don't duplicate alarms
    if not any(a['message'] == message for a in current_alarms):
        current_alarms.append(alarm)
        # Write back the modified list to persist changes
        PROCESS_STATE['alarms'] = current_alarms

# ============================================
# ADDITIONAL VULNERABILITIES FOR TESTING
# ============================================

@app.route('/api/search')
def search():
    """VULNERABILITY: Reflected XSS"""
    query = request.args.get('q', '')
    # No sanitization - direct output
    return f"""
    <html>
    <body>
    <h1>Search Results</h1>
    <p>You searched for: {query}</p>
    <p>No results found.</p>
    </body>
    </html>
    """

@app.route('/api/comment', methods=['POST'])
def comment():
    """VULNERABILITY: Stored XSS"""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    comment_text = request.form.get('comment', '')
    # Store in database without sanitization
    conn = sqlite3.connect('plc.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY, user TEXT, comment TEXT, timestamp TEXT)")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO comments (user, comment, timestamp) VALUES (?, ?, ?)",
              (session['username'], comment_text, timestamp))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Comment added'})

@app.route('/api/comments')
def comments():
    """Display comments with XSS vulnerability"""
    conn = sqlite3.connect('plc.db')
    c = conn.cursor()
    try:
        c.execute("SELECT user, comment, timestamp FROM comments ORDER BY id DESC LIMIT 50")
        comments_list = c.fetchall()
    except:
        comments_list = []
    conn.close()

    html = "<html><body><h1>Comments</h1>"
    for user, comment, timestamp in comments_list:
        # VULNERABILITY: No escaping
        html += f"<div><strong>{user}</strong> ({timestamp}): {comment}</div>"
    html += "</body></html>"

    return html

@app.route('/api/upload', methods=['POST'])
@require_role('admin', 'operator')
def upload_file():
    """VULNERABILITY: Unrestricted file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # VULNERABILITY: No file type validation, no sanitization
    upload_dir = 'uploads'
    os.makedirs(upload_dir, exist_ok=True)

    # Directly use user-provided filename (dangerous)
    filepath = os.path.join(upload_dir, file.filename)
    file.save(filepath)

    log_action(session['username'], 'file_upload', f'Uploaded {file.filename}')

    return jsonify({
        'success': True,
        'filename': file.filename,
        'path': filepath
    })

@app.route('/api/download/<path:filename>')
def download_file(filename):
    """VULNERABILITY: Path traversal in file download"""
    # No path validation - allows directory traversal
    try:
        with open(filename, 'rb') as f:
            content = f.read()
        return content
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/user/<int:user_id>')
def get_user(user_id):
    """VULNERABILITY: Insecure Direct Object Reference (IDOR)"""
    # No authorization check - any logged in user can view any user
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    conn = sqlite3.connect('plc.db')
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({
            'id': user[0],
            'username': user[1],
            'role': user[2]
        })
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/modify_user', methods=['POST'])
def modify_user():
    """VULNERABILITY: Mass assignment / IDOR"""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    # VULNERABILITY: No authorization check, accepts user_id from request
    user_id = request.form.get('user_id')
    new_role = request.form.get('role')

    conn = sqlite3.connect('plc.db')
    c = conn.cursor()
    c.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
    conn.commit()
    conn.close()

    log_action(session['username'], 'modify_user', f'Modified user {user_id} to role {new_role}')

    return jsonify({'success': True, 'message': f'User {user_id} updated to {new_role}'})

@app.route('/api/xml', methods=['POST'])
def parse_xml():
    """VULNERABILITY: XML External Entity (XXE)"""
    xml_data = request.data.decode('utf-8')

    try:
        import xml.etree.ElementTree as ET
        # VULNERABILITY: No protection against XXE
        root = ET.fromstring(xml_data)
        return jsonify({
            'success': True,
            'data': ET.tostring(root, encoding='unicode')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/eval', methods=['POST'])
@require_role('admin')
def eval_code():
    """VULNERABILITY: Code injection / eval()"""
    code = request.form.get('code', '')

    try:
        # EXTREMELY DANGEROUS - Never do this in real code
        result = eval(code)
        log_action(session['username'], 'eval_code', f'Evaluated: {code}')
        return jsonify({'success': True, 'result': str(result)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/modbus/raw', methods=['POST'])
def modbus_raw():
    """VULNERABILITY: Unauthenticated Modbus control"""
    # No authentication required for raw Modbus commands
    register = request.form.get('register', 0, type=int)
    value = request.form.get('value', 0, type=int)

    # Direct register manipulation without authorization
    PROCESS_STATE['api_access_count'] = PROCESS_STATE.get('api_access_count', 0) + 1

    log_action('ANONYMOUS', 'modbus_raw', f'Register {register} = {value}')

    return jsonify({
        'success': True,
        'register': register,
        'value': value,
        'message': 'Raw Modbus command executed (unauthenticated)'
    })

@app.route('/api/keys')
def get_api_keys():
    """VULNERABILITY: Exposed API keys"""
    # Returns sensitive keys without authentication
    return jsonify({
        'api_key': PROCESS_STATE['api_key'],
        'secret_token': PROCESS_STATE['secret_token'],
        'database_path': 'plc.db',
        'secret_key': app.secret_key
    })

@app.route('/api/ping')
def ping():
    """VULNERABILITY: Command injection via ping"""
    host = request.args.get('host', 'localhost')

    try:
        # VULNERABILITY: No input validation
        result = subprocess.check_output(f'ping -c 1 {host}', shell=True, stderr=subprocess.STDOUT, timeout=5)
        return jsonify({'success': True, 'output': result.decode('utf-8')})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ============================================
# ADVANCED VULNERABILITIES (TRICKY EXPLOITATION)
# ============================================

@app.route('/operator/report', methods=['GET', 'POST'])
@require_role('admin', 'operator')
def generate_report():
    """VULNERABILITY: Server-Side Template Injection (SSTI)"""
    if request.method == 'POST':
        from jinja2 import Template

        report_title = request.form.get('title', 'System Report')
        report_type = request.form.get('type', 'summary')

        # VULNERABILITY: Direct template rendering from user input
        template_string = request.form.get('template', '')

        if not template_string:
            # Default template
            template_string = """
            <html>
            <body>
            <h1>{{ title }}</h1>
            <p>Report Type: {{ type }}</p>
            <p>Generated by: {{ user }}</p>
            <p>Timestamp: {{ timestamp }}</p>
            </body>
            </html>
            """

        try:
            # VULNERABILITY: User-controlled template - SSTI
            template = Template(template_string)
            rendered = template.render(
                title=report_title,
                type=report_type,
                user=session.get('username'),
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            log_action(session['username'], 'generate_report', f'Generated {report_type} report')

            return rendered
        except Exception as e:
            return f"Error rendering template: {str(e)}", 400

    return render_template('report.html',
                          username=session.get('username'),
                          role=session.get('role'))

@app.route('/operator/search')
@require_role('admin', 'operator')
def search_logs():
    """VULNERABILITY: Blind SQL Injection in search"""
    search_term = request.args.get('q', '')
    search_type = request.args.get('type', 'action')

    # If no search term, show search form
    if not search_term:
        return render_template('search.html')

    conn = sqlite3.connect('plc.db')
    c = conn.cursor()

    # VULNERABILITY: Blind SQL Injection
    # Operator can search logs, but query is vulnerable
    if search_type == 'action':
        query = f"SELECT COUNT(*) FROM logs WHERE action LIKE '%{search_term}%'"
    elif search_type == 'user':
        query = f"SELECT COUNT(*) FROM logs WHERE user LIKE '%{search_term}%'"
    else:
        query = f"SELECT COUNT(*) FROM logs WHERE details LIKE '%{search_term}%'"

    try:
        print(f"[SEARCH] Executing: {query}")
        c.execute(query)
        count = c.fetchone()[0]
        conn.close()

        # Return JSON if it looks like an API request
        if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
            return jsonify({
                'success': True,
                'query': search_term,
                'type': search_type,
                'results': count,
                'message': f'Found {count} results'
            })
        else:
            # Return HTML page
            return render_template('search.html', results=count, query=search_term, search_type=search_type)
    except Exception as e:
        conn.close()
        if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
            return jsonify({'error': str(e)}), 400
        else:
            return render_template('search.html', error=str(e), query=search_term)

@app.route('/operator/export', methods=['GET', 'POST'])
@require_role('admin', 'operator')
def export_data():
    """VULNERABILITY: Insecure Deserialization"""
    if request.method == 'GET':
        return render_template('operator_export.html',
                              username=session.get('username'),
                              role=session.get('role'))

    import pickle
    import base64

    export_type = request.form.get('type', 'logs')

    # Create export data
    if export_type == 'logs':
        conn = sqlite3.connect('plc.db')
        c = conn.cursor()
        c.execute(f"SELECT * FROM logs WHERE user='{session.get('username')}' LIMIT 50")
        data = c.fetchall()
        conn.close()
    elif export_type == 'alarms':
        data = PROCESS_STATE.get('alarms', [])
    else:
        data = {'error': 'Invalid export type'}

    # VULNERABILITY: Pickle serialization exposes attack surface
    pickled = pickle.dumps(data)
    encoded = base64.b64encode(pickled).decode('utf-8')

    log_action(session['username'], 'export_data', f'Exported {export_type}')

    # Return JSON for API calls, HTML for browser
    if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        return jsonify({
            'success': True,
            'export_type': export_type,
            'data': encoded,
            'format': 'base64-pickle'
        })
    else:
        return render_template('operator_export.html',
                              username=session.get('username'),
                              role=session.get('role'),
                              export_data=encoded)

@app.route('/operator/import', methods=['POST'])
@require_role('admin', 'operator')
def import_data():
    """VULNERABILITY: Insecure Deserialization - RCE vector"""
    import pickle
    import base64

    encoded_data = request.form.get('data', '')

    try:
        # VULNERABILITY: Unpickling user-controlled data - RCE!
        decoded = base64.b64decode(encoded_data)
        data = pickle.loads(decoded)

        log_action(session['username'], 'import_data', 'Imported data')

        records = len(data) if isinstance(data, (list, dict)) else 1

        # Return JSON for API calls, HTML for browser
        if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
            return jsonify({
                'success': True,
                'message': 'Data imported successfully',
                'records': records
            })
        else:
            return render_template('operator_export.html',
                                  username=session.get('username'),
                                  role=session.get('role'),
                                  import_result=f'Successfully imported {records} records')
    except Exception as e:
        if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
            return jsonify({'error': str(e)}), 400
        else:
            return render_template('operator_export.html',
                                  username=session.get('username'),
                                  role=session.get('role'),
                                  error=str(e))

@app.route('/operator/config', methods=['GET', 'POST'])
@require_role('admin', 'operator')
def operator_config():
    """VULNERABILITY: Mass Assignment + Configuration Injection"""
    if request.method == 'POST':
        # VULNERABILITY: Accepts any configuration parameters
        config = {}

        # Check for custom parameters (mass assignment vuln)
        custom_key = request.form.get('custom_key', '')
        custom_value = request.form.get('custom_value', '')

        if custom_key and custom_value:
            # VULNERABILITY: Direct assignment of any key-value pair
            config[custom_key] = custom_value
        else:
            # Normal form fields
            for key, value in request.form.items():
                if key not in ['custom_key', 'custom_value']:
                    config[key] = value

        # Store in session (dangerous - can override role, username, etc.)
        for key, value in config.items():
            session[key] = value

        log_action(session['username'], 'update_config', f'Updated config: {list(config.keys())}')

        # Return JSON for API calls, HTML for browser
        if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
            return jsonify({
                'success': True,
                'message': 'Configuration updated',
                'config': config
            })
        else:
            return render_template('operator_config.html',
                                  username=session.get('username'),
                                  role=session.get('role'),
                                  current_config=dict(session),
                                  success=True)

    # GET request - show form
    return render_template('operator_config.html',
                          username=session.get('username'),
                          role=session.get('role'),
                          current_config=dict(session))

@app.route('/operator/webhook', methods=['POST'])
@require_role('admin', 'operator')
def webhook():
    """VULNERABILITY: SSRF (Server-Side Request Forgery)"""
    webhook_url = request.form.get('url', '')
    event_type = request.form.get('event', 'alarm')

    # VULNERABILITY: No URL validation - can hit internal services
    try:
        import requests as req
        payload = {
            'event': event_type,
            'user': session.get('username'),
            'timestamp': datetime.now().isoformat()
        }

        # SSRF - operator can make server request any URL
        response = req.post(webhook_url, json=payload, timeout=5)

        log_action(session['username'], 'webhook_call', f'Called webhook: {webhook_url}')

        return jsonify({
            'success': True,
            'status_code': response.status_code,
            'response': response.text[:500]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/operator/token', methods=['GET', 'POST'])
@require_role('admin', 'operator')
def get_token():
    """VULNERABILITY: Weak JWT-like token generation"""
    import hashlib
    import time

    if request.method == 'POST':
        # VULNERABILITY: Predictable token generation
        user = session.get('username')
        role = session.get('role')
        timestamp = str(int(time.time()))

        # Weak token: just MD5 hash of predictable data
        token_data = f"{user}:{role}:{timestamp}"
        token = hashlib.md5(token_data.encode()).hexdigest()

        token_info = {
            'token': token,
            'username': user,
            'role': role,
            'timestamp': timestamp,
            'hint': 'Token format: md5(username:role:timestamp)'
        }

        # Return JSON for API calls, HTML for browser
        if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
            return jsonify({
                'success': True,
                **token_info
            })
        else:
            return render_template('operator_token.html',
                                  username=session.get('username'),
                                  role=session.get('role'),
                                  token_data=token_info)

    # GET request - show form
    return render_template('operator_token.html',
                          username=session.get('username'),
                          role=session.get('role'))

@app.route('/operator/validate', methods=['POST'])
def validate_token():
    """VULNERABILITY: Token validation bypass"""
    import hashlib

    token = request.form.get('token', '')
    username = request.form.get('username', '')
    role = request.form.get('role', '')

    # VULNERABILITY: Accepts any role if token format is correct
    # Can forge tokens by knowing the algorithm
    try:
        # Try to find valid timestamp (brute force window)
        import time
        current_time = int(time.time())

        for offset in range(-300, 300):  # 10 minute window
            check_time = str(current_time + offset)
            expected = hashlib.md5(f"{username}:{role}:{check_time}".encode()).hexdigest()

            if expected == token:
                # Valid token! Create session
                session['username'] = username
                session['role'] = role
                session['user_id'] = 999  # Fake ID

                result = {
                    'valid': True,
                    'message': f'Token validated successfully! Logged in as {username} with role {role}'
                }

                # Return JSON for API calls, HTML for browser
                if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
                    return jsonify({
                        'success': True,
                        'message': result['message'],
                        'username': username,
                        'role': role
                    })
                else:
                    return render_template('operator_token.html',
                                          username=username,
                                          role=role,
                                          validation_result=result)

        # Token not found in time window
        result = {
            'valid': False,
            'message': 'Invalid token or token expired'
        }

        if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
            return jsonify({'error': 'Invalid token'}), 401
        else:
            return render_template('operator_token.html',
                                  username=session.get('username', 'guest'),
                                  role=session.get('role', 'guest'),
                                  validation_result=result)
    except Exception as e:
        if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
            return jsonify({'error': str(e)}), 400
        else:
            result = {
                'valid': False,
                'message': f'Error validating token: {str(e)}'
            }
            return render_template('operator_token.html',
                                  username=session.get('username', 'guest'),
                                  role=session.get('role', 'guest'),
                                  validation_result=result)

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  Vulnerable Modbus PLC Simulator                          ║
    ║  FOR SECURITY TESTING AND EDUCATION ONLY                  ║
    ╚═══════════════════════════════════════════════════════════╝

    Default Credentials:
      admin / admin       (Administrator)
      operator / operator123 (Operator)
      guest / guest       (Guest)

    Web Interface: http://localhost:5000
    Modbus TCP:    localhost:5502

    Known Vulnerabilities:
      • SQL Injection in login
      • Default credentials
      • Command injection in admin panel
      • Directory traversal
      • Information disclosure
      • Insufficient access controls
      • Session hijacking
      • Unauthenticated Modbus access
      • No register bounds checking

    WARNING: DO NOT EXPOSE TO INTERNET
    """)

    # Initialize database
    init_db()

    # Start Modbus TCP server in background thread
    print("[STARTUP] Starting Modbus TCP server...")
    start_modbus_server()

    # Give Modbus server time to bind to port
    import time
    time.sleep(0.5)

    # Start Flask application (this blocks)
    print("[STARTUP] Starting Flask web interface...")
    app.run(host='0.0.0.0', port=5000, debug=True)
