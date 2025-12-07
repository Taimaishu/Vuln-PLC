#!/usr/bin/env python3
"""
Realistic PLC Simulation Engine
Implements scan cycle, ladder logic execution, and proper PLC states
"""

import time
import threading
import logging
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any, Callable
import shared_state

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class PLCState(Enum):
    """PLC operating states"""
    STOP = "STOP"
    RUN = "RUN"
    PROGRAM = "PROGRAM"
    ERROR = "ERROR"

class InstructionType(Enum):
    """Ladder logic instruction types"""
    LD = "LD"      # Load (normally open contact)
    LDN = "LDN"    # Load NOT (normally closed contact)
    AND = "AND"    # AND
    OR = "OR"      # OR
    OUT = "OUT"    # Output coil
    TON = "TON"    # Timer ON-delay
    CTU = "CTU"    # Counter UP
    MOV = "MOV"    # Move/assign value
    ADD = "ADD"    # Addition
    SUB = "SUB"    # Subtraction
    CMP = "CMP"    # Compare

@dataclass
class Instruction:
    """Single ladder logic instruction"""
    type: InstructionType
    operands: List[str]
    comment: str = ""

@dataclass
class Timer:
    """PLC Timer"""
    preset: float
    elapsed: float = 0.0
    running: bool = False
    done: bool = False

@dataclass
class Counter:
    """PLC Counter"""
    preset: int
    count: int = 0
    done: bool = False

class PLCEngine:
    """
    Realistic PLC simulation engine

    Features:
    - Cyclic scan execution (typical 10-100ms)
    - Input/Output image tables
    - Ladder logic interpreter
    - PLC states (RUN/STOP/PROGRAM)
    - Watchdog timer
    """

    def __init__(self, plc_id: str, scan_time_ms: int = 50):
        self.plc_id = plc_id
        self.scan_time = scan_time_ms / 1000.0  # Convert to seconds
        self.state = PLCState.STOP

        # Memory areas (like real PLCs)
        self.input_image = {}      # I0.0, I0.1, etc.
        self.output_image = {}     # Q0.0, Q0.1, etc.
        self.memory_bits = {}      # M0.0, M0.1, etc.
        self.data_blocks = {}      # DB1, DB2, etc.

        # Timers and counters
        self.timers = {}
        self.counters = {}

        # Ladder logic program
        self.program: List[Instruction] = []

        # Execution state
        self.accumulator = False  # Current logic state
        self.scan_count = 0
        self.last_scan_time = 0.0
        self.max_scan_time = 0.0
        self.watchdog_timeout = 1.0  # 1 second watchdog
        self.last_watchdog_reset = time.time()

        # Background thread
        self.running = False
        self.thread = None

        shared_state.init_state()

    def load_program(self, program: List[Instruction]):
        """Load ladder logic program"""
        self.program = program
        log.info(f"[{self.plc_id}] Loaded program with {len(program)} instructions")

    def set_state(self, new_state: PLCState):
        """Change PLC state"""
        old_state = self.state
        self.state = new_state
        log.info(f"[{self.plc_id}] State change: {old_state.value} -> {new_state.value}")

        # Update shared state
        shared_state.update_state(f'{self.plc_id}_state', new_state.value)

    def start(self):
        """Start the PLC engine"""
        if self.running:
            return

        self.running = True
        self.state = PLCState.RUN
        self.thread = threading.Thread(target=self._scan_cycle, daemon=True)
        self.thread.start()
        log.info(f"[{self.plc_id}] PLC engine started (scan time: {self.scan_time*1000:.1f}ms)")

    def stop(self):
        """Stop the PLC engine"""
        self.running = False
        self.state = PLCState.STOP
        if self.thread:
            self.thread.join(timeout=2.0)
        log.info(f"[{self.plc_id}] PLC engine stopped")

    def _scan_cycle(self):
        """Main scan cycle (mimics real PLC operation)"""
        while self.running:
            cycle_start = time.time()

            try:
                # Check watchdog
                if time.time() - self.last_watchdog_reset > self.watchdog_timeout:
                    log.error(f"[{self.plc_id}] WATCHDOG TIMEOUT!")
                    self.set_state(PLCState.ERROR)
                    shared_state.update_state(f'{self.plc_id}_watchdog_fault', True)
                    time.sleep(1.0)
                    continue

                if self.state == PLCState.RUN:
                    # 1. Read inputs (from shared state)
                    self._read_inputs()

                    # 2. Execute program logic
                    self._execute_program()

                    # 3. Write outputs (to shared state)
                    self._write_outputs()

                    # 4. Update timers
                    self._update_timers(self.scan_time)

                    self.scan_count += 1

            except Exception as e:
                log.error(f"[{self.plc_id}] Scan cycle error: {e}")
                self.set_state(PLCState.ERROR)

            # Calculate scan time
            cycle_time = time.time() - cycle_start
            self.last_scan_time = cycle_time
            self.max_scan_time = max(self.max_scan_time, cycle_time)

            # Update diagnostics
            shared_state.update_state(f'{self.plc_id}_scan_time_ms', cycle_time * 1000)
            shared_state.update_state(f'{self.plc_id}_scan_count', self.scan_count)

            # Sleep to maintain scan rate
            sleep_time = max(0, self.scan_time - cycle_time)
            time.sleep(sleep_time)

    def _read_inputs(self):
        """Read inputs from shared state into input image"""
        # Example: Read pump status, sensor values, etc.
        state = shared_state.load_state()

        # Map shared state to input image
        for key, value in state.items():
            if key.startswith(f'{self.plc_id}_input_'):
                bit_addr = key.replace(f'{self.plc_id}_input_', '')
                self.input_image[bit_addr] = value

    def _write_outputs(self):
        """Write outputs from output image to shared state"""
        # Write output image to shared state
        for addr, value in self.output_image.items():
            shared_state.update_state(f'{self.plc_id}_output_{addr}', value)

    def _execute_program(self):
        """Execute ladder logic program"""
        self.accumulator = False

        for instruction in self.program:
            try:
                self._execute_instruction(instruction)
            except Exception as e:
                log.error(f"[{self.plc_id}] Instruction error: {instruction.type} - {e}")

    def _execute_instruction(self, instr: Instruction):
        """Execute a single instruction"""
        if instr.type == InstructionType.LD:
            # Load normally open contact
            addr = instr.operands[0]
            self.accumulator = self._get_bit(addr)

        elif instr.type == InstructionType.LDN:
            # Load normally closed contact
            addr = instr.operands[0]
            self.accumulator = not self._get_bit(addr)

        elif instr.type == InstructionType.AND:
            # AND with contact
            addr = instr.operands[0]
            self.accumulator = self.accumulator and self._get_bit(addr)

        elif instr.type == InstructionType.OR:
            # OR with contact
            addr = instr.operands[0]
            self.accumulator = self.accumulator or self._get_bit(addr)

        elif instr.type == InstructionType.OUT:
            # Output coil
            addr = instr.operands[0]
            self._set_bit(addr, self.accumulator)

        elif instr.type == InstructionType.TON:
            # Timer ON-delay
            timer_name = instr.operands[0]
            preset = float(instr.operands[1])

            if timer_name not in self.timers:
                self.timers[timer_name] = Timer(preset=preset)

            timer = self.timers[timer_name]

            if self.accumulator and not timer.running:
                timer.running = True
                timer.elapsed = 0.0
            elif not self.accumulator:
                timer.running = False
                timer.elapsed = 0.0
                timer.done = False

            timer.done = timer.elapsed >= timer.preset
            self.accumulator = timer.done

        elif instr.type == InstructionType.CMP:
            # Compare values
            op1 = self._get_value(instr.operands[0])
            operator = instr.operands[1]
            op2 = self._get_value(instr.operands[2])

            if operator == '>':
                self.accumulator = op1 > op2
            elif operator == '<':
                self.accumulator = op1 < op2
            elif operator == '==':
                self.accumulator = op1 == op2
            elif operator == '>=':
                self.accumulator = op1 >= op2
            elif operator == '<=':
                self.accumulator = op1 <= op2

    def _update_timers(self, delta_time: float):
        """Update all running timers"""
        for timer in self.timers.values():
            if timer.running:
                timer.elapsed += delta_time

    def _get_bit(self, addr: str) -> bool:
        """Get bit value from memory"""
        if addr.startswith('I'):
            return self.input_image.get(addr, False)
        elif addr.startswith('Q'):
            return self.output_image.get(addr, False)
        elif addr.startswith('M'):
            return self.memory_bits.get(addr, False)
        else:
            # Try shared state
            state_key = f'{self.plc_id}_{addr}'
            return shared_state.get_state(state_key, False)

    def _set_bit(self, addr: str, value: bool):
        """Set bit value in memory"""
        if addr.startswith('Q'):
            self.output_image[addr] = value
        elif addr.startswith('M'):
            self.memory_bits[addr] = value
        else:
            # Write to shared state
            state_key = f'{self.plc_id}_{addr}'
            shared_state.update_state(state_key, value)

    def _get_value(self, operand: str) -> float:
        """Get numeric value (from register or constant)"""
        if operand.isdigit() or operand.replace('.', '', 1).isdigit():
            return float(operand)
        else:
            # Get from shared state
            state_key = f'{self.plc_id}_{operand}'
            return shared_state.get_state(state_key, 0.0)

    def reset_watchdog(self):
        """Reset watchdog timer"""
        self.last_watchdog_reset = time.time()
        shared_state.update_state(f'{self.plc_id}_watchdog_fault', False)

    def get_diagnostics(self) -> Dict[str, Any]:
        """Get PLC diagnostics"""
        return {
            'state': self.state.value,
            'scan_count': self.scan_count,
            'last_scan_time_ms': self.last_scan_time * 1000,
            'max_scan_time_ms': self.max_scan_time * 1000,
            'program_size': len(self.program),
            'input_count': len(self.input_image),
            'output_count': len(self.output_image),
            'timer_count': len(self.timers),
            'counter_count': len(self.counters)
        }


# Example ladder logic programs

def create_tank_control_program() -> List[Instruction]:
    """
    Example: Tank level control with pump

    Network 1: Start pump if level < 30%
    Network 2: Stop pump if level > 80%
    Network 3: Emergency stop
    """
    return [
        # Network 1: Low level start
        Instruction(InstructionType.CMP, ['tank1_level', '<', '30'], "Check if level low"),
        Instruction(InstructionType.AND, ['M0.0'], "AND with run permissive"),
        Instruction(InstructionType.OUT, ['pump1_status'], "Start pump"),

        # Network 2: High level stop
        Instruction(InstructionType.CMP, ['tank1_level', '>', '80'], "Check if level high"),
        Instruction(InstructionType.OUT, ['M0.1'], "Set stop flag"),

        # Network 3: Apply stop flag
        Instruction(InstructionType.LD, ['pump1_status'], "Load pump status"),
        Instruction(InstructionType.AND, ['M0.1'], "AND with stop flag"),
        Instruction(InstructionType.OUT, ['pump1_status'], "Update pump"),

        # Network 4: Emergency stop
        Instruction(InstructionType.LD, ['emergency_stop'], "Load E-stop"),
        Instruction(InstructionType.OUT, ['pump1_status'], "Force pump off"),
    ]


if __name__ == '__main__':
    # Test PLC engine
    engine = PLCEngine('plc1', scan_time_ms=50)

    # Load example program
    program = create_tank_control_program()
    engine.load_program(program)

    # Start engine
    engine.start()

    try:
        while True:
            time.sleep(5)
            diag = engine.get_diagnostics()
            print(f"\n[PLC Diagnostics]")
            print(f"  State: {diag['state']}")
            print(f"  Scans: {diag['scan_count']}")
            print(f"  Scan Time: {diag['last_scan_time_ms']:.2f}ms (max: {diag['max_scan_time_ms']:.2f}ms)")

            engine.reset_watchdog()
    except KeyboardInterrupt:
        engine.stop()
