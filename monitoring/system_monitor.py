#!/usr/bin/env python3
"""
System Monitoring Dashboard
Real-time monitoring of all ICS components:
- PLC engines (scan cycles, diagnostics)
- Modbus IDS (alerts, statistics)
- Protocol servers (S7, Modbus)
- Network traffic
- Security events
"""

import time
import threading
import logging
from datetime import datetime
from typing import Dict, List
import shared_state

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class SystemMonitor:
    """
    Central monitoring system for ICS infrastructure

    Monitors:
    - PLC scan cycles and health
    - Security alerts from IDS
    - Protocol traffic patterns
    - System resource usage
    - Anomaly detection
    """

    def __init__(self):
        self.running = False
        self.thread = None
        self.start_time = time.time()

        # Metrics tracking
        self.metrics = {
            'plc_engines': {},
            'modbus_ids': {},
            's7_servers': {},
            'network': {},
            'security': {
                'total_alerts': 0,
                'critical_alerts': 0,
                'last_alert_time': None
            }
        }

        shared_state.init_state()

    def start(self):
        """Start monitoring"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

        log.info("""
╔════════════════════════════════════════════════════════════════╗
║          ICS SYSTEM MONITOR - Real-Time Dashboard              ║
╚════════════════════════════════════════════════════════════════╝

Monitoring:
  ✓ PLC Engine Status & Diagnostics
  ✓ Modbus IDS Alerts & Statistics
  ✓ S7 Protocol Server Activity
  ✓ Network Traffic Patterns
  ✓ Security Events & Anomalies

Dashboard updates every 5 seconds
Press Ctrl+C to stop
        """)

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        log.info("[Monitor] Stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        iteration = 0

        while self.running:
            try:
                iteration += 1

                # Collect metrics
                self._collect_plc_metrics()
                self._collect_ids_metrics()
                self._collect_network_metrics()
                self._check_security_status()

                # Display dashboard every 5 seconds
                if iteration % 5 == 0:
                    self._display_dashboard()

                time.sleep(1)

            except Exception as e:
                log.error(f"[Monitor] Error: {e}")

    def _collect_plc_metrics(self):
        """Collect PLC engine metrics"""
        plc_ids = ['plc1', 'plc2', 'plc3', 'plc4']

        for plc_id in plc_ids:
            # Get scan time
            scan_time = shared_state.get_state(f'{plc_id}_scan_time_ms', 0.0)
            scan_count = shared_state.get_state(f'{plc_id}_scan_count', 0)
            plc_state = shared_state.get_state(f'{plc_id}_state', 'UNKNOWN')
            watchdog_fault = shared_state.get_state(f'{plc_id}_watchdog_fault', False)

            self.metrics['plc_engines'][plc_id] = {
                'state': plc_state,
                'scan_time_ms': scan_time,
                'scan_count': scan_count,
                'watchdog_fault': watchdog_fault,
                'health': 'FAULT' if watchdog_fault else 'OK'
            }

    def _collect_ids_metrics(self):
        """Collect Modbus IDS metrics"""
        ids_stats = shared_state.get_state('modbus_ids_stats', {})
        ids_alerts = shared_state.get_state('modbus_ids_alerts', [])

        # Count alerts by severity
        severity_counts = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
        recent_alerts = 0
        five_min_ago = time.time() - 300

        for alert in ids_alerts:
            severity_counts[alert.get('severity', 'LOW')] += 1

            # Count recent alerts (last 5 minutes)
            try:
                alert_time = datetime.strptime(alert['timestamp'], '%Y-%m-%d %H:%M:%S').timestamp()
                if alert_time > five_min_ago:
                    recent_alerts += 1
            except:
                pass

        self.metrics['modbus_ids'] = {
            'total_events': ids_stats.get('total_events', 0),
            'total_alerts': ids_stats.get('total_alerts', 0),
            'recent_alerts': recent_alerts,
            'severity_counts': severity_counts,
            'status': 'ACTIVE' if ids_stats.get('enabled', False) else 'INACTIVE'
        }

        # Update security metrics
        self.metrics['security']['total_alerts'] = ids_stats.get('total_alerts', 0)
        self.metrics['security']['critical_alerts'] = severity_counts['CRITICAL']
        if ids_alerts:
            self.metrics['security']['last_alert_time'] = ids_alerts[-1].get('timestamp')

    def _collect_network_metrics(self):
        """Collect network traffic metrics"""
        traffic_log = shared_state.get_state('network_traffic_log', [])

        # Analyze recent traffic (last 100 entries)
        protocol_counts = {}
        source_counts = {}

        for entry in traffic_log[-100:]:
            protocol = entry.get('protocol', 'unknown')
            source = entry.get('source', 'unknown')

            protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1

        self.metrics['network'] = {
            'total_packets': len(traffic_log),
            'recent_packets': len(traffic_log[-100:]),
            'protocol_distribution': protocol_counts,
            'top_sources': dict(sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        }

    def _check_security_status(self):
        """Check overall security status"""
        # Check for critical conditions
        critical_conditions = []

        # Check for PLC faults
        for plc_id, metrics in self.metrics['plc_engines'].items():
            if metrics.get('watchdog_fault'):
                critical_conditions.append(f"{plc_id.upper()} watchdog fault")

            if metrics.get('state') == 'ERROR':
                critical_conditions.append(f"{plc_id.upper()} in ERROR state")

        # Check for high alert rate
        ids_metrics = self.metrics.get('modbus_ids', {})
        if ids_metrics.get('recent_alerts', 0) > 10:
            critical_conditions.append(f"High IDS alert rate: {ids_metrics['recent_alerts']}/5min")

        # Check for critical IDS alerts
        if ids_metrics.get('severity_counts', {}).get('CRITICAL', 0) > 0:
            critical_conditions.append(f"{ids_metrics['severity_counts']['CRITICAL']} CRITICAL security alerts")

        # Update security status
        if critical_conditions:
            self.metrics['security']['status'] = 'CRITICAL'
            self.metrics['security']['issues'] = critical_conditions
        else:
            self.metrics['security']['status'] = 'NORMAL'
            self.metrics['security']['issues'] = []

    def _display_dashboard(self):
        """Display real-time dashboard"""
        uptime = time.time() - self.start_time
        uptime_str = time.strftime('%H:%M:%S', time.gmtime(uptime))

        print("\n" + "="*70)
        print(f"ICS SYSTEM MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Uptime: {uptime_str}")
        print("="*70)

        # Security Status
        sec = self.metrics['security']
        status_symbol = "🔴" if sec['status'] == 'CRITICAL' else "🟢"
        print(f"\n{status_symbol} SECURITY STATUS: {sec['status']}")
        print(f"  Total Alerts: {sec['total_alerts']} (Critical: {sec['critical_alerts']})")
        if sec.get('last_alert_time'):
            print(f"  Last Alert: {sec['last_alert_time']}")
        if sec.get('issues'):
            print(f"  ⚠️  Issues:")
            for issue in sec['issues']:
                print(f"      • {issue}")

        # PLC Status
        print(f"\n🏭 PLC ENGINES:")
        for plc_id, metrics in sorted(self.metrics['plc_engines'].items()):
            state_symbol = "✓" if metrics['health'] == 'OK' else "✗"
            print(f"  {state_symbol} {plc_id.upper():6s} | State: {metrics['state']:7s} | " +
                  f"Scan: {metrics['scan_time_ms']:6.2f}ms | " +
                  f"Count: {metrics['scan_count']:8d}")

        # Modbus IDS
        ids = self.metrics['modbus_ids']
        print(f"\n🛡️  MODBUS IDS:")
        print(f"  Status: {ids.get('status', 'UNKNOWN')}")
        print(f"  Events: {ids.get('total_events', 0):,} | Alerts: {ids.get('total_alerts', 0)} " +
              f"(Recent: {ids.get('recent_alerts', 0)})")

        if ids.get('severity_counts'):
            sev = ids['severity_counts']
            print(f"  Severity: LOW={sev['LOW']} MED={sev['MEDIUM']} " +
                  f"HIGH={sev['HIGH']} CRIT={sev['CRITICAL']}")

        # Network Traffic
        net = self.metrics['network']
        print(f"\n📡 NETWORK TRAFFIC:")
        print(f"  Total Packets: {net.get('total_packets', 0):,} (Recent: {net.get('recent_packets', 0)})")

        if net.get('protocol_distribution'):
            protocols = net['protocol_distribution']
            proto_str = ", ".join([f"{k}={v}" for k, v in protocols.items()])
            print(f"  Protocols: {proto_str}")

        if net.get('top_sources'):
            print(f"  Top Sources:")
            for source, count in list(net['top_sources'].items())[:3]:
                print(f"    • {source}: {count} packets")

        print("\n" + "-"*70)

    def get_health_summary(self) -> Dict:
        """Get overall system health summary"""
        # Count healthy vs faulty PLCs
        plc_count = len(self.metrics['plc_engines'])
        plc_healthy = sum(1 for m in self.metrics['plc_engines'].values() if m['health'] == 'OK')

        return {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': time.time() - self.start_time,
            'security_status': self.metrics['security']['status'],
            'plc_health': f"{plc_healthy}/{plc_count}",
            'total_alerts': self.metrics['security']['total_alerts'],
            'critical_alerts': self.metrics['security']['critical_alerts'],
            'ids_active': self.metrics['modbus_ids'].get('status') == 'ACTIVE',
            'issues': self.metrics['security'].get('issues', [])
        }


def create_monitoring_dashboard_web():
    """Create simple web dashboard using Flask"""
    from flask import Flask, jsonify, render_template_string

    app = Flask(__name__)
    monitor = SystemMonitor()

    HTML_TEMPLATE = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ICS System Monitor</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Courier New', monospace;
                background: #0a0a0a;
                color: #0f0;
                padding: 20px;
            }
            .header {
                background: #1a1a1a;
                padding: 20px;
                border: 2px solid #0f0;
                margin-bottom: 20px;
            }
            .status-ok { color: #0f0; }
            .status-critical { color: #f00; }
            .panel {
                background: #1a1a1a;
                border: 1px solid #333;
                padding: 15px;
                margin-bottom: 15px;
            }
            .panel h2 { color: #0ff; margin-bottom: 10px; }
            .metric { padding: 5px 0; }
            .alert { background: #3a0000; border: 1px solid #f00; padding: 10px; margin: 5px 0; }
        </style>
        <script>
            function updateDashboard() {
                fetch('/api/health')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('status').textContent = data.security_status;
                        document.getElementById('status').className =
                            data.security_status === 'CRITICAL' ? 'status-critical' : 'status-ok';

                        document.getElementById('plc-health').textContent = data.plc_health;
                        document.getElementById('alerts').textContent = data.total_alerts;
                        document.getElementById('uptime').textContent =
                            Math.floor(data.uptime_seconds / 60) + ' minutes';

                        // Update issues
                        const issuesDiv = document.getElementById('issues');
                        if (data.issues && data.issues.length > 0) {
                            issuesDiv.innerHTML = data.issues.map(i =>
                                '<div class="alert">⚠️ ' + i + '</div>'
                            ).join('');
                        } else {
                            issuesDiv.innerHTML = '<div class="status-ok">✓ No issues detected</div>';
                        }
                    });
            }

            setInterval(updateDashboard, 2000);
            updateDashboard();
        </script>
    </head>
    <body>
        <div class="header">
            <h1>🏭 ICS SYSTEM MONITOR</h1>
            <p>Real-time monitoring of industrial control systems</p>
        </div>

        <div class="panel">
            <h2>🛡️ Security Status</h2>
            <div class="metric">Status: <span id="status" class="status-ok">NORMAL</span></div>
            <div class="metric">Total Alerts: <span id="alerts">0</span></div>
            <div class="metric">Uptime: <span id="uptime">0 minutes</span></div>
        </div>

        <div class="panel">
            <h2>🏭 PLC Health</h2>
            <div class="metric">Healthy PLCs: <span id="plc-health">0/0</span></div>
        </div>

        <div class="panel">
            <h2>⚠️ Active Issues</h2>
            <div id="issues">
                <div class="status-ok">✓ No issues detected</div>
            </div>
        </div>

        <div class="panel">
            <p style="color: #666; font-size: 12px;">
                Dashboard auto-refreshes every 2 seconds<br>
                For detailed logs, check console output
            </p>
        </div>
    </body>
    </html>
    '''

    @app.route('/')
    def dashboard():
        return render_template_string(HTML_TEMPLATE)

    @app.route('/api/health')
    def api_health():
        return jsonify(monitor.get_health_summary())

    # Start monitor
    monitor.start()

    print("\n🌐 Web Dashboard: http://localhost:5999")
    app.run(host='0.0.0.0', port=5999, debug=False)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--web':
        # Start web dashboard
        create_monitoring_dashboard_web()
    else:
        # Start console monitor
        monitor = SystemMonitor()
        monitor.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitor...")
            monitor.stop()
