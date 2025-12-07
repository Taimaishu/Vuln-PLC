#!/usr/bin/env python3
"""
Shared state manager for PLC simulator
Allows Modbus server and Flask app to share data
"""

import json
import os
import threading
import time

STATE_FILE = '/tmp/vulnplc_state.json'
LOCK = threading.Lock()

# Default state
DEFAULT_STATE = {
    'tank1_level': 50.0,
    'tank1_temp': 25.0,
    'tank1_pressure': 101.3,
    'tank2_level': 75.0,
    'tank2_temp': 30.0,
    'tank2_pressure': 95.5,
    'pump1_status': True,
    'pump1_speed': 1500,
    'pump2_status': False,
    'pump2_speed': 0,
    'pump3_status': True,
    'pump3_speed': 2000,
    'valve1_status': False,
    'valve2_status': True,
    'valve3_status': False,
    'valve4_status': False,
    'motor1_speed': 1500,
    'motor2_speed': 0,
    'heater1_status': False,
    'heater1_setpoint': 60.0,
    'cooler1_status': True,
    'cooler1_setpoint': 20.0,
    'conveyor_status': True,
    'conveyor_speed': 50,
    'emergency_stop': False,
    'safety_interlock': True,
    'flow_rate': 15.5,
    'vibration': 2.5,
    'ph_level': 7.0,
    'conductivity': 50.0,
    'alarms': [],
    'last_update': time.time()
}

def init_state():
    """Initialize state file if it doesn't exist"""
    if not os.path.exists(STATE_FILE):
        save_state(DEFAULT_STATE)
    return load_state()

def load_state():
    """Load state from file"""
    try:
        with LOCK:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            else:
                return DEFAULT_STATE.copy()
    except Exception as e:
        print(f"Error loading state: {e}")
        return DEFAULT_STATE.copy()

def save_state(state):
    """Save state to file"""
    try:
        with LOCK:
            state['last_update'] = time.time()
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving state: {e}")

def update_state(key, value):
    """Update a single state value"""
    state = load_state()
    state[key] = value
    save_state(state)

def get_state(key, default=None):
    """Get a single state value"""
    state = load_state()
    return state.get(key, default)

# Modbus register mapping
# Each register maps to a specific state variable
REGISTER_MAP = {
    # Holding Registers (Read/Write) - Function Code 3/6/16
    0: ('tank1_level', 'float', 10),      # Scaled by 10 (500 = 50.0%)
    1: ('tank1_temp', 'float', 10),       # Scaled by 10 (250 = 25.0°C)
    2: ('tank1_pressure', 'float', 10),   # Scaled by 10 (1013 = 101.3 kPa)
    3: ('tank2_level', 'float', 10),
    4: ('tank2_temp', 'float', 10),
    5: ('tank2_pressure', 'float', 10),
    6: ('pump1_speed', 'int', 1),
    7: ('pump2_speed', 'int', 1),
    8: ('pump3_speed', 'int', 1),
    9: ('motor1_speed', 'int', 1),
    10: ('motor2_speed', 'int', 1),
    11: ('conveyor_speed', 'int', 1),
    12: ('heater1_setpoint', 'float', 10),
    13: ('cooler1_setpoint', 'float', 10),
    14: ('flow_rate', 'float', 10),
    15: ('vibration', 'float', 10),
    16: ('ph_level', 'float', 10),
    17: ('conductivity', 'float', 10),
}

# Coils (Read/Write Boolean) - Function Code 1/5/15
COIL_MAP = {
    0: 'pump1_status',
    1: 'pump2_status',
    2: 'pump3_status',
    3: 'valve1_status',
    4: 'valve2_status',
    5: 'valve3_status',
    6: 'valve4_status',
    7: 'heater1_status',
    8: 'cooler1_status',
    9: 'conveyor_status',
    10: 'emergency_stop',
    11: 'safety_interlock',
}

def register_to_state(register, value):
    """Convert Modbus register value to state value"""
    if register in REGISTER_MAP:
        key, value_type, scale = REGISTER_MAP[register]
        if value_type == 'float':
            return key, float(value) / scale
        else:
            return key, int(value)
    return None, None

def state_to_register(register):
    """Convert state value to Modbus register value"""
    if register in REGISTER_MAP:
        key, value_type, scale = REGISTER_MAP[register]
        value = get_state(key, 0)
        if value_type == 'float':
            return int(value * scale)
        else:
            return int(value)
    return 0

def coil_to_state(coil, value):
    """Convert Modbus coil value to state"""
    if coil in COIL_MAP:
        key = COIL_MAP[coil]
        return key, bool(value)
    return None, None

def state_to_coil(coil):
    """Convert state value to Modbus coil value"""
    if coil in COIL_MAP:
        key = COIL_MAP[coil]
        value = get_state(key, False)
        return 1 if value else 0
    return 0

if __name__ == '__main__':
    # Test the shared state
    print("Initializing shared state...")
    state = init_state()
    print(f"Current state: {json.dumps(state, indent=2)}")

    print("\nTesting update...")
    update_state('tank1_level', 75.5)
    print(f"Tank 1 level: {get_state('tank1_level')}")

    print("\nRegister mapping test:")
    print(f"Register 0 (tank1_level): {state_to_register(0)}")
    print(f"Coil 0 (pump1_status): {state_to_coil(0)}")
