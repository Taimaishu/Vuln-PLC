#!/usr/bin/env python3
"""
Modbus TCP Server for Vulnerable PLC Simulator
Implements standard Modbus protocol on port 5502
Syncs with web interface via shared state
"""

try:
    from pymodbus.server.sync import StartTcpServer
    from pymodbus.device import ModbusDeviceIdentification
    from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
    from pymodbus.datastore import ModbusSparseDataBlock
except ImportError:
    print("pymodbus not installed. Run: pip install pymodbus==2.5.3")
    exit(1)

import threading
import time
import random
import shared_state

class SyncedDataBlock(ModbusSequentialDataBlock):
    """Custom data block that syncs with shared state"""

    def __init__(self, address, values, is_coil=False):
        super().__init__(address, values)
        self.is_coil = is_coil

    def setValues(self, address, values):
        """Override to sync changes to shared state"""
        super().setValues(address, values)

        # Update shared state when registers/coils are written
        for i, value in enumerate(values):
            reg_addr = address + i

            if self.is_coil:
                key, state_value = shared_state.coil_to_state(reg_addr, value)
                if key:
                    shared_state.update_state(key, state_value)
                    print(f"[Modbus] Coil {reg_addr} → {key} = {state_value}")
            else:
                key, state_value = shared_state.register_to_state(reg_addr, value)
                if key:
                    shared_state.update_state(key, state_value)
                    print(f"[Modbus] Register {reg_addr} → {key} = {state_value}")

class ModbusPLCServer:
    def __init__(self, host='0.0.0.0', port=5502):
        self.host = host
        self.port = port
        self.context = None

        # Initialize shared state
        shared_state.init_state()

    def initialize_data_store(self):
        """Initialize Modbus data store with values from shared state"""

        # Initialize holding registers from shared state
        hr_values = [0] * 100
        for reg in range(100):
            hr_values[reg] = shared_state.state_to_register(reg)

        # Initialize coils from shared state
        coil_values = [0] * 100
        for coil in range(100):
            coil_values[coil] = shared_state.state_to_coil(coil)

        # Create data blocks with syncing
        store = ModbusSlaveContext(
            di=ModbusSequentialDataBlock(0, [0] * 100),  # Discrete inputs (read-only)
            co=SyncedDataBlock(0, coil_values, is_coil=True),  # Coils (synced)
            hr=SyncedDataBlock(0, hr_values, is_coil=False),  # Holding registers (synced)
            ir=ModbusSequentialDataBlock(0, [0] * 100)  # Input registers (read-only, simulated)
        )

        self.context = ModbusServerContext(slaves=store, single=True)

        # Start background threads
        threading.Thread(target=self.sync_state_to_modbus, daemon=True).start()
        threading.Thread(target=self.simulate_sensors, daemon=True).start()

    def sync_state_to_modbus(self):
        """Periodically sync shared state to Modbus registers"""
        while True:
            try:
                time.sleep(1)  # Sync every second

                slave_id = 0x00
                state = shared_state.load_state()

                # Update holding registers from state
                # Use parent class setValues to bypass SyncedDataBlock override (prevents feedback loop)
                for reg in range(20):  # Only update mapped registers
                    value = shared_state.state_to_register(reg)
                    ModbusSequentialDataBlock.setValues(self.context[slave_id].store['h'], reg, [value])

                # Update coils from state
                # Use parent class setValues to bypass SyncedDataBlock override (prevents feedback loop)
                for coil in range(15):  # Only update mapped coils
                    value = shared_state.state_to_coil(coil)
                    ModbusSequentialDataBlock.setValues(self.context[slave_id].store['c'], coil, [value])

            except Exception as e:
                print(f"Sync error: {e}")
                time.sleep(5)

    def simulate_sensors(self):
        """Simulate sensor readings (input registers)"""
        while True:
            try:
                time.sleep(2)

                slave_id = 0x00
                state = shared_state.load_state()

                # Read-only input registers that mirror current state
                # These simulate real sensor readings
                values = [
                    int(state.get('tank1_level', 50) * 10),
                    int(state.get('tank1_temp', 25) * 10),
                    int(state.get('tank1_pressure', 101) * 10),
                    int(state.get('flow_rate', 15) * 10),
                    int(state.get('vibration', 2) * 10),
                    state.get('pump1_speed', 1500),
                    1 if state.get('pump1_status', False) else 0,
                    1 if state.get('emergency_stop', False) else 0,
                ]

                self.context[slave_id].setValues(4, 0, values)

            except Exception as e:
                print(f"Sensor simulation error: {e}")
                time.sleep(5)

    def start(self):
        """Start the Modbus TCP server"""
        self.initialize_data_store()

        # Configure device identification
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'VulnPLC Inc.'
        identity.ProductCode = 'VulnPLC-3000'
        identity.VendorUrl = 'http://localhost:5000'
        identity.ProductName = 'Vulnerable PLC Simulator'
        identity.ModelName = 'VulnPLC-3000'
        identity.MajorMinorRevision = '1.0.0'

        print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║  Modbus TCP Server Starting (Synced Mode)                 ║
    ╚═══════════════════════════════════════════════════════════╝

    Modbus TCP Server: {self.host}:{self.port}
    Device: VulnPLC-3000
    State File: {shared_state.STATE_FILE}

    REGISTER MAPPING (Holding Registers - FC 3/6/16):
    ────────────────────────────────────────────────────────────
    0  = Tank 1 Level (scaled x10: 500 = 50.0%)
    1  = Tank 1 Temperature (scaled x10: 250 = 25.0°C)
    2  = Tank 1 Pressure (scaled x10: 1013 = 101.3 kPa)
    3  = Tank 2 Level
    4  = Tank 2 Temperature
    5  = Tank 2 Pressure
    6  = Pump 1 Speed (RPM)
    7  = Pump 2 Speed (RPM)
    14 = Flow Rate (scaled x10)
    15 = Vibration (scaled x10)

    COIL MAPPING (Coils - FC 1/5/15):
    ────────────────────────────────────────────────────────────
    0  = Pump 1 Status (ON/OFF)
    1  = Pump 2 Status
    2  = Pump 3 Status
    3  = Valve 1 Status
    4  = Valve 2 Status
    10 = Emergency Stop
    11 = Safety Interlock

    TEST COMMANDS:
    ────────────────────────────────────────────────────────────
    # Read tank level
    modbus read localhost:5502 0 1

    # Set tank level to 80%
    modbus write localhost:5502 0 800

    # Turn on pump 1
    modbus write localhost:5502 -t 0 0 1

    # Read multiple registers
    modbus read localhost:5502 0 10

    # Metasploit scanner
    use auxiliary/scanner/scada/modbusclient
    set RHOSTS localhost
    set RPORT 5502
    run

    Changes via Modbus will appear in real-time on the HMI!
    Press Ctrl+C to stop
        """)

        try:
            StartTcpServer(
                self.context,
                identity=identity,
                address=(self.host, self.port)
            )
        except KeyboardInterrupt:
            print("\nShutting down Modbus server...")
        except Exception as e:
            print(f"Error starting Modbus server: {e}")

if __name__ == '__main__':
    server = ModbusPLCServer(host='0.0.0.0', port=5502)
    server.start()
