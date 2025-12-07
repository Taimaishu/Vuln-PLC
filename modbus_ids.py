#!/usr/bin/env python3
"""
Modbus Intrusion Detection System (IDS)
Monitors Modbus TCP traffic for anomalies and suspicious patterns

Detection capabilities:
- Unexpected function codes
- Out-of-range register/coil addresses
- Rapid-fire commands (flooding)
- Unauthorized write attempts
- Timing anomalies
- Command sequence violations
"""

import time
import threading
import logging
import os
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import shared_state

# PCAP capture support
try:
    from scapy.all import sniff, wrpcap, TCP, IP, Raw
    from scapy.layers.inet import Ether
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    logging.warning("Scapy not available - PCAP capture disabled. Install with: pip install scapy")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

@dataclass
class ModbusEvent:
    """Single Modbus event"""
    timestamp: float
    source_ip: str
    dest_ip: str
    function_code: int
    address: int
    value: Optional[int] = None
    unit_id: int = 1

@dataclass
class Alert:
    """IDS Alert"""
    timestamp: float
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    alert_type: str
    description: str
    source_ip: str
    details: Dict

class ModbusIDS:
    """
    Modbus TCP Intrusion Detection System

    Detection methods:
    - Signature-based: Known attack patterns
    - Anomaly-based: Statistical deviations from baseline
    - Policy-based: Violations of defined rules
    """

    # Legitimate function codes
    LEGITIMATE_FUNCTION_CODES = {
        1,   # Read Coils
        2,   # Read Discrete Inputs
        3,   # Read Holding Registers
        4,   # Read Input Registers
        5,   # Write Single Coil
        6,   # Write Single Register
        15,  # Write Multiple Coils
        16,  # Write Multiple Registers
        23,  # Read/Write Multiple Registers
    }

    # Critical function codes (require elevated permissions)
    CRITICAL_FUNCTION_CODES = {
        6,   # Write Single Register
        15,  # Write Multiple Coils
        16,  # Write Multiple Registers
    }

    def __init__(self, pcap_dir: str = '/app/pcaps', enable_pcap: bool = True):
        self.enabled = True
        self.alerts: deque = deque(maxlen=1000)  # Keep last 1000 alerts

        # Baseline traffic statistics
        self.baseline = {
            'function_codes': defaultdict(int),
            'source_ips': defaultdict(int),
            'hourly_counts': defaultdict(int),
        }

        # Recent events for pattern detection
        self.recent_events: deque = deque(maxlen=100)

        # Rate limiting tracking
        self.rate_tracker: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        # Policy rules
        self.authorized_writers = set()  # IPs allowed to write
        self.protected_addresses = set()  # Critical registers

        # Background monitoring
        self.running = False
        self.thread = None

        # PCAP capture configuration
        self.pcap_enabled = enable_pcap and SCAPY_AVAILABLE
        self.pcap_dir = pcap_dir
        self.packet_buffer = []
        self.capture_thread = None
        self.capture_running = False
        self.current_pcap_file = None
        self.packets_captured = 0
        self.pcap_rotation_size = 100 * 1024 * 1024  # 100MB
        self.pcap_rotation_interval = 3600  # 1 hour
        self.last_pcap_rotation = time.time()

        # Create PCAP directory
        if self.pcap_enabled:
            os.makedirs(pcap_dir, exist_ok=True)
            log.info(f"[Modbus IDS] PCAP capture enabled, saving to {pcap_dir}")
        else:
            if not SCAPY_AVAILABLE:
                log.warning("[Modbus IDS] PCAP capture disabled - scapy not available")

        shared_state.init_state()

    def start(self):
        """Start IDS monitoring"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

        # Start PCAP capture
        if self.pcap_enabled:
            self.start_packet_capture()

        log.info("[Modbus IDS] Started monitoring")

    def stop(self):
        """Stop IDS monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)

        # Stop PCAP capture
        if self.pcap_enabled:
            self.stop_packet_capture()

        log.info("[Modbus IDS] Stopped monitoring")

    def analyze_event(self, event: ModbusEvent) -> List[Alert]:
        """
        Analyze a Modbus event for suspicious activity
        Returns list of alerts (can be empty)
        """
        alerts = []

        # Add to recent events
        self.recent_events.append(event)

        # Update baseline
        self.baseline['function_codes'][event.function_code] += 1
        self.baseline['source_ips'][event.source_ip] += 1

        # Detection checks
        alerts.extend(self._check_invalid_function_code(event))
        alerts.extend(self._check_unauthorized_write(event))
        alerts.extend(self._check_protected_address(event))
        alerts.extend(self._check_rate_limiting(event))
        alerts.extend(self._check_scan_pattern(event))
        alerts.extend(self._check_timing_anomaly(event))

        # Store alerts
        for alert in alerts:
            self.alerts.append(alert)
            self._log_alert(alert)

        return alerts

    def _check_invalid_function_code(self, event: ModbusEvent) -> List[Alert]:
        """Detect invalid or unusual function codes"""
        alerts = []

        if event.function_code not in self.LEGITIMATE_FUNCTION_CODES:
            alerts.append(Alert(
                timestamp=event.timestamp,
                severity='HIGH',
                alert_type='INVALID_FUNCTION_CODE',
                description=f'Invalid Modbus function code: {event.function_code}',
                source_ip=event.source_ip,
                details={'function_code': event.function_code}
            ))

        return alerts

    def _check_unauthorized_write(self, event: ModbusEvent) -> List[Alert]:
        """Detect write attempts from unauthorized sources"""
        alerts = []

        if event.function_code in self.CRITICAL_FUNCTION_CODES:
            if self.authorized_writers and event.source_ip not in self.authorized_writers:
                alerts.append(Alert(
                    timestamp=event.timestamp,
                    severity='CRITICAL',
                    alert_type='UNAUTHORIZED_WRITE',
                    description=f'Unauthorized write attempt from {event.source_ip}',
                    source_ip=event.source_ip,
                    details={
                        'function_code': event.function_code,
                        'address': event.address,
                        'value': event.value
                    }
                ))

        return alerts

    def _check_protected_address(self, event: ModbusEvent) -> List[Alert]:
        """Detect access to protected/critical addresses"""
        alerts = []

        if event.address in self.protected_addresses:
            if event.function_code in self.CRITICAL_FUNCTION_CODES:
                alerts.append(Alert(
                    timestamp=event.timestamp,
                    severity='CRITICAL',
                    alert_type='PROTECTED_ADDRESS_WRITE',
                    description=f'Write to protected address {event.address}',
                    source_ip=event.source_ip,
                    details={
                        'address': event.address,
                        'function_code': event.function_code,
                        'value': event.value
                    }
                ))

        return alerts

    def _check_rate_limiting(self, event: ModbusEvent) -> List[Alert]:
        """Detect flooding/rapid-fire attacks"""
        alerts = []

        # Track events per source IP
        key = event.source_ip
        self.rate_tracker[key].append(event.timestamp)

        # Check if more than 50 events in last 1 second
        recent = [t for t in self.rate_tracker[key] if event.timestamp - t < 1.0]

        if len(recent) > 50:
            alerts.append(Alert(
                timestamp=event.timestamp,
                severity='HIGH',
                alert_type='RATE_LIMIT_EXCEEDED',
                description=f'Flooding detected: {len(recent)} requests/sec from {event.source_ip}',
                source_ip=event.source_ip,
                details={'rate': len(recent)}
            ))

        return alerts

    def _check_scan_pattern(self, event: ModbusEvent) -> List[Alert]:
        """Detect sequential register scanning"""
        alerts = []

        # Get recent events from same source
        source_events = [e for e in self.recent_events
                        if e.source_ip == event.source_ip
                        and event.timestamp - e.timestamp < 5.0]

        if len(source_events) >= 10:
            # Check if addresses are sequential
            addresses = [e.address for e in source_events[-10:]]
            if self._is_sequential(addresses):
                alerts.append(Alert(
                    timestamp=event.timestamp,
                    severity='MEDIUM',
                    alert_type='REGISTER_SCAN',
                    description=f'Sequential register scan detected from {event.source_ip}',
                    source_ip=event.source_ip,
                    details={'addresses': addresses}
                ))

        return alerts

    def _check_timing_anomaly(self, event: ModbusEvent) -> List[Alert]:
        """Detect timing-based anomalies"""
        alerts = []

        # Check for commands at unusual times (e.g., 2-5 AM)
        hour = datetime.fromtimestamp(event.timestamp).hour
        if 2 <= hour < 5:
            # Check if this is unusual for this source
            if self.baseline['source_ips'][event.source_ip] > 100:
                # Established source acting at odd hours
                alerts.append(Alert(
                    timestamp=event.timestamp,
                    severity='LOW',
                    alert_type='UNUSUAL_TIME',
                    description=f'Command from {event.source_ip} at unusual hour: {hour}:00',
                    source_ip=event.source_ip,
                    details={'hour': hour}
                ))

        return alerts

    def _is_sequential(self, addresses: List[int], max_gap: int = 2) -> bool:
        """Check if addresses are roughly sequential"""
        if len(addresses) < 5:
            return False

        gaps = [addresses[i+1] - addresses[i] for i in range(len(addresses)-1)]
        return all(0 < gap <= max_gap for gap in gaps)

    def _log_alert(self, alert: Alert):
        """Log alert to console and shared state"""
        severity_symbol = {
            'LOW': '⚠️',
            'MEDIUM': '⚠️⚠️',
            'HIGH': '🚨',
            'CRITICAL': '🚨🚨🚨'
        }

        symbol = severity_symbol.get(alert.severity, '⚠️')
        log.warning(f"{symbol} [{alert.severity}] {alert.alert_type}: {alert.description}")

        # Store in shared state
        alert_log = shared_state.get_state('modbus_ids_alerts', [])
        alert_log.append({
            'timestamp': datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'severity': alert.severity,
            'type': alert.alert_type,
            'description': alert.description,
            'source_ip': alert.source_ip,
            'details': alert.details
        })

        # Keep only last 100 alerts
        if len(alert_log) > 100:
            alert_log = alert_log[-100:]

        shared_state.update_state('modbus_ids_alerts', alert_log)

    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                # Periodic analysis of traffic patterns
                self._analyze_baseline()

                # Check for persistent threats
                self._check_persistent_threats()

                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                log.error(f"[Modbus IDS] Monitor loop error: {e}")

    def _analyze_baseline(self):
        """Analyze traffic baseline for anomalies"""
        # Update statistics in shared state
        stats = {
            'total_events': sum(self.baseline['function_codes'].values()),
            'unique_sources': len(self.baseline['source_ips']),
            'total_alerts': len(self.alerts),
            'recent_alerts': len([a for a in self.alerts if time.time() - a.timestamp < 60])
        }

        shared_state.update_state('modbus_ids_stats', stats)

    def _check_persistent_threats(self):
        """Check for persistent malicious activity"""
        # Count alerts per source IP in last hour
        one_hour_ago = time.time() - 3600
        recent_alerts = [a for a in self.alerts if a.timestamp > one_hour_ago]

        alert_counts = defaultdict(int)
        for alert in recent_alerts:
            alert_counts[alert.source_ip] += 1

        # Alert if any source has >10 alerts in last hour
        for source_ip, count in alert_counts.items():
            if count > 10:
                log.error(f"🚨🚨🚨 PERSISTENT THREAT: {source_ip} has {count} alerts in last hour")

    def get_alerts(self, last_n: int = 20) -> List[Dict]:
        """Get recent alerts"""
        return list(self.alerts)[-last_n:]

    def get_statistics(self) -> Dict:
        """Get IDS statistics"""
        return {
            'enabled': self.enabled,
            'total_events': sum(self.baseline['function_codes'].values()),
            'total_alerts': len(self.alerts),
            'function_code_distribution': dict(self.baseline['function_codes']),
            'source_distribution': dict(self.baseline['source_ips']),
            'recent_alerts': len([a for a in self.alerts if time.time() - a.timestamp < 300])
        }

    def add_authorized_writer(self, ip: str):
        """Add IP to authorized writers list"""
        self.authorized_writers.add(ip)
        log.info(f"[Modbus IDS] Added authorized writer: {ip}")

    def add_protected_address(self, address: int):
        """Mark an address as protected"""
        self.protected_addresses.add(address)
        log.info(f"[Modbus IDS] Protected address: {address}")

    # =========================================================================
    # PCAP Capture Methods
    # =========================================================================

    def start_packet_capture(self, interface: str = 'any'):
        """Start capturing Modbus TCP packets"""
        if not self.pcap_enabled:
            return

        if self.capture_running:
            log.warning("[PCAP] Capture already running")
            return

        self.capture_running = True
        self.current_pcap_file = self._get_pcap_filename()

        # Start capture thread
        self.capture_thread = threading.Thread(
            target=self._capture_loop,
            args=(interface,),
            daemon=True
        )
        self.capture_thread.start()

        log.info(f"[PCAP] Started packet capture on {interface}, writing to {self.current_pcap_file}")

    def stop_packet_capture(self):
        """Stop packet capture and save remaining packets"""
        if not self.capture_running:
            return

        self.capture_running = False

        # Wait for capture thread to finish
        if self.capture_thread:
            self.capture_thread.join(timeout=5.0)

        # Save any remaining packets
        if self.packet_buffer:
            self._save_pcap()

        log.info(f"[PCAP] Stopped packet capture. Total packets: {self.packets_captured}")

    def _capture_loop(self, interface: str):
        """Main packet capture loop"""
        try:
            # Capture filter for Modbus TCP (port 502)
            filter_str = "tcp port 502"

            # Start sniffing
            sniff(
                iface=interface,
                filter=filter_str,
                prn=self._packet_handler,
                store=False,
                stop_filter=lambda p: not self.capture_running
            )

        except Exception as e:
            log.error(f"[PCAP] Capture error: {e}")
            self.capture_running = False

    def _packet_handler(self, packet):
        """Handle captured packet"""
        try:
            # Add to buffer
            self.packet_buffer.append(packet)
            self.packets_captured += 1

            # Check if we need to save/rotate
            if len(self.packet_buffer) >= 1000:  # Save every 1000 packets
                self._save_pcap()

            # Check for rotation
            if self._should_rotate_pcap():
                self._rotate_pcap()

        except Exception as e:
            log.error(f"[PCAP] Packet handler error: {e}")

    def _save_pcap(self):
        """Save packet buffer to PCAP file"""
        if not self.packet_buffer:
            return

        try:
            # Append to current PCAP file
            wrpcap(self.current_pcap_file, self.packet_buffer, append=True)
            log.debug(f"[PCAP] Saved {len(self.packet_buffer)} packets to {self.current_pcap_file}")

            # Clear buffer
            self.packet_buffer = []

        except Exception as e:
            log.error(f"[PCAP] Save error: {e}")

    def _should_rotate_pcap(self) -> bool:
        """Check if PCAP file should be rotated"""
        # Time-based rotation
        if time.time() - self.last_pcap_rotation >= self.pcap_rotation_interval:
            return True

        # Size-based rotation
        if self.current_pcap_file and os.path.exists(self.current_pcap_file):
            file_size = os.path.getsize(self.current_pcap_file)
            if file_size >= self.pcap_rotation_size:
                return True

        return False

    def _rotate_pcap(self):
        """Rotate PCAP file"""
        # Save current buffer
        if self.packet_buffer:
            self._save_pcap()

        old_file = self.current_pcap_file
        log.info(f"[PCAP] Rotating PCAP file: {old_file}")

        # Create new file
        self.current_pcap_file = self._get_pcap_filename()
        self.last_pcap_rotation = time.time()

        log.info(f"[PCAP] New PCAP file: {self.current_pcap_file}")

    def _get_pcap_filename(self) -> str:
        """Generate PCAP filename with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"modbus_{timestamp}.pcap"
        return os.path.join(self.pcap_dir, filename)

    def get_pcap_stats(self) -> Dict:
        """Get PCAP capture statistics"""
        stats = {
            'enabled': self.pcap_enabled,
            'running': self.capture_running,
            'packets_captured': self.packets_captured,
            'current_file': self.current_pcap_file,
            'buffer_size': len(self.packet_buffer)
        }

        # Get directory stats
        if self.pcap_enabled and os.path.exists(self.pcap_dir):
            pcap_files = [f for f in os.listdir(self.pcap_dir) if f.endswith('.pcap')]
            total_size = sum(os.path.getsize(os.path.join(self.pcap_dir, f)) for f in pcap_files)

            stats['total_files'] = len(pcap_files)
            stats['total_size_mb'] = total_size / (1024 * 1024)

        return stats


# Example usage and testing
if __name__ == '__main__':
    ids = ModbusIDS()

    # Configure policies
    ids.add_authorized_writer('192.168.100.20')  # HMI server
    ids.add_authorized_writer('192.168.100.30')  # Engineering workstation
    ids.add_protected_address(10)  # Critical safety register

    # Start monitoring
    ids.start()

    # Simulate some events
    print("\n=== Testing Modbus IDS ===\n")

    # Legitimate read
    event1 = ModbusEvent(
        timestamp=time.time(),
        source_ip='192.168.100.20',
        dest_ip='192.168.100.10',
        function_code=3,
        address=0
    )
    alerts = ids.analyze_event(event1)
    print(f"Legitimate read: {len(alerts)} alerts")

    # Unauthorized write
    event2 = ModbusEvent(
        timestamp=time.time(),
        source_ip='192.168.1.100',  # Unauthorized
        dest_ip='192.168.100.10',
        function_code=6,
        address=5,
        value=9999
    )
    alerts = ids.analyze_event(event2)
    print(f"Unauthorized write: {len(alerts)} alerts")

    # Invalid function code
    event3 = ModbusEvent(
        timestamp=time.time(),
        source_ip='192.168.100.20',
        dest_ip='192.168.100.10',
        function_code=99,  # Invalid
        address=0
    )
    alerts = ids.analyze_event(event3)
    print(f"Invalid function code: {len(alerts)} alerts")

    # Flooding attack
    print("\nSimulating flooding attack...")
    for i in range(60):
        event = ModbusEvent(
            timestamp=time.time(),
            source_ip='192.168.1.100',
            dest_ip='192.168.100.10',
            function_code=3,
            address=i
        )
        alerts = ids.analyze_event(event)
        time.sleep(0.01)

    print(f"\nTotal alerts: {len(ids.alerts)}")
    print("\nRecent alerts:")
    for alert in ids.get_alerts(last_n=5):
        print(f"  [{alert.severity}] {alert.alert_type}: {alert.description}")

    print("\nStatistics:")
    stats = ids.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    ids.stop()
