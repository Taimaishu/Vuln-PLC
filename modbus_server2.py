#!/usr/bin/env python3
"""
PLC-2: Pressure Control System - Modbus TCP Server
Port 5503

Simulates a pressure control system with compressors and pressure vessels
INTENTIONALLY VULNERABLE - For security testing only
"""

from pymodbus.server.sync import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
from pymodbus.constants import Endian
import threading
import time
import random
import logging
import shared_state

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Initialize shared state
shared_state.init_state()

# PLC-2 State - Pressure Control System
PLC2_STATE = {
    'pressure_vessel_1': 100.0,      # PSI
    'pressure_vessel_2': 100.0,      # PSI
    'compressor_1_status': False,
    'compressor_2_status': False,
    'compressor_1_speed': 50,        # 0-100%
    'compressor_2_speed': 50,        # 0-100%
    'relief_valve_1': False,
    'relief_valve_2': False,
    'pressure_sensor_1': 100.0,
    'pressure_sensor_2': 100.0,
    'emergency_vent': False,
    'high_pressure_alarm_1': False,
    'high_pressure_alarm_2': False,
    'low_pressure_alarm_1': False,
    'low_pressure_alarm_2': False,
}

# Store state in shared storage
def sync_state_to_shared():
    """Sync PLC-2 state to shared storage"""
    for key, value in PLC2_STATE.items():
        shared_state.update_state(f'plc2_{key}', value)

def sync_state_from_shared():
    """Load PLC-2 state from shared storage"""
    state = shared_state.load_state()
    for key in PLC2_STATE.keys():
        shared_key = f'plc2_{key}'
        if shared_key in state:
            PLC2_STATE[key] = state[shared_key]

# Modbus Register Mapping
# Holding Registers (Read/Write) - Address 0-99
# 0-19:   Pressure Vessel 1 controls
# 20-39:  Pressure Vessel 2 controls
# 40-49:  Compressor controls
# 50-59:  Relief valve controls
# 60-99:  Reserved

# Input Registers (Read-Only) - Address 0-99
# 0-19:   Pressure sensors
# 20-39:  Temperature sensors (not used)
# 40-59:  Status indicators
# 60-99:  Reserved

# Coils (Read/Write) - Address 0-99
# 0:  Compressor 1 status
# 1:  Compressor 2 status
# 2:  Relief valve 1
# 3:  Relief valve 2
# 4:  Emergency vent
# 5-99: Reserved

def process_simulation():
    """Simulate pressure control system behavior"""
    while True:
        try:
            # Load current state from shared storage
            sync_state_from_shared()

            # Simulate pressure vessel 1
            if PLC2_STATE['compressor_1_status']:
                # Compressor running increases pressure
                increase = PLC2_STATE['compressor_1_speed'] * 0.1
                PLC2_STATE['pressure_vessel_1'] += increase
            else:
                # Natural pressure leak
                PLC2_STATE['pressure_vessel_1'] -= 0.5

            # Relief valve opens automatically at high pressure
            if PLC2_STATE['pressure_vessel_1'] > 150:
                PLC2_STATE['relief_valve_1'] = True

            if PLC2_STATE['relief_valve_1']:
                PLC2_STATE['pressure_vessel_1'] -= 5.0

            # Clamp pressure
            PLC2_STATE['pressure_vessel_1'] = max(0, min(200, PLC2_STATE['pressure_vessel_1']))

            # Simulate pressure vessel 2
            if PLC2_STATE['compressor_2_status']:
                increase = PLC2_STATE['compressor_2_speed'] * 0.1
                PLC2_STATE['pressure_vessel_2'] += increase
            else:
                PLC2_STATE['pressure_vessel_2'] -= 0.5

            if PLC2_STATE['pressure_vessel_2'] > 150:
                PLC2_STATE['relief_valve_2'] = True

            if PLC2_STATE['relief_valve_2']:
                PLC2_STATE['pressure_vessel_2'] -= 5.0

            PLC2_STATE['pressure_vessel_2'] = max(0, min(200, PLC2_STATE['pressure_vessel_2']))

            # Emergency vent
            if PLC2_STATE['emergency_vent']:
                PLC2_STATE['pressure_vessel_1'] -= 10.0
                PLC2_STATE['pressure_vessel_2'] -= 10.0

            # Update pressure sensors (with small noise)
            PLC2_STATE['pressure_sensor_1'] = PLC2_STATE['pressure_vessel_1'] + random.uniform(-1, 1)
            PLC2_STATE['pressure_sensor_2'] = PLC2_STATE['pressure_vessel_2'] + random.uniform(-1, 1)

            # Alarm conditions
            PLC2_STATE['high_pressure_alarm_1'] = PLC2_STATE['pressure_vessel_1'] > 140
            PLC2_STATE['high_pressure_alarm_2'] = PLC2_STATE['pressure_vessel_2'] > 140
            PLC2_STATE['low_pressure_alarm_1'] = PLC2_STATE['pressure_vessel_1'] < 20
            PLC2_STATE['low_pressure_alarm_2'] = PLC2_STATE['pressure_vessel_2'] < 20

            # Save state to shared storage
            sync_state_to_shared()

            # Update Modbus registers
            update_modbus_registers()

            time.sleep(1)
        except Exception as e:
            log.error(f"Process simulation error: {e}")
            time.sleep(1)

def update_modbus_registers():
    """Update Modbus datastore with current state"""
    try:
        context = server_context[0]

        # Update holding registers
        context.setValues(3, 0, [int(PLC2_STATE['pressure_vessel_1'] * 10)])  # Reg 0: Vessel 1 pressure
        context.setValues(3, 1, [int(PLC2_STATE['compressor_1_speed'])])       # Reg 1: Compressor 1 speed
        context.setValues(3, 20, [int(PLC2_STATE['pressure_vessel_2'] * 10)])  # Reg 20: Vessel 2 pressure
        context.setValues(3, 21, [int(PLC2_STATE['compressor_2_speed'])])      # Reg 21: Compressor 2 speed

        # Update input registers (read-only sensors)
        context.setValues(4, 0, [int(PLC2_STATE['pressure_sensor_1'] * 10)])   # Input 0: Sensor 1
        context.setValues(4, 1, [int(PLC2_STATE['pressure_sensor_2'] * 10)])   # Input 1: Sensor 2
        context.setValues(4, 10, [int(PLC2_STATE['high_pressure_alarm_1'])])   # Input 10: Alarm 1
        context.setValues(4, 11, [int(PLC2_STATE['high_pressure_alarm_2'])])   # Input 11: Alarm 2
        context.setValues(4, 12, [int(PLC2_STATE['low_pressure_alarm_1'])])    # Input 12: Low alarm 1
        context.setValues(4, 13, [int(PLC2_STATE['low_pressure_alarm_2'])])    # Input 13: Low alarm 2

        # Update coils
        context.setValues(1, 0, [PLC2_STATE['compressor_1_status']])
        context.setValues(1, 1, [PLC2_STATE['compressor_2_status']])
        context.setValues(1, 2, [PLC2_STATE['relief_valve_1']])
        context.setValues(1, 3, [PLC2_STATE['relief_valve_2']])
        context.setValues(1, 4, [PLC2_STATE['emergency_vent']])

    except Exception as e:
        log.error(f"Error updating registers: {e}")

def read_modbus_registers():
    """Read Modbus registers and update state"""
    try:
        context = server_context[0]

        # Read coils
        coils = context.getValues(1, 0, 10)
        PLC2_STATE['compressor_1_status'] = bool(coils[0])
        PLC2_STATE['compressor_2_status'] = bool(coils[1])
        PLC2_STATE['relief_valve_1'] = bool(coils[2])
        PLC2_STATE['relief_valve_2'] = bool(coils[3])
        PLC2_STATE['emergency_vent'] = bool(coils[4])

        # Read holding registers
        regs = context.getValues(3, 0, 60)
        if regs[1] != PLC2_STATE['compressor_1_speed']:
            PLC2_STATE['compressor_1_speed'] = max(0, min(100, regs[1]))
        if regs[21] != PLC2_STATE['compressor_2_speed']:
            PLC2_STATE['compressor_2_speed'] = max(0, min(100, regs[21]))

    except Exception as e:
        log.error(f"Error reading registers: {e}")

def register_monitor():
    """Monitor register changes and log them"""
    while True:
        try:
            read_modbus_registers()
            time.sleep(0.5)
        except Exception as e:
            log.error(f"Register monitor error: {e}")
            time.sleep(1)

# Initialize Modbus datastore
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0]*100),  # Discrete Inputs
    co=ModbusSequentialDataBlock(0, [0]*100),  # Coils
    hr=ModbusSequentialDataBlock(0, [0]*100),  # Holding Registers
    ir=ModbusSequentialDataBlock(0, [0]*100)   # Input Registers
)

server_context = ModbusServerContext(slaves=store, single=True)

# Device identification
identity = ModbusDeviceIdentification()
identity.VendorName = 'VulnPLC'
identity.ProductCode = 'PLC-2'
identity.VendorUrl = 'http://github.com/vulnerable-plc'
identity.ProductName = 'Pressure Control PLC'
identity.ModelName = 'VulnPLC-2000-PSI'
identity.MajorMinorRevision = '1.0.0'

if __name__ == '__main__':
    # Start simulation thread
    sim_thread = threading.Thread(target=process_simulation, daemon=True)
    sim_thread.start()

    # Start register monitor thread
    monitor_thread = threading.Thread(target=register_monitor, daemon=True)
    monitor_thread.start()

    log.info("=" * 60)
    log.info("PLC-2: Pressure Control System - Modbus Server")
    log.info("=" * 60)
    log.info("Modbus TCP Port: 5503")
    log.info("Function Codes:")
    log.info("  - FC01: Read Coils (Compressor/Valve status)")
    log.info("  - FC03: Read Holding Registers (Control values)")
    log.info("  - FC04: Read Input Registers (Sensor readings)")
    log.info("  - FC05: Write Single Coil")
    log.info("  - FC06: Write Single Register")
    log.info("  - FC15: Write Multiple Coils")
    log.info("  - FC16: Write Multiple Registers")
    log.info("=" * 60)
    log.info("Register Map:")
    log.info("  Holding Registers:")
    log.info("    0: Vessel 1 Pressure (x10)")
    log.info("    1: Compressor 1 Speed (0-100%)")
    log.info("    20: Vessel 2 Pressure (x10)")
    log.info("    21: Compressor 2 Speed (0-100%)")
    log.info("  Input Registers:")
    log.info("    0: Pressure Sensor 1 (x10)")
    log.info("    1: Pressure Sensor 2 (x10)")
    log.info("    10-13: Alarm states")
    log.info("  Coils:")
    log.info("    0: Compressor 1 ON/OFF")
    log.info("    1: Compressor 2 ON/OFF")
    log.info("    2: Relief Valve 1")
    log.info("    3: Relief Valve 2")
    log.info("    4: Emergency Vent")
    log.info("=" * 60)
    log.info("VULNERABILITY NOTE:")
    log.info("  - No authentication required")
    log.info("  - No command validation")
    log.info("  - Vulnerable to replay attacks")
    log.info("  - No rate limiting")
    log.info("=" * 60)

    # Start Modbus server
    try:
        StartTcpServer(server_context, identity=identity, address=("0.0.0.0", 5503))
    except KeyboardInterrupt:
        log.info("Shutting down PLC-2 Modbus server...")
    except Exception as e:
        log.error(f"Server error: {e}")
