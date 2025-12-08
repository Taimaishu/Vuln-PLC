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

    app.run(host='0.0.0.0', port=5012, debug=True)
