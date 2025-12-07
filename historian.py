#!/usr/bin/env python3
"""
Historian Service - Time-Series Data Collection
Ports: 8086 (API), 8888 (Web UI)

Simulates OSIsoft PI / InfluxDB-like historian
Collects data from all PLCs for trending and analysis

INTENTIONALLY VULNERABLE - For security testing only
Vulnerabilities: Time-series injection, unauthorized access, query injection
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import threading
import time
from datetime import datetime, timedelta
import random
import json
import shared_state

app = Flask(__name__)
app.secret_key = 'historian-weak-secret-456'

shared_state.init_state()

# Initialize historian database
def init_historian_db():
    conn = sqlite3.connect('historian.db')
    c = conn.cursor()

    # Time-series data table
    c.execute('''CREATE TABLE IF NOT EXISTS timeseries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  plc_id INTEGER,
                  tag_name TEXT,
                  value REAL,
                  quality TEXT)''')

    # Alarms table
    c.execute('''CREATE TABLE IF NOT EXISTS alarms
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  plc_id INTEGER,
                  alarm_type TEXT,
                  message TEXT,
                  severity TEXT,
                  acknowledged INTEGER DEFAULT 0)''')

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS historian_users
                 (id INTEGER PRIMARY KEY,
                  username TEXT,
                  password TEXT,
                  role TEXT)''')

    # Insert default users
    c.execute("DELETE FROM historian_users")
    c.execute("INSERT INTO historian_users VALUES (1, 'historian', 'data123', 'admin')")
    c.execute("INSERT INTO historian_users VALUES (2, 'analyst', 'trend456', 'viewer')")
    c.execute("INSERT INTO historian_users VALUES (3, 'guest', 'guest', 'guest')")

    conn.commit()
    conn.close()

init_historian_db()

def data_collector():
    """Collect data from all PLCs every 5 seconds"""
    while True:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn = sqlite3.connect('historian.db')
            c = conn.cursor()

            state = shared_state.load_state()

            # Collect PLC-1 data
            for key, value in state.items():
                if key.startswith('tank') or key.startswith('pump') or key.startswith('valve'):
                    if isinstance(value, (int, float, bool)):
                        c.execute("INSERT INTO timeseries (timestamp, plc_id, tag_name, value, quality) VALUES (?, ?, ?, ?, ?)",
                                (timestamp, 1, key, float(value), 'GOOD'))

            # Collect PLC-2 data
            for key, value in state.items():
                if key.startswith('plc2_'):
                    tag = key.replace('plc2_', '')
                    if isinstance(value, (int, float, bool)):
                        c.execute("INSERT INTO timeseries (timestamp, plc_id, tag_name, value, quality) VALUES (?, ?, ?, ?, ?)",
                                (timestamp, 2, tag, float(value), 'GOOD'))

            # Collect PLC-3 data
            for key, value in state.items():
                if key.startswith('plc3_'):
                    tag = key.replace('plc3_', '')
                    if isinstance(value, (int, float, bool)):
                        c.execute("INSERT INTO timeseries (timestamp, plc_id, tag_name, value, quality) VALUES (?, ?, ?, ?, ?)",
                                (timestamp, 3, tag, float(value), 'GOOD'))

            # Collect PLC-4 data
            for key, value in state.items():
                if key.startswith('plc4_'):
                    tag = key.replace('plc4_', '')
                    if isinstance(value, (int, float, bool)):
                        c.execute("INSERT INTO timeseries (timestamp, plc_id, tag_name, value, quality) VALUES (?, ?, ?, ?, ?)",
                                (timestamp, 4, tag, float(value), 'GOOD'))

            conn.commit()
            conn.close()

            # Clean up old data (keep last 24 hours)
            cleanup_old_data()

            time.sleep(5)
        except Exception as e:
            print(f"Data collector error: {e}")
            time.sleep(5)

def cleanup_old_data():
    """Remove data older than 24 hours"""
    try:
        cutoff = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect('historian.db')
        c = conn.cursor()
        c.execute("DELETE FROM timeseries WHERE timestamp < ?", (cutoff,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Cleanup error: {e}")

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """VULNERABILITY: SQL Injection"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # VULNERABILITY: SQL Injection
        conn = sqlite3.connect('historian.db')
        c = conn.cursor()
        query = f"SELECT * FROM historian_users WHERE username='{username}' AND password='{password}'"

        try:
            c.execute(query)
            user = c.fetchone()

            if user:
                session['username'] = user[1]
                session['role'] = user[3]
                conn.close()
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid credentials'
        except Exception as e:
            error = f'Database error: {str(e)}'

        conn.close()

    return render_template('historian_login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('historian_dashboard.html',
                          username=session['username'],
                          role=session['role'])

@app.route('/api/query', methods=['POST'])
def api_query():
    """VULNERABILITY: SQL Injection in query endpoint"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or {}
    plc_id = data.get('plc_id', 'all')
    tag_name = data.get('tag_name', '%')
    hours = data.get('hours', 1)

    # VULNERABILITY: SQL Injection in query
    conn = sqlite3.connect('historian.db')
    c = conn.cursor()

    start_time = (datetime.now() - timedelta(hours=int(hours))).strftime('%Y-%m-%d %H:%M:%S')

    if plc_id == 'all':
        query = f"SELECT * FROM timeseries WHERE tag_name LIKE '{tag_name}' AND timestamp > '{start_time}' ORDER BY timestamp DESC LIMIT 1000"
    else:
        query = f"SELECT * FROM timeseries WHERE plc_id={plc_id} AND tag_name LIKE '{tag_name}' AND timestamp > '{start_time}' ORDER BY timestamp DESC LIMIT 1000"

    try:
        c.execute(query)
        rows = c.fetchall()
        conn.close()

        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'timestamp': row[1],
                'plc_id': row[2],
                'tag_name': row[3],
                'value': row[4],
                'quality': row[5]
            })

        return jsonify({'success': True, 'data': results, 'count': len(results)})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/inject', methods=['POST'])
def api_inject():
    """VULNERABILITY: Time-series injection - allows inserting fake data"""
    # VULNERABILITY: No authentication check
    # if 'username' not in session:
    #     return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or {}
    timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    plc_id = data.get('plc_id', 1)
    tag_name = data.get('tag_name', '')
    value = data.get('value', 0)
    quality = data.get('quality', 'BAD')

    conn = sqlite3.connect('historian.db')
    c = conn.cursor()
    c.execute("INSERT INTO timeseries (timestamp, plc_id, tag_name, value, quality) VALUES (?, ?, ?, ?, ?)",
              (timestamp, plc_id, tag_name, value, quality))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': 'Data injected',
        'warning': 'No validation performed'
    })

@app.route('/api/trending/<plc_id>/<tag_name>')
def api_trending(plc_id, tag_name):
    """Get trending data for a specific tag"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    hours = request.args.get('hours', 1, type=int)
    start_time = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('historian.db')
    c = conn.cursor()
    c.execute("SELECT timestamp, value FROM timeseries WHERE plc_id=? AND tag_name=? AND timestamp > ? ORDER BY timestamp ASC",
              (plc_id, tag_name, start_time))
    rows = c.fetchall()
    conn.close()

    timestamps = [row[0] for row in rows]
    values = [row[1] for row in rows]

    return jsonify({
        'timestamps': timestamps,
        'values': values,
        'count': len(rows)
    })

@app.route('/api/tags')
def api_tags():
    """Get all available tags"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = sqlite3.connect('historian.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT plc_id, tag_name FROM timeseries ORDER BY plc_id, tag_name")
    rows = c.fetchall()
    conn.close()

    tags = {}
    for row in rows:
        plc_id = f"PLC-{row[0]}"
        if plc_id not in tags:
            tags[plc_id] = []
        tags[plc_id].append(row[1])

    return jsonify({'tags': tags})

@app.route('/api/alarms')
def api_alarms():
    """Get recent alarms"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = sqlite3.connect('historian.db')
    c = conn.cursor()
    c.execute("SELECT * FROM alarms ORDER BY timestamp DESC LIMIT 100")
    rows = c.fetchall()
    conn.close()

    alarms = []
    for row in rows:
        alarms.append({
            'id': row[0],
            'timestamp': row[1],
            'plc_id': row[2],
            'alarm_type': row[3],
            'message': row[4],
            'severity': row[5],
            'acknowledged': row[6]
        })

    return jsonify({'alarms': alarms})

@app.route('/api/export', methods=['POST'])
def api_export():
    """VULNERABILITY: Arbitrary file read via export"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    format_type = request.form.get('format', 'csv')
    filename = request.form.get('filename', 'export.csv')

    # VULNERABILITY: Directory traversal
    if format_type == 'custom':
        # Allows reading arbitrary files
        try:
            with open(filename, 'r') as f:
                content = f.read()
            return jsonify({'success': True, 'data': content})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    return jsonify({'success': True, 'message': 'Export prepared'})

# Start data collector thread
collector_thread = threading.Thread(target=data_collector, daemon=True)
collector_thread.start()

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  Historian Service - Time-Series Data Collection          ║
    ║  FOR SECURITY TESTING AND EDUCATION ONLY                  ║
    ╚═══════════════════════════════════════════════════════════╝

    Default Credentials:
      historian / data123  (Admin)
      analyst / trend456   (Viewer)
      guest / guest        (Guest)

    Web Interface: http://localhost:8888
    API Endpoint:  http://localhost:8086 (simulated)

    Known Vulnerabilities:
      • SQL Injection in login
      • SQL Injection in query endpoint
      • Time-series data injection (no auth)
      • Unauthorized data access
      • Directory traversal in export
      • No input validation

    WARNING: DO NOT EXPOSE TO INTERNET
    """)

    app.run(host='0.0.0.0', port=8888, debug=True)
