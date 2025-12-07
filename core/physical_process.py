#!/usr/bin/env python3
"""
Physical Process Simulator
Realistic simulation of industrial processes with physics-based calculations

Simulates:
- Tank level dynamics (inflow/outflow)
- Pressure systems (compression, relief)
- Temperature control (heating/cooling)
- Flow rates and valve positions
- Safety interlocks and consequences
"""

import time
import threading
import logging
import math
from dataclasses import dataclass
from typing import Dict, Optional
import shared_state

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@dataclass
class PhysicalState:
    """Current state of physical process"""
    timestamp: float
    tank_level: float  # % (0-100)
    pressure: float  # PSI
    temperature: float  # Celsius
    flow_rate: float  # GPM
    valve_position: float  # % (0-100)
    pump_running: bool
    alarm_state: str  # NORMAL, WARNING, ALARM, EMERGENCY


class TankSystem:
    """
    Water tank with inflow and outflow

    Physics:
    - Level increases with pump inflow
    - Level decreases with valve outflow
    - Overflow if level > 100%
    - Pump cavitation if level < 5%
    """

    def __init__(self, capacity_gallons: float = 1000):
        self.capacity = capacity_gallons
        self.level_percent = 50.0  # Start at 50%
        self.pump_inflow_rate = 50.0  # GPM when pump is on
        self.valve_outflow_base = 30.0  # GPM base rate
        self.overflow = False
        self.cavitation = False

    def update(self, dt: float, pump_on: bool, valve_open_percent: float):
        """Update tank level based on pump and valve states"""
        # Calculate inflow
        inflow = self.pump_inflow_rate if pump_on else 0.0

        # Calculate outflow (proportional to valve position and level)
        # Flow increases with level due to pressure
        level_factor = math.sqrt(max(0.1, self.level_percent / 100.0))
        outflow = self.valve_outflow_base * (valve_open_percent / 100.0) * level_factor

        # Net flow
        net_flow = inflow - outflow

        # Update level (convert flow to percentage)
        level_change = (net_flow / self.capacity) * 100.0 * dt
        self.level_percent += level_change

        # Check constraints
        if self.level_percent > 100.0:
            self.level_percent = 100.0
            self.overflow = True
            log.error("🚨 TANK OVERFLOW! Level: 100%")
        else:
            self.overflow = False

        if self.level_percent < 5.0 and pump_on:
            self.cavitation = True
            log.error("🚨 PUMP CAVITATION! Level: <5%")
        else:
            self.cavitation = False

        if self.level_percent < 0.0:
            self.level_percent = 0.0

        return {
            'level': self.level_percent,
            'inflow': inflow,
            'outflow': outflow,
            'overflow': self.overflow,
            'cavitation': self.cavitation
        }


class PressureSystem:
    """
    Compressed air/gas system

    Physics:
    - Pressure increases with compressor operation
    - Pressure decreases with usage/leaks
    - Relief valve opens at high pressure
    - Vessel rupture if pressure exceeds design limit
    """

    def __init__(self, max_pressure_psi: float = 150):
        self.pressure = 80.0  # PSI - start at normal operating pressure
        self.max_pressure = max_pressure_psi
        self.compressor_rate = 10.0  # PSI/sec when compressor running
        self.leak_rate = 2.0  # PSI/sec baseline leak
        self.relief_valve_setpoint = 120.0  # PSI
        self.relief_valve_open = False
        self.rupture = False

    def update(self, dt: float, compressor_on: bool, relief_valve_forced: bool = False):
        """Update pressure based on compressor and relief valve"""
        # Compressor input
        if compressor_on:
            self.pressure += self.compressor_rate * dt

        # Baseline leakage
        self.pressure -= self.leak_rate * dt

        # Relief valve (automatic or forced)
        if relief_valve_forced or self.pressure >= self.relief_valve_setpoint:
            self.relief_valve_open = True
            relief_rate = 15.0  # PSI/sec when relief valve open
            self.pressure -= relief_rate * dt
        else:
            self.relief_valve_open = False

        # Check for rupture
        if self.pressure > self.max_pressure:
            self.rupture = True
            self.pressure = 0.0  # Catastrophic failure
            log.error(f"🚨🚨🚨 VESSEL RUPTURE! Pressure exceeded {self.max_pressure} PSI")

        # Constraints
        if self.pressure < 0:
            self.pressure = 0.0

        return {
            'pressure': self.pressure,
            'relief_valve_open': self.relief_valve_open,
            'rupture': self.rupture,
            'alarm': 'CRITICAL' if self.rupture else ('HIGH' if self.pressure > 130 else 'NORMAL')
        }


class TemperatureSystem:
    """
    Temperature control system (furnace/reactor)

    Physics:
    - Temperature increases with heater operation
    - Temperature decreases with cooling and ambient loss
    - Thermal runaway if cooling fails
    - Material damage at high temperatures
    """

    def __init__(self, ambient_temp: float = 20.0):
        self.temperature = ambient_temp
        self.ambient = ambient_temp
        self.heater_rate = 5.0  # °C/sec when heater on
        self.cooling_rate = 3.0  # °C/sec when cooling on
        self.ambient_loss_rate = 0.5  # °C/sec heat loss to environment
        self.max_safe_temp = 200.0  # °C
        self.damage_temp = 250.0  # °C - material damage
        self.thermal_runaway = False
        self.damage = False

    def update(self, dt: float, heater_on: bool, cooling_on: bool):
        """Update temperature based on heater and cooling"""
        # Heater input
        if heater_on:
            self.temperature += self.heater_rate * dt

        # Active cooling
        if cooling_on:
            self.temperature -= self.cooling_rate * dt

        # Ambient heat loss (proportional to temp difference)
        temp_diff = self.temperature - self.ambient
        if temp_diff > 0:
            loss = self.ambient_loss_rate * (temp_diff / 100.0) * dt
            self.temperature -= loss

        # Check for thermal runaway (heater on, no cooling, high temp)
        if heater_on and not cooling_on and self.temperature > 150:
            self.thermal_runaway = True
            log.error(f"🚨 THERMAL RUNAWAY! Temp: {self.temperature:.1f}°C")
        else:
            self.thermal_runaway = False

        # Check for damage
        if self.temperature > self.damage_temp:
            self.damage = True
            log.error(f"🚨🚨 EQUIPMENT DAMAGE! Temp: {self.temperature:.1f}°C exceeds {self.damage_temp}°C")

        # Constraints
        if self.temperature < self.ambient:
            self.temperature = self.ambient

        return {
            'temperature': self.temperature,
            'thermal_runaway': self.thermal_runaway,
            'damage': self.damage,
            'alarm': 'CRITICAL' if self.damage else ('HIGH' if self.temperature > self.max_safe_temp else 'NORMAL')
        }


class SafetySystem:
    """
    Emergency shutdown and safety interlock system

    Monitors all process variables and triggers shutdowns
    """

    def __init__(self):
        self.shutdown_active = False
        self.interlock_bypass = False
        self.alarm_count = 0

    def check_safety(self, tank_state: Dict, pressure_state: Dict, temp_state: Dict) -> Dict:
        """Check all process variables for unsafe conditions"""
        alarms = []

        # Tank alarms
        if tank_state['overflow']:
            alarms.append("TANK_OVERFLOW")
        if tank_state['cavitation']:
            alarms.append("PUMP_CAVITATION")
        if tank_state['level'] > 95:
            alarms.append("TANK_HIGH_LEVEL")
        if tank_state['level'] < 10:
            alarms.append("TANK_LOW_LEVEL")

        # Pressure alarms
        if pressure_state['rupture']:
            alarms.append("VESSEL_RUPTURE")
        if pressure_state['pressure'] > 130:
            alarms.append("HIGH_PRESSURE")
        if pressure_state['pressure'] < 50:
            alarms.append("LOW_PRESSURE")

        # Temperature alarms
        if temp_state['damage']:
            alarms.append("EQUIPMENT_DAMAGE")
        if temp_state['thermal_runaway']:
            alarms.append("THERMAL_RUNAWAY")
        if temp_state['temperature'] > 200:
            alarms.append("HIGH_TEMPERATURE")

        # Determine shutdown
        critical_alarms = ['VESSEL_RUPTURE', 'EQUIPMENT_DAMAGE', 'TANK_OVERFLOW']
        if any(alarm in alarms for alarm in critical_alarms):
            if not self.interlock_bypass:
                self.shutdown_active = True
                log.error("🚨🚨🚨 EMERGENCY SHUTDOWN ACTIVATED")

        self.alarm_count = len(alarms)

        return {
            'alarms': alarms,
            'shutdown_active': self.shutdown_active,
            'alarm_count': self.alarm_count
        }


class PhysicalProcessSimulator:
    """
    Complete industrial process simulator
    Integrates tank, pressure, temperature, and safety systems
    """

    def __init__(self):
        self.tank = TankSystem(capacity_gallons=1000)
        self.pressure = PressureSystem(max_pressure_psi=150)
        self.temperature = TemperatureSystem(ambient_temp=20.0)
        self.safety = SafetySystem()

        self.running = False
        self.thread = None
        self.update_interval = 0.1  # 100ms update rate

        shared_state.init_state()

    def start(self):
        """Start physical process simulation"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.thread.start()
        log.info("[Physical Process] Started simulation")

    def stop(self):
        """Stop simulation"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        log.info("[Physical Process] Stopped simulation")

    def _simulation_loop(self):
        """Main simulation loop"""
        last_time = time.time()

        while self.running:
            try:
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time

                # Get control inputs from PLCs via shared state
                pump_on = shared_state.get_state('plc1_pump_status', False)
                valve_position = shared_state.get_state('plc1_valve_position', 50.0)
                compressor_on = shared_state.get_state('plc2_compressor_1_status', False)
                relief_valve = shared_state.get_state('plc2_relief_valve_1', False)
                heater_on = shared_state.get_state('plc3_heater_status', False)
                cooling_on = shared_state.get_state('plc3_cooling_status', True)

                # Update physical systems
                tank_state = self.tank.update(dt, pump_on, valve_position)
                pressure_state = self.pressure.update(dt, compressor_on, relief_valve)
                temp_state = self.temperature.update(dt, heater_on, cooling_on)

                # Safety checks
                safety_state = self.safety.check_safety(tank_state, pressure_state, temp_state)

                # If emergency shutdown, force all actuators off
                if safety_state['shutdown_active']:
                    shared_state.update_state('plc1_pump_status', False)
                    shared_state.update_state('plc2_compressor_1_status', False)
                    shared_state.update_state('plc3_heater_status', False)

                # Update shared state with physical values
                shared_state.update_state('physical_tank_level', tank_state['level'])
                shared_state.update_state('physical_pressure', pressure_state['pressure'])
                shared_state.update_state('physical_temperature', temp_state['temperature'])
                shared_state.update_state('physical_alarms', safety_state['alarms'])
                shared_state.update_state('physical_shutdown', safety_state['shutdown_active'])

                # Update PLC sensor readings (with small noise)
                import random
                noise_factor = 0.02  # 2% noise

                tank_reading = tank_state['level'] * (1 + random.uniform(-noise_factor, noise_factor))
                pressure_reading = pressure_state['pressure'] * (1 + random.uniform(-noise_factor, noise_factor))
                temp_reading = temp_state['temperature'] * (1 + random.uniform(-noise_factor, noise_factor))

                shared_state.update_state('plc1_tank_level', int(tank_reading))
                shared_state.update_state('plc2_pressure', int(pressure_reading))
                shared_state.update_state('plc3_temperature', int(temp_reading))

                time.sleep(self.update_interval)

            except Exception as e:
                log.error(f"[Physical Process] Simulation error: {e}")

    def get_state(self) -> PhysicalState:
        """Get current physical state"""
        return PhysicalState(
            timestamp=time.time(),
            tank_level=self.tank.level_percent,
            pressure=self.pressure.pressure,
            temperature=self.temperature.temperature,
            flow_rate=self.tank.valve_outflow_base,
            valve_position=shared_state.get_state('plc1_valve_position', 50.0),
            pump_running=shared_state.get_state('plc1_pump_status', False),
            alarm_state='EMERGENCY' if self.safety.shutdown_active else 'NORMAL'
        )

    def reset(self):
        """Reset simulation to initial state"""
        self.tank = TankSystem(capacity_gallons=1000)
        self.pressure = PressureSystem(max_pressure_psi=150)
        self.temperature = TemperatureSystem(ambient_temp=20.0)
        self.safety = SafetySystem()
        log.info("[Physical Process] Reset to initial state")


# Example usage and testing
if __name__ == '__main__':
    simulator = PhysicalProcessSimulator()
    simulator.start()

    print("\n=== Physical Process Simulator ===\n")
    print("Simulating realistic industrial process...")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            state = simulator.get_state()
            print(f"\r[{time.strftime('%H:%M:%S')}] " +
                  f"Tank: {state.tank_level:5.1f}% | " +
                  f"Pressure: {state.pressure:6.1f} PSI | " +
                  f"Temp: {state.temperature:5.1f}°C | " +
                  f"Pump: {'ON ' if state.pump_running else 'OFF'} | " +
                  f"Status: {state.alarm_state:10s}", end='')
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nStopping simulator...")
        simulator.stop()
