#!/usr/bin/env python3
"""
PLC-4: Safety/Emergency Shutdown System - Web Interface
Port 5013

INTENTIONALLY VULNERABLE - For security testing only
Vulnerabilities: Weak authentication, timing attacks, safety system bypass
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import time
import hashlib
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import shared_state

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'plc4-safety-weak-key-000'

shared_state.init_state()

# VULNERABILITY: Hardcoded safety credentials
SAFETY_USERS = {
    'safety_eng': 'safe123',
    'operator': 'esd456',
    'admin': 'admin'
}

# VULNERABILITY: Weak override code
SAFETY_OVERRIDE_CODE = '1234'

def get_plc4_state():
    state = shared_state.load_state()
    plc4_state = {}
    for key, value in state.items():
        if key.startswith('plc4_'):
            plc4_state[key.replace('plc4_', '')] = value
    return plc4_state

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """VULNERABILITY: Timing attack - username enumeration"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # VULNERABILITY: Timing attack reveals valid usernames
        if username in SAFETY_USERS:
            time.sleep(0.2)  # Intentional delay for valid users

            # VULNERABILITY: Password comparison is not constant-time
            correct_pass = SAFETY_USERS[username]
            if password == correct_pass:
                session['username'] = username
                session['plc_id'] = 4
                session['safety_clearance'] = True
                return redirect(url_for('dashboard'))
            else:
                time.sleep(0.1)  # Additional delay for wrong password
                error = 'Invalid password'
        else:
            # Fast response for invalid username
            error = 'Invalid credentials'

    return render_template('plc4_login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    plc_state = get_plc4_state()
    return render_template('plc4_dashboard.html',
                          username=session['username'],
                          state=plc_state)

@app.route('/api/status')
def api_status():
    plc_state = get_plc4_state()
    return jsonify({
        'plc_id': 4,
        'name': 'Safety/ESD System',
        'status': 'armed' if plc_state.get('safety_system_armed') else 'disarmed',
        'state': plc_state
    })

@app.route('/api/control', methods=['POST'])
def api_control():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or request.form.to_dict()
    action = data.get('action')
    value = data.get('value')

    # Emergency stops
    if action in ['emergency_stop_1', 'emergency_stop_2', 'emergency_stop_3', 'master_emergency_stop']:
        shared_state.update_state(f'plc4_{action}', value in ['true', 'True', True, 1, '1'])

    # Safety interlocks
    elif action in ['safety_interlock_1', 'safety_interlock_2', 'safety_interlock_3']:
        shared_state.update_state(f'plc4_{action}', value in ['true', 'True', True, 1, '1'])

    # Fire/Gas detection
    elif action in ['fire_detection_zone1', 'fire_detection_zone2', 'fire_detection_zone3']:
        shared_state.update_state(f'plc4_{action}', value in ['true', 'True', True, 1, '1'])
    elif action in ['gas_detection_zone1', 'gas_detection_zone2']:
        shared_state.update_state(f'plc4_{action}', value in ['true', 'True', True, 1, '1'])

    # Fire suppression & evacuation
    elif action in ['fire_suppression_active', 'evacuation_alarm']:
        shared_state.update_state(f'plc4_{action}', value in ['true', 'True', True, 1, '1'])

    # VULNERABILITY: Safety bypass can be enabled without additional checks
    elif action == 'safety_bypass_mode':
        shared_state.update_state('plc4_safety_bypass_mode', value in ['true', 'True', True, 1, '1'])
        if value:
            return jsonify({
                'success': True,
                'warning': 'SAFETY BYPASS ENABLED - All safety systems disabled!',
                'action': action
            })

    # Watchdog
    elif action == 'watchdog_enabled':
        shared_state.update_state('plc4_watchdog_enabled', value in ['true', 'True', True, 1, '1'])

    elif action == 'reset_watchdog':
        shared_state.update_state('plc4_watchdog_counter', 0)

    elif action == 'reset_all_alarms':
        shared_state.update_state('plc4_master_emergency_stop', False)
        shared_state.update_state('plc4_evacuation_alarm', False)
        shared_state.update_state('plc4_fire_suppression_active', False)

    return jsonify({'success': True, 'action': action, 'value': value})

@app.route('/api/safety_override', methods=['POST'])
def safety_override():
    """VULNERABILITY: Weak override code allows safety bypass"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    override_code = request.form.get('code', '')

    # VULNERABILITY: Simple string comparison, weak code
    if override_code == SAFETY_OVERRIDE_CODE:
        # Reset watchdog and enable bypass
        shared_state.update_state('plc4_watchdog_counter', 0)
        shared_state.update_state('plc4_safety_bypass_mode', True)
        shared_state.update_state('plc4_system_healthy', True)

        return jsonify({
            'success': True,
            'message': 'Safety override accepted - All safety systems bypassed',
            'warning': 'CRITICAL: Safety systems are now disabled!'
        })
    else:
        # VULNERABILITY: Response reveals if code is close
        if override_code.startswith('12'):
            return jsonify({
                'error': 'Invalid code',
                'hint': 'Code starts correctly...'
            }), 401
        else:
            return jsonify({'error': 'Invalid override code'}), 401

@app.route('/api/emergency_shutdown', methods=['POST'])
def emergency_shutdown():
    """Trigger full emergency shutdown"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Activate all emergency stops
    shared_state.update_state('plc4_master_emergency_stop', True)
    shared_state.update_state('plc4_emergency_stop_1', True)
    shared_state.update_state('plc4_emergency_stop_2', True)
    shared_state.update_state('plc4_emergency_stop_3', True)
    shared_state.update_state('plc4_evacuation_alarm', True)

    # Also trigger emergency stops on other PLCs
    shared_state.update_state('plc2_emergency_vent', True)
    shared_state.update_state('plc3_thermal_runaway', False)

    return jsonify({
        'success': True,
        'message': 'EMERGENCY SHUTDOWN ACTIVATED',
        'affected_systems': ['PLC-1', 'PLC-2', 'PLC-3', 'PLC-4']
    })

@app.route('/api/simulate_incident', methods=['POST'])
def simulate_incident():
    """VULNERABILITY: Allows simulating various incidents for testing"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    incident_type = request.form.get('type', 'fire')

    if incident_type == 'fire':
        shared_state.update_state('plc4_fire_detection_zone1', True)
        shared_state.update_state('plc4_fire_detection_zone2', True)
        return jsonify({'success': True, 'incident': 'Fire detected in zones 1 and 2'})

    elif incident_type == 'gas':
        shared_state.update_state('plc4_gas_detection_zone1', True)
        return jsonify({'success': True, 'incident': 'Gas leak detected in zone 1'})

    elif incident_type == 'multiple':
        shared_state.update_state('plc4_fire_detection_zone1', True)
        shared_state.update_state('plc4_gas_detection_zone2', True)
        shared_state.update_state('plc4_emergency_stop_1', True)
        return jsonify({'success': True, 'incident': 'Multiple simultaneous incidents'})

    return jsonify({'error': 'Invalid incident type'}), 400

@app.route('/api/audit_log')
def audit_log():
    """Get safety audit log"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Simulate audit log entries
    logs = [
        {'timestamp': '2024-12-07 10:30:15', 'event': 'System armed', 'user': 'safety_eng'},
        {'timestamp': '2024-12-07 10:35:22', 'event': 'Watchdog reset', 'user': 'operator'},
        {'timestamp': '2024-12-07 10:40:10', 'event': 'Safety bypass enabled', 'user': 'admin'},
        {'timestamp': '2024-12-07 10:41:33', 'event': 'Emergency stop triggered', 'user': 'operator'},
        {'timestamp': '2024-12-07 10:45:00', 'event': 'System reset', 'user': 'safety_eng'},
    ]

    return jsonify({'logs': logs})

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  PLC-4: Safety/Emergency Shutdown System                  ║
    ║  FOR SECURITY TESTING AND EDUCATION ONLY                  ║
    ╚═══════════════════════════════════════════════════════════╝

    Default Credentials:
      safety_eng / safe123
      operator / esd456
      admin / admin

    Safety Override Code: 1234

    Web Interface: http://localhost:5013
    Modbus TCP:    localhost:5505

    Known Vulnerabilities:
      • Timing attacks in authentication
      • Weak safety override code (1234)
      • Safety bypass can be enabled remotely
      • No multi-factor authentication for critical functions
      • Watchdog can be disabled
      • Information disclosure in failed override attempts

    CRITICAL WARNING:
      This is a SAFETY SYSTEM simulator. In real systems, these
      vulnerabilities would be catastrophic and potentially fatal.
      DO NOT EXPOSE TO INTERNET.
    """)

    app.run(host='0.0.0.0', port=5013, debug=True)
