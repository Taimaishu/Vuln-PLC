#!/usr/bin/env python3
"""
HMI (Human-Machine Interface) Server
Visual SCADA interface with P&ID diagrams and real-time process data

Features:
- Live process visualization (tank levels, pressures, temperatures)
- Animated equipment (pumps, valves, compressors)
- Alarm panels with priority indicators
- Trend charts for historical data
- Control buttons for operators
"""

import os
import sys
import time
import logging
from flask import Flask, render_template, jsonify, request
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import shared_state

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'hmi-secret-key-change-in-production'

# Initialize shared state
shared_state.init_state()


@app.route('/')
def index():
    """Main HMI dashboard"""
    return render_template('hmi_dashboard.html')


@app.route('/api/process_data')
def get_process_data():
    """Get current process data for all systems"""
    data = {
        'timestamp': time.time(),

        # Tank System (PLC-1)
        'tank': {
            'level': shared_state.get_state('physical_tank_level', 50.0),
            'pump_running': shared_state.get_state('plc1_pump_status', False),
            'valve_position': shared_state.get_state('plc1_valve_position', 50.0),
            'overflow': shared_state.get_state('physical_tank_level', 0) > 95,
            'low_level': shared_state.get_state('physical_tank_level', 0) < 10
        },

        # Pressure System (PLC-2)
        'pressure': {
            'value': shared_state.get_state('physical_pressure', 80.0),
            'compressor_running': shared_state.get_state('plc2_compressor_1_status', False),
            'relief_valve_open': shared_state.get_state('plc2_relief_valve_1', False),
            'high_alarm': shared_state.get_state('physical_pressure', 0) > 120,
            'low_alarm': shared_state.get_state('physical_pressure', 0) < 50
        },

        # Temperature System (PLC-3)
        'temperature': {
            'value': shared_state.get_state('physical_temperature', 20.0),
            'heater_on': shared_state.get_state('plc3_heater_status', False),
            'cooling_on': shared_state.get_state('plc3_cooling_status', True),
            'high_alarm': shared_state.get_state('physical_temperature', 0) > 200,
            'thermal_runaway': False  # TODO: Get from physical process
        },

        # Safety System (PLC-4)
        'safety': {
            'shutdown_active': shared_state.get_state('physical_shutdown', False),
            'alarms': shared_state.get_state('physical_alarms', [])
        }
    }

    return jsonify(data)


@app.route('/api/alarms')
def get_alarms():
    """Get current active alarms"""
    alarms = []

    # Collect alarms from physical process
    physical_alarms = shared_state.get_state('physical_alarms', [])
    for alarm in physical_alarms:
        alarms.append({
            'timestamp': time.time(),
            'system': 'Physical Process',
            'severity': 'CRITICAL' if 'RUPTURE' in alarm or 'DAMAGE' in alarm else 'HIGH',
            'message': alarm
        })

    # Check IDS alerts
    ids_alerts = shared_state.get_state('modbus_ids_alerts', [])
    for alert in ids_alerts[-10:]:  # Last 10 alerts
        alarms.append({
            'timestamp': alert.get('timestamp', ''),
            'system': 'Security IDS',
            'severity': alert.get('severity', 'MEDIUM'),
            'message': f"{alert.get('type', 'UNKNOWN')}: {alert.get('description', '')}"
        })

    return jsonify(alarms)


@app.route('/api/control/<system>/<action>', methods=['POST'])
def control_action(system, action):
    """Execute control action"""
    try:
        if system == 'tank':
            if action == 'start_pump':
                shared_state.update_state('plc1_pump_status', True)
            elif action == 'stop_pump':
                shared_state.update_state('plc1_pump_status', False)
            elif action == 'open_valve':
                shared_state.update_state('plc1_valve_position', 100.0)
            elif action == 'close_valve':
                shared_state.update_state('plc1_valve_position', 0.0)

        elif system == 'pressure':
            if action == 'start_compressor':
                shared_state.update_state('plc2_compressor_1_status', True)
            elif action == 'stop_compressor':
                shared_state.update_state('plc2_compressor_1_status', False)
            elif action == 'open_relief':
                shared_state.update_state('plc2_relief_valve_1', True)
            elif action == 'close_relief':
                shared_state.update_state('plc2_relief_valve_1', False)

        elif system == 'temperature':
            if action == 'heater_on':
                shared_state.update_state('plc3_heater_status', True)
            elif action == 'heater_off':
                shared_state.update_state('plc3_heater_status', False)
            elif action == 'cooling_on':
                shared_state.update_state('plc3_cooling_status', True)
            elif action == 'cooling_off':
                shared_state.update_state('plc3_cooling_status', False)

        return jsonify({'success': True, 'message': f'Action {action} executed'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    log.info("=== HMI Server Starting ===")
    log.info("Access HMI at: http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)
