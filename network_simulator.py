#!/usr/bin/env python3
"""
ICS Network Traffic Simulator
Generates realistic industrial network traffic with intentional security issues

Simulates:
- CorpNet (192.168.1.0/24)
- OT Zone (192.168.100.0/24)
- DMZ (192.168.50.0/24)
- Lack of proper segmentation
- Realistic traffic patterns
- Network issues (packet loss, misbehaving devices)
- Safety incidents
"""

import socket
import struct
import random
import time
import threading
import logging
from datetime import datetime
import shared_state

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Network Topology (INTENTIONALLY INSECURE)
NETWORK_SEGMENTS = {
    'corpnet': {
        'subnet': '192.168.1.0/24',
        'devices': {
            'employee_laptop': '192.168.1.100',
            'email_server': '192.168.1.10',
            'file_server': '192.168.1.20',
            'printer': '192.168.1.30'
        }
    },
    'ot_zone': {
        'subnet': '192.168.100.0/24',
        'devices': {
            'plc1': '192.168.100.10',  # Tank Control
            'plc2': '192.168.100.11',  # Pressure Control
            'plc3': '192.168.100.12',  # Temperature Control
            'plc4': '192.168.100.13',  # Safety/ESD
            'hmi_server': '192.168.100.20',
            'engineering_ws': '192.168.100.30',
            'misbehaving_device': '192.168.100.99'  # Problematic device
        }
    },
    'dmz': {
        'subnet': '192.168.50.0/24',
        'devices': {
            'historian': '192.168.50.10',
            'web_portal': '192.168.50.20'
        }
    }
}

# VULNERABILITY: No firewall rules between segments
FIREWALL_RULES = {
    'corpnet_to_ot': 'ALLOW_ALL',  # Should be DENY
    'ot_to_corpnet': 'ALLOW_ALL',  # Should be DENY
    'corpnet_to_dmz': 'ALLOW_ALL',
    'ot_to_dmz': 'ALLOW_ALL',
    'dmz_to_ot': 'ALLOW_ALL'  # Should be RESTRICTED
}

# Traffic patterns
TRAFFIC_PATTERNS = {
    'hmi_polling': {
        'source': 'hmi_server',
        'destinations': ['plc1', 'plc2', 'plc3', 'plc4'],
        'protocol': 'modbus',
        'interval': 1.0,  # Poll every second
        'description': 'HMI polling PLCs for real-time data'
    },
    'historian_collection': {
        'source': 'historian',
        'destinations': ['plc1', 'plc2', 'plc3', 'plc4'],
        'protocol': 'modbus',
        'interval': 5.0,  # Every 5 seconds
        'description': 'Historian collecting time-series data'
    },
    'engineering_access': {
        'source': 'engineering_ws',
        'destinations': ['plc1', 'plc2', 'plc3', 'plc4'],
        'protocol': 'modbus',
        'interval': random.uniform(30, 300),  # Occasional access
        'description': 'Engineer accessing PLC registers'
    },
    'corpnet_intrusion': {
        'source': 'employee_laptop',
        'destinations': ['plc1', 'hmi_server'],
        'protocol': 'modbus',
        'interval': random.uniform(60, 600),  # Suspicious access
        'description': 'VULNERABILITY: Corp user accessing OT network'
    },
    'misbehaving_device_spam': {
        'source': 'misbehaving_device',
        'destinations': ['plc1', 'plc2', 'plc3', 'plc4', 'hmi_server'],
        'protocol': 'modbus',
        'interval': 0.1,  # Too frequent - causing issues
        'description': 'Faulty device spamming network'
    }
}

# Packet loss simulation
PACKET_LOSS_RATE = 0.02  # 2% packet loss

# Safety incident scenarios
SAFETY_INCIDENTS = [
    {
        'name': 'pressure_runaway',
        'trigger_time': 300,  # 5 minutes after start
        'description': 'PLC-2 pressure vessel exceeds safe limits',
        'actions': [
            ('plc2_pressure_vessel_1', 180.0),  # Dangerously high
            ('plc2_safety_interlock_1', False)
        ]
    },
    {
        'name': 'thermal_incident',
        'trigger_time': 600,  # 10 minutes
        'description': 'PLC-3 thermal runaway condition',
        'actions': [
            ('plc3_thermal_runaway', True),
            ('plc3_zone1_temp', 150.0)
        ]
    },
    {
        'name': 'safety_bypass',
        'trigger_time': 900,  # 15 minutes
        'description': 'Safety system compromised',
        'actions': [
            ('plc4_safety_bypass_mode', True),
            ('plc4_watchdog_enabled', False)
        ]
    }
]

class NetworkTrafficSimulator:
    def __init__(self):
        self.running = False
        self.start_time = time.time()
        shared_state.init_state()

    def simulate_modbus_traffic(self, source, destination, function_code=3):
        """Simulate Modbus TCP traffic"""
        # Simulate packet loss
        if random.random() < PACKET_LOSS_RATE:
            log.warning(f"[PACKET LOSS] {source} -> {destination}")
            return False

        # Get device IPs
        source_ip = self.get_device_ip(source)
        dest_ip = self.get_device_ip(destination)

        if not source_ip or not dest_ip:
            return False

        # Log traffic
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log.info(f"[{timestamp}] Modbus: {source_ip}:{random.randint(49152, 65535)} -> {dest_ip}:502 FC={function_code}")

        # Store in shared state for IDS analysis
        traffic_entry = {
            'timestamp': timestamp,
            'source': source_ip,
            'destination': dest_ip,
            'protocol': 'modbus',
            'function_code': function_code
        }

        # Add to traffic log
        traffic_log = shared_state.get_state('network_traffic_log', [])
        traffic_log.append(traffic_entry)

        # Keep only last 100 entries (reduced to limit state file size)
        if len(traffic_log) > 100:
            traffic_log = traffic_log[-100:]

        shared_state.update_state('network_traffic_log', traffic_log)

        return True

    def get_device_ip(self, device_name):
        """Get IP address for a device"""
        for segment in NETWORK_SEGMENTS.values():
            if device_name in segment['devices']:
                return segment['devices'][device_name]
        return None

    def hmi_polling_thread(self):
        """Simulate HMI polling all PLCs"""
        pattern = TRAFFIC_PATTERNS['hmi_polling']
        while self.running:
            for plc in pattern['destinations']:
                self.simulate_modbus_traffic(pattern['source'], plc, function_code=3)  # Read holding registers
            time.sleep(pattern['interval'])

    def historian_collection_thread(self):
        """Simulate historian collecting data"""
        pattern = TRAFFIC_PATTERNS['historian_collection']
        while self.running:
            for plc in pattern['destinations']:
                self.simulate_modbus_traffic(pattern['source'], plc, function_code=4)  # Read input registers
            time.sleep(pattern['interval'])

    def engineering_access_thread(self):
        """Simulate occasional engineering workstation access"""
        pattern = TRAFFIC_PATTERNS['engineering_access']
        while self.running:
            plc = random.choice(pattern['destinations'])
            fc = random.choice([3, 4, 6, 16])  # Read/Write operations
            self.simulate_modbus_traffic(pattern['source'], plc, function_code=fc)
            time.sleep(random.uniform(30, 300))

    def corpnet_intrusion_thread(self):
        """VULNERABILITY: Simulate unauthorized corporate network access to OT"""
        pattern = TRAFFIC_PATTERNS['corpnet_intrusion']
        while self.running:
            # This should be blocked by firewall but isn't
            dest = random.choice(pattern['destinations'])
            self.simulate_modbus_traffic(pattern['source'], dest, function_code=3)
            log.warning(f"[SECURITY] Unauthorized CorpNet -> OT traffic detected!")
            time.sleep(random.uniform(60, 600))

    def misbehaving_device_thread(self):
        """Simulate a faulty device causing network issues"""
        pattern = TRAFFIC_PATTERNS['misbehaving_device_spam']
        while self.running:
            # Spam the network with unnecessary traffic
            for _ in range(10):  # Burst of 10 packets
                dest = random.choice(pattern['destinations'])
                self.simulate_modbus_traffic(pattern['source'], dest, function_code=3)
            time.sleep(pattern['interval'])

    def safety_incident_monitor(self):
        """Monitor for and trigger safety incidents"""
        while self.running:
            elapsed = time.time() - self.start_time

            for incident in SAFETY_INCIDENTS:
                if abs(elapsed - incident['trigger_time']) < 5:  # Within 5 seconds of trigger time
                    log.error(f"[SAFETY INCIDENT] {incident['name']}: {incident['description']}")

                    # Execute incident actions
                    for key, value in incident['actions']:
                        shared_state.update_state(key, value)
                        log.error(f"  -> Set {key} = {value}")

            time.sleep(5)

    def network_statistics_thread(self):
        """Calculate and log network statistics"""
        while self.running:
            time.sleep(60)  # Every minute

            traffic_log = shared_state.get_state('network_traffic_log', [])

            if traffic_log:
                # Calculate statistics
                total_packets = len(traffic_log)
                last_minute = [t for t in traffic_log if self._within_last_minute(t['timestamp'])]

                log.info(f"[STATS] Total packets: {total_packets}, Last minute: {len(last_minute)}")

                # Detect anomalies
                if len(last_minute) > 100:
                    log.warning(f"[ANOMALY] High traffic rate detected: {len(last_minute)} packets/min")

    def _within_last_minute(self, timestamp_str):
        """Check if timestamp is within last minute"""
        try:
            ts = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
            now = datetime.now()
            return (now - ts).total_seconds() < 60
        except:
            return False

    def start(self):
        """Start all network simulation threads"""
        self.running = True
        self.start_time = time.time()

        log.info("=" * 70)
        log.info("ICS Network Traffic Simulator Starting")
        log.info("=" * 70)
        log.info("Network Topology:")
        for segment_name, segment_info in NETWORK_SEGMENTS.items():
            log.info(f"  {segment_name.upper()}: {segment_info['subnet']}")
            for device, ip in segment_info['devices'].items():
                log.info(f"    {device}: {ip}")
        log.info("")
        log.info("Firewall Status: MISCONFIGURED")
        for rule, policy in FIREWALL_RULES.items():
            log.info(f"  {rule}: {policy}")
        log.info("")
        log.info("Traffic Patterns:")
        for pattern_name, pattern in TRAFFIC_PATTERNS.items():
            log.info(f"  {pattern_name}: {pattern['description']}")
        log.info("=" * 70)

        # Start traffic threads
        threads = [
            threading.Thread(target=self.hmi_polling_thread, daemon=True),
            threading.Thread(target=self.historian_collection_thread, daemon=True),
            threading.Thread(target=self.engineering_access_thread, daemon=True),
            threading.Thread(target=self.corpnet_intrusion_thread, daemon=True),
            threading.Thread(target=self.misbehaving_device_thread, daemon=True),
            threading.Thread(target=self.safety_incident_monitor, daemon=True),
            threading.Thread(target=self.network_statistics_thread, daemon=True)
        ]

        for thread in threads:
            thread.start()

        log.info("All traffic simulation threads started")
        log.info("Monitoring for safety incidents...")

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the simulator"""
        log.info("Stopping network simulator...")
        self.running = False

if __name__ == '__main__':
    simulator = NetworkTrafficSimulator()
    simulator.start()
