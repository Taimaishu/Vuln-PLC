#!/usr/bin/env python3
"""
PLC-4: Safety/Emergency Shutdown System - Modbus TCP Server
Port 5505

Simulates a critical safety system with emergency stops and interlocks
INTENTIONALLY VULNERABLE - For security testing only
Vulnerabilities: Weak authentication, timing attacks, safety bypass
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

# PLC-4 State - Safety/ESD System
PLC4_STATE = {
    'emergency_stop_1': False,
    'emergency_stop_2': False,
    'emergency_stop_3': False,
    'master_emergency_stop': False,
    'safety_interlock_1': True,        # True = safe
    'safety_interlock_2': True,
    'safety_interlock_3': True,
    'fire_detection_zone1': False,
    'fire_detection_zone2': False,
    'fire_detection_zone3': False,
    'gas_detection_zone1': False,
    'gas_detection_zone2': False,
    'gas_leak_detected': False,
    'fire_suppression_active': False,
    'evacuation_alarm': False,
    'safety_system_armed': True,
    'safety_bypass_mode': False,       # VULNERABILITY: Can be enabled
    'watchdog_enabled': True,
    'watchdog_counter': 0,
    'critical_alarm_count': 0,
    'safety_override_code': 0,         # VULNERABILITY: Can be guessed
    'last_safety_check': time.time(),
    'system_healthy': True,
}

def sync_state_to_shared():
    """Sync PLC-4 state to shared storage (calculated values only, not controls)"""
    calculated_keys = [
        'watchdog_counter', 'critical_alarm_count',
        'last_safety_check', 'system_healthy',
        'gas_leak_detected'
    ]
    for key in calculated_keys:
        if key in PLC4_STATE:
            shared_state.update_state(f'plc4_{key}', PLC4_STATE[key])

def sync_state_from_shared():
    state = shared_state.load_state()
    for key in PLC4_STATE.keys():
        shared_key = f'plc4_{key}'
        if shared_key in state and state[shared_key] is not None:
            PLC4_STATE[key] = state[shared_key]

def process_simulation():
    """Simulate safety system"""
    while True:
        try:
            # NOTE: Don't load state from shared - it would overwrite
            # control values set via web interface or Modbus
            # Control values come from register monitor thread only

            # Watchdog timer
            if PLC4_STATE['watchdog_enabled']:
                PLC4_STATE['watchdog_counter'] += 1
                if PLC4_STATE['watchdog_counter'] > 60:
                    log.warning("Watchdog timeout - safety system may have failed")
                    PLC4_STATE['system_healthy'] = False

            # Check for emergency conditions
            any_emergency = (
                PLC4_STATE['emergency_stop_1'] or
                PLC4_STATE['emergency_stop_2'] or
                PLC4_STATE['emergency_stop_3']
            )

            if any_emergency:
                PLC4_STATE['master_emergency_stop'] = True

            # Fire detection logic
            fire_detected = (
                PLC4_STATE['fire_detection_zone1'] or
                PLC4_STATE['fire_detection_zone2'] or
                PLC4_STATE['fire_detection_zone3']
            )

            if fire_detected:
                PLC4_STATE['evacuation_alarm'] = True
                PLC4_STATE['fire_suppression_active'] = True
                PLC4_STATE['master_emergency_stop'] = True

            # Gas leak detection
            gas_detected = (
                PLC4_STATE['gas_detection_zone1'] or
                PLC4_STATE['gas_detection_zone2']
            )

            if gas_detected:
                PLC4_STATE['gas_leak_detected'] = True
                PLC4_STATE['evacuation_alarm'] = True
                PLC4_STATE['master_emergency_stop'] = True

            # VULNERABILITY: Safety bypass mode disables all safety checks
            if PLC4_STATE['safety_bypass_mode']:
                log.warning("SAFETY BYPASS MODE ACTIVE - All safety interlocks disabled!")
                PLC4_STATE['safety_interlock_1'] = True
                PLC4_STATE['safety_interlock_2'] = True
                PLC4_STATE['safety_interlock_3'] = True
                # Don't trigger alarms in bypass mode
                PLC4_STATE['master_emergency_stop'] = False

            # Count critical alarms
            PLC4_STATE['critical_alarm_count'] = sum([
                PLC4_STATE['master_emergency_stop'],
                fire_detected,
                gas_detected,
            ])

            # Update last safety check timestamp
            PLC4_STATE['last_safety_check'] = time.time()

            sync_state_to_shared()
            update_modbus_registers()

            time.sleep(1)
        except Exception as e:
            log.error(f"Process simulation error: {e}")
            time.sleep(1)

def update_modbus_registers():
    try:
        context = server_context[0]

        # Coils - Digital outputs
        context.setValues(1, 0, [PLC4_STATE['emergency_stop_1']])
        context.setValues(1, 1, [PLC4_STATE['emergency_stop_2']])
        context.setValues(1, 2, [PLC4_STATE['emergency_stop_3']])
        context.setValues(1, 3, [PLC4_STATE['master_emergency_stop']])
        context.setValues(1, 10, [PLC4_STATE['safety_interlock_1']])
        context.setValues(1, 11, [PLC4_STATE['safety_interlock_2']])
        context.setValues(1, 12, [PLC4_STATE['safety_interlock_3']])
        context.setValues(1, 20, [PLC4_STATE['fire_detection_zone1']])
        context.setValues(1, 21, [PLC4_STATE['fire_detection_zone2']])
        context.setValues(1, 22, [PLC4_STATE['fire_detection_zone3']])
        context.setValues(1, 23, [PLC4_STATE['gas_detection_zone1']])
        context.setValues(1, 24, [PLC4_STATE['gas_detection_zone2']])
        context.setValues(1, 30, [PLC4_STATE['fire_suppression_active']])
        context.setValues(1, 31, [PLC4_STATE['evacuation_alarm']])
        context.setValues(1, 40, [PLC4_STATE['safety_bypass_mode']])
        context.setValues(1, 41, [PLC4_STATE['watchdog_enabled']])
        context.setValues(1, 42, [PLC4_STATE['system_healthy']])

        # Holding registers
        context.setValues(3, 0, [PLC4_STATE['critical_alarm_count']])
        context.setValues(3, 1, [PLC4_STATE['watchdog_counter']])
        context.setValues(3, 2, [PLC4_STATE['safety_override_code']])

        # Input registers (read-only status)
        context.setValues(4, 0, [int(PLC4_STATE['system_healthy'])])
        context.setValues(4, 1, [PLC4_STATE['critical_alarm_count']])
        context.setValues(4, 2, [int(time.time() - PLC4_STATE['last_safety_check'])])

    except Exception as e:
        log.error(f"Error updating registers: {e}")

def read_modbus_registers():
    """Read Modbus registers and update state ONLY if changed by external write"""
    try:
        context = server_context[0]

        # Read coils - only update if they differ from current state
        coils = context.getValues(1, 0, 50)
        if bool(coils[0]) != PLC4_STATE['emergency_stop_1']:
            PLC4_STATE['emergency_stop_1'] = bool(coils[0])
            log.info(f"External Modbus write: emergency_stop_1 = {coils[0]}")
        if bool(coils[1]) != PLC4_STATE['emergency_stop_2']:
            PLC4_STATE['emergency_stop_2'] = bool(coils[1])
            log.info(f"External Modbus write: emergency_stop_2 = {coils[1]}")
        if bool(coils[2]) != PLC4_STATE['emergency_stop_3']:
            PLC4_STATE['emergency_stop_3'] = bool(coils[2])
            log.info(f"External Modbus write: emergency_stop_3 = {coils[2]}")
        if bool(coils[3]) != PLC4_STATE['master_emergency_stop']:
            PLC4_STATE['master_emergency_stop'] = bool(coils[3])
            log.info(f"External Modbus write: master_emergency_stop = {coils[3]}")
        if bool(coils[10]) != PLC4_STATE['safety_interlock_1']:
            PLC4_STATE['safety_interlock_1'] = bool(coils[10])
            log.info(f"External Modbus write: safety_interlock_1 = {coils[10]}")
        if bool(coils[11]) != PLC4_STATE['safety_interlock_2']:
            PLC4_STATE['safety_interlock_2'] = bool(coils[11])
            log.info(f"External Modbus write: safety_interlock_2 = {coils[11]}")
        if bool(coils[12]) != PLC4_STATE['safety_interlock_3']:
            PLC4_STATE['safety_interlock_3'] = bool(coils[12])
            log.info(f"External Modbus write: safety_interlock_3 = {coils[12]}")
        if bool(coils[20]) != PLC4_STATE['fire_detection_zone1']:
            PLC4_STATE['fire_detection_zone1'] = bool(coils[20])
            log.info(f"External Modbus write: fire_detection_zone1 = {coils[20]}")
        if bool(coils[21]) != PLC4_STATE['fire_detection_zone2']:
            PLC4_STATE['fire_detection_zone2'] = bool(coils[21])
            log.info(f"External Modbus write: fire_detection_zone2 = {coils[21]}")
        if bool(coils[22]) != PLC4_STATE['fire_detection_zone3']:
            PLC4_STATE['fire_detection_zone3'] = bool(coils[22])
            log.info(f"External Modbus write: fire_detection_zone3 = {coils[22]}")
        if bool(coils[23]) != PLC4_STATE['gas_detection_zone1']:
            PLC4_STATE['gas_detection_zone1'] = bool(coils[23])
            log.info(f"External Modbus write: gas_detection_zone1 = {coils[23]}")
        if bool(coils[24]) != PLC4_STATE['gas_detection_zone2']:
            PLC4_STATE['gas_detection_zone2'] = bool(coils[24])
            log.info(f"External Modbus write: gas_detection_zone2 = {coils[24]}")
        if bool(coils[30]) != PLC4_STATE['fire_suppression_active']:
            PLC4_STATE['fire_suppression_active'] = bool(coils[30])
            log.info(f"External Modbus write: fire_suppression_active = {coils[30]}")
        if bool(coils[31]) != PLC4_STATE['evacuation_alarm']:
            PLC4_STATE['evacuation_alarm'] = bool(coils[31])
            log.info(f"External Modbus write: evacuation_alarm = {coils[31]}")
        if bool(coils[40]) != PLC4_STATE['safety_bypass_mode']:
            PLC4_STATE['safety_bypass_mode'] = bool(coils[40])
            log.info(f"External Modbus write: safety_bypass_mode = {coils[40]}")
        if bool(coils[41]) != PLC4_STATE['watchdog_enabled']:
            PLC4_STATE['watchdog_enabled'] = bool(coils[41])
            log.info(f"External Modbus write: watchdog_enabled = {coils[41]}")

        # Read holding registers - only update if changed
        regs = context.getValues(3, 0, 10)
        if regs[2] != PLC4_STATE['safety_override_code']:
            PLC4_STATE['safety_override_code'] = regs[2]
            log.info(f"External Modbus write: safety_override_code = {regs[2]}")
            # Reset watchdog if code matches
            if PLC4_STATE['safety_override_code'] == 1234:  # VULNERABILITY: Weak code
                PLC4_STATE['watchdog_counter'] = 0
                log.info("Watchdog counter reset via override code")

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

def shared_state_monitor():
    """Monitor shared state for web interface changes"""
    while True:
        try:
            state = shared_state.load_state()
            keys_to_monitor = [
                'emergency_stop_1', 'emergency_stop_2', 'emergency_stop_3',
                'master_emergency_stop', 'safety_interlock_1', 'safety_interlock_2', 'safety_interlock_3',
                'fire_detection_zone1', 'fire_detection_zone2', 'fire_detection_zone3',
                'gas_detection_zone1', 'gas_detection_zone2',
                'fire_suppression_active', 'evacuation_alarm',
                'safety_bypass_mode', 'watchdog_enabled'
            ]
            for key in keys_to_monitor:
                shared_key = f'plc4_{key}'
                if shared_key in state and state[shared_key] is not None:
                    if PLC4_STATE[key] != state[shared_key]:
                        log.info(f"Web interface change: {key} = {state[shared_key]}")
                        PLC4_STATE[key] = state[shared_key]
            time.sleep(0.3)
        except Exception as e:
            log.error(f"State monitor error: {e}")
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
identity.ProductCode = 'PLC-4'
identity.VendorUrl = 'http://github.com/vulnerable-plc'
identity.ProductName = 'Safety/ESD PLC'
identity.ModelName = 'VulnPLC-4000-ESD'
identity.MajorMinorRevision = '3.0.1'

if __name__ == '__main__':
    # Initialize shared state with PLC-4 defaults
    sync_state_to_shared()
    log.info("PLC-4 state initialized in shared storage")

    sim_thread = threading.Thread(target=process_simulation, daemon=True)
    sim_thread.start()

    monitor_thread = threading.Thread(target=register_monitor, daemon=True)
    monitor_thread.start()

    state_monitor_thread = threading.Thread(target=shared_state_monitor, daemon=True)
    state_monitor_thread.start()

    log.info("=" * 60)
    log.info("PLC-4: Safety/Emergency Shutdown System - Modbus Server")
    log.info("=" * 60)
    log.info("Modbus TCP Port: 5505")
    log.info("=" * 60)
    log.info("Register Map:")
    log.info("  Coils:")
    log.info("    0-3: Emergency Stops")
    log.info("    10-12: Safety Interlocks")
    log.info("    20-22: Fire Detection Zones")
    log.info("    23-24: Gas Detection Zones")
    log.info("    30-31: Fire Suppression & Evacuation")
    log.info("    40: Safety Bypass Mode (DANGEROUS!)")
    log.info("    41: Watchdog Enable")
    log.info("    42: System Health")
    log.info("  Holding Registers:")
    log.info("    0: Critical Alarm Count")
    log.info("    1: Watchdog Counter")
    log.info("    2: Safety Override Code (1234 = reset)")
    log.info("  Input Registers:")
    log.info("    0: System Healthy (0/1)")
    log.info("    1: Critical Alarm Count")
    log.info("    2: Time Since Last Safety Check")
    log.info("=" * 60)
    log.info("CRITICAL VULNERABILITIES:")
    log.info("  - Safety bypass can be enabled via Modbus")
    log.info("  - Weak override code (1234)")
    log.info("  - No authentication on safety-critical functions")
    log.info("  - Watchdog can be disabled remotely")
    log.info("  - Timing attacks possible on authentication")
    log.info("=" * 60)

    try:
        StartTcpServer(server_context, identity=identity, address=("0.0.0.0", 5505))
    except KeyboardInterrupt:
        log.info("Shutting down PLC-4 Modbus server...")
    except Exception as e:
        log.error(f"Server error: {e}")
