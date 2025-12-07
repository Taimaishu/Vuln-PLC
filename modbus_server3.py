#!/usr/bin/env python3
"""
PLC-3: Temperature Control System - Modbus TCP Server
Port 5504

Simulates a temperature control system with heaters and coolers
INTENTIONALLY VULNERABLE - For security testing only
Vulnerabilities: Firmware upload bypass, insecure deserialization, race conditions
"""

from pymodbus.server.sync import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import threading
import time
import random
import logging
import shared_state

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

shared_state.init_state()

# PLC-3 State - Temperature Control System
PLC3_STATE = {
    'zone1_temp': 25.0,              # Celsius
    'zone2_temp': 25.0,
    'zone3_temp': 25.0,
    'heater1_status': False,
    'heater2_status': False,
    'heater3_status': False,
    'heater1_power': 50,             # 0-100%
    'heater2_power': 50,
    'heater3_power': 50,
    'cooler1_status': False,
    'cooler2_status': False,
    'cooler3_status': False,
    'cooler1_power': 50,
    'cooler2_power': 50,
    'cooler3_power': 50,
    'setpoint1': 25.0,
    'setpoint2': 25.0,
    'setpoint3': 25.0,
    'safety_limit_high': 100.0,
    'safety_limit_low': 0.0,
    'thermal_runaway': False,
}

def sync_state_to_shared():
    for key, value in PLC3_STATE.items():
        shared_state.update_state(f'plc3_{key}', value)

def sync_state_from_shared():
    state = shared_state.load_state()
    for key in PLC3_STATE.keys():
        shared_key = f'plc3_{key}'
        if shared_key in state:
            PLC3_STATE[key] = state[shared_key]

def process_simulation():
    """Simulate temperature control system"""
    while True:
        try:
            sync_state_from_shared()

            # Simulate Zone 1
            ambient_loss = (PLC3_STATE['zone1_temp'] - 20) * 0.05
            PLC3_STATE['zone1_temp'] -= ambient_loss

            if PLC3_STATE['heater1_status']:
                PLC3_STATE['zone1_temp'] += PLC3_STATE['heater1_power'] * 0.02
            if PLC3_STATE['cooler1_status']:
                PLC3_STATE['zone1_temp'] -= PLC3_STATE['cooler1_power'] * 0.03

            # Simulate Zone 2
            ambient_loss = (PLC3_STATE['zone2_temp'] - 20) * 0.05
            PLC3_STATE['zone2_temp'] -= ambient_loss

            if PLC3_STATE['heater2_status']:
                PLC3_STATE['zone2_temp'] += PLC3_STATE['heater2_power'] * 0.02
            if PLC3_STATE['cooler2_status']:
                PLC3_STATE['zone2_temp'] -= PLC3_STATE['cooler2_power'] * 0.03

            # Simulate Zone 3
            ambient_loss = (PLC3_STATE['zone3_temp'] - 20) * 0.05
            PLC3_STATE['zone3_temp'] -= ambient_loss

            if PLC3_STATE['heater3_status']:
                PLC3_STATE['zone3_temp'] += PLC3_STATE['heater3_power'] * 0.02
            if PLC3_STATE['cooler3_status']:
                PLC3_STATE['zone3_temp'] -= PLC3_STATE['cooler3_power'] * 0.03

            # VULNERABILITY: Thermal runaway condition (race condition)
            if PLC3_STATE['thermal_runaway']:
                PLC3_STATE['zone1_temp'] += 5.0
                PLC3_STATE['zone2_temp'] += 5.0
                PLC3_STATE['zone3_temp'] += 5.0

            # Safety limits
            PLC3_STATE['zone1_temp'] = max(-50, min(200, PLC3_STATE['zone1_temp']))
            PLC3_STATE['zone2_temp'] = max(-50, min(200, PLC3_STATE['zone2_temp']))
            PLC3_STATE['zone3_temp'] = max(-50, min(200, PLC3_STATE['zone3_temp']))

            sync_state_to_shared()
            update_modbus_registers()

            time.sleep(1)
        except Exception as e:
            log.error(f"Process simulation error: {e}")
            time.sleep(1)

def update_modbus_registers():
    try:
        context = server_context[0]

        # Holding registers - temperatures (x10 for precision)
        context.setValues(3, 0, [int(PLC3_STATE['zone1_temp'] * 10)])
        context.setValues(3, 1, [int(PLC3_STATE['setpoint1'] * 10)])
        context.setValues(3, 2, [int(PLC3_STATE['heater1_power'])])
        context.setValues(3, 3, [int(PLC3_STATE['cooler1_power'])])

        context.setValues(3, 20, [int(PLC3_STATE['zone2_temp'] * 10)])
        context.setValues(3, 21, [int(PLC3_STATE['setpoint2'] * 10)])
        context.setValues(3, 22, [int(PLC3_STATE['heater2_power'])])
        context.setValues(3, 23, [int(PLC3_STATE['cooler2_power'])])

        context.setValues(3, 40, [int(PLC3_STATE['zone3_temp'] * 10)])
        context.setValues(3, 41, [int(PLC3_STATE['setpoint3'] * 10)])
        context.setValues(3, 42, [int(PLC3_STATE['heater3_power'])])
        context.setValues(3, 43, [int(PLC3_STATE['cooler3_power'])])

        # Coils - on/off states
        context.setValues(1, 0, [PLC3_STATE['heater1_status']])
        context.setValues(1, 1, [PLC3_STATE['heater2_status']])
        context.setValues(1, 2, [PLC3_STATE['heater3_status']])
        context.setValues(1, 3, [PLC3_STATE['cooler1_status']])
        context.setValues(1, 4, [PLC3_STATE['cooler2_status']])
        context.setValues(1, 5, [PLC3_STATE['cooler3_status']])
        context.setValues(1, 10, [PLC3_STATE['thermal_runaway']])

    except Exception as e:
        log.error(f"Error updating registers: {e}")

def read_modbus_registers():
    try:
        context = server_context[0]

        coils = context.getValues(1, 0, 20)
        PLC3_STATE['heater1_status'] = bool(coils[0])
        PLC3_STATE['heater2_status'] = bool(coils[1])
        PLC3_STATE['heater3_status'] = bool(coils[2])
        PLC3_STATE['cooler1_status'] = bool(coils[3])
        PLC3_STATE['cooler2_status'] = bool(coils[4])
        PLC3_STATE['cooler3_status'] = bool(coils[5])
        PLC3_STATE['thermal_runaway'] = bool(coils[10])

        regs = context.getValues(3, 0, 60)
        PLC3_STATE['heater1_power'] = max(0, min(100, regs[2]))
        PLC3_STATE['cooler1_power'] = max(0, min(100, regs[3]))
        PLC3_STATE['heater2_power'] = max(0, min(100, regs[22]))
        PLC3_STATE['cooler2_power'] = max(0, min(100, regs[23]))
        PLC3_STATE['heater3_power'] = max(0, min(100, regs[42]))
        PLC3_STATE['cooler3_power'] = max(0, min(100, regs[43]))

    except Exception as e:
        log.error(f"Error reading registers: {e}")

def register_monitor():
    while True:
        try:
            read_modbus_registers()
            time.sleep(0.5)
        except Exception as e:
            log.error(f"Register monitor error: {e}")
            time.sleep(1)

# Initialize Modbus datastore
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0]*100),
    co=ModbusSequentialDataBlock(0, [0]*100),
    hr=ModbusSequentialDataBlock(0, [0]*100),
    ir=ModbusSequentialDataBlock(0, [0]*100)
)

server_context = ModbusServerContext(slaves=store, single=True)

identity = ModbusDeviceIdentification()
identity.VendorName = 'VulnPLC'
identity.ProductCode = 'PLC-3'
identity.VendorUrl = 'http://github.com/vulnerable-plc'
identity.ProductName = 'Temperature Control PLC'
identity.ModelName = 'VulnPLC-3000-TEMP'
identity.MajorMinorRevision = '2.1.0'

if __name__ == '__main__':
    sim_thread = threading.Thread(target=process_simulation, daemon=True)
    sim_thread.start()

    monitor_thread = threading.Thread(target=register_monitor, daemon=True)
    monitor_thread.start()

    log.info("=" * 60)
    log.info("PLC-3: Temperature Control System - Modbus Server")
    log.info("=" * 60)
    log.info("Modbus TCP Port: 5504")
    log.info("=" * 60)
    log.info("Register Map:")
    log.info("  Holding Registers:")
    log.info("    0-3: Zone 1 (temp, setpoint, heater, cooler)")
    log.info("    20-23: Zone 2 (temp, setpoint, heater, cooler)")
    log.info("    40-43: Zone 3 (temp, setpoint, heater, cooler)")
    log.info("  Coils:")
    log.info("    0-2: Heater 1-3 ON/OFF")
    log.info("    3-5: Cooler 1-3 ON/OFF")
    log.info("    10: Thermal Runaway (DANGER)")
    log.info("=" * 60)
    log.info("VULNERABILITY NOTE:")
    log.info("  - Race condition in thermal runaway")
    log.info("  - No safety interlock verification")
    log.info("  - Vulnerable to firmware injection")
    log.info("=" * 60)

    try:
        StartTcpServer(server_context, identity=identity, address=("0.0.0.0", 5504))
    except KeyboardInterrupt:
        log.info("Shutting down PLC-3 Modbus server...")
    except Exception as e:
        log.error(f"Server error: {e}")
