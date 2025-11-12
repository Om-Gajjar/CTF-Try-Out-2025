# Blueprint Heist - Challenge Analysis

**Status:** In Progress  
**Difficulty:** Medium  
**Points:** 1000

---

## Challenge Overview

Urban Planning Commission web application with:
- wkhtmltopdf for PDF generation
- GraphQL API (requires admin auth)
- JWT authentication
- MySQL database
- Flag at `/root/flag.txt` with `/readflag` SUID binary

---

## Vulnerabilities Discovered

### 1. SSRF via wkhtmltopdf (Confirmed)
- `/download` endpoint accepts user-controlled URL
- **Protocols supported**:
  - ✅ `http://` - Works
  - ✅ `https://` - Works  
  - ✅ `file://` - Works (limited by permissions)
  - ✅ `gopher://` - Works!
  - ❌ `data://` - Doesn't execute JavaScript

- **Can read**:
  - `/app/` directory files (owned by node)
  - Internal HTTP services on localhost

- **Cannot read**:
  - `/root/flag.txt` - Permission denied
  - `/app/.env` - Permission denied
  - `/readflag` binary - Permission denied
  - `/proc/*/environ` - Permission denied

### 2. SQL Injection in GraphQL (Blocked)
- `getDataByName` query vulnerable: `SELECT * FROM users WHERE name like '%${args.name}%'`
- But `detectSqli()` regex blocks: `!#$%^&*()-_=+{}[]\|;:'",.<>/?`
- Cannot break out of LIKE clause without quotes
- **Not exploitable**

### 3. JWT Authentication
- Secret stored in `.env`: `IM_Sup3r_K3y_pl3ase_b3_c4r3ful?`
- But instance uses DIFFERENT secret (randomly generated?)
- Cannot forge admin tokens without correct secret
- **Blocked**

### 4. Admin Panel (Requires localhost + admin token)
- `/admin` - Accessible only from 127.0.0.1
- `/graphql` - Requires admin token AND localhost
- Admin page executes JavaScript to make GraphQL queries
- But wkhtmltopdf doesn't execute JavaScript properly
- **Cannot exploit**

---

## Attack Vectors Attempted

### ✅ SSRF to Internal Services
- Successfully accessed `http://127.0.0.1:1337/` via wkhtmltopdf
- Can make GET requests to localhost

### ❌ JavaScript Execution  
- Tried `data:text/html` URIs with JavaScript - Not executed
- Tried auto-submit forms - Not working
- wkhtmltopdf npm package doesn't enable JS by default

### ❌ File:// Protocol LFI
- Can read some `/app/` files
- Cannot read sensitive files (permissions)

### ✅ Gopher Protocol
- `gopher://127.0.0.1:3306/` works!
- Could potentially interact with MySQL
- Complex to craft valid MySQL protocol payloads

### ❌ JWT Secret Brute Force
- Tried common secrets - All failed
- Secret appears to be randomly generated per instance

### ❌ Command Injection
- URL parameters with `$()` pass validation
- But don't execute as commands

### ❌ SSTI through Errors
- Error messages rendered via EJS with `<%= error %>`
- HTML-escaped, no injection possible

---

## Likely Solution Path (Unconfirmed)

The challenge probably requires:

1. **Option A: JWT Secret Extraction**
   - Find a way to read the actual JWT secret from the running instance
   - `/proc/*/environ` is blocked but maybe there's another way
   - Or brute force with better wordlist

2. **Option B: MySQL Gopher Exploitation**
   - Craft proper gopher:// payload to interact with MySQL
   - Use `LOAD_FILE()` or `INTO OUTFILE` to read/write files
   - MySQL password is known: `D4T4b4s3Secr3tP4ssw0rd1ss0L0ngOmG!`

3. **Option C: wkhtmltopdf RCE**
   - Exploit a CVE in wkhtmltopdf 0.12.5
   - Chain with SSRF to achieve RCE

4. **Option D: Missing Endpoint**
   - There might be an undiscovered endpoint
   - Or a different attack vector not yet explored

---

## Files Read Successfully

- `/app/index.js`
- `/app/controllers/downloadController.js`
- `/app/controllers/authController.js`
- Other `/app/` JavaScript files

---

## Next Steps

1. Research wkhtmltopdf 0.12.5 CVEs
2. Learn MySQL gopher protocol exploitation
3. Try more JWT secrets from common lists
4. Fuzz for hidden endpoints
5. Check if there's a timing attack or race condition

---

## Commands Used

```bash
# Get guest token
curl http://target/getToken

# SSRF test
curl -X POST http://target/download?token=TOKEN \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1:1337/"}'

# File read  
curl -X POST http://target/download?token=TOKEN \
  -H "Content-Type: application/json" \
  -d '{"url":"file:///app/index.js"}'

# Gopher test
curl -X POST http://target/download?token=TOKEN \
  -H "Content-Type: application/json" \
  -d '{"url":"gopher://127.0.0.1:3306/"}'
```

---

**Status:** Requires further research or hint to proceed
