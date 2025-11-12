# Prison Pipeline - CTF Challenge

## 📋 Challenge Information

**Category:** Misc / Web  
**Difficulty:** Medium-Hard  
**Ports:** 5000 (Application), 8080 (Prisoner DB)  
**Challenge Type:** YAML Deserialization + Command Injection  

## 📝 Challenge Description

Prison Pipeline is a complex web application consisting of two services:

1. **Application Service** (Port 5000) - Main web interface for managing prisoners
2. **Prisoner-DB Service** (Port 8080) - Database service with REST API

The challenge involves exploiting YAML deserialization vulnerabilities and potential command injection through the prisoner database system.

## 🎯 Solution Overview

This multi-service challenge presents several attack vectors:

### Architecture

```
User → Application (Port 5000)
         ↓ HTTP
      Prisoner-DB (Port 8080) → YAML Files
         ↓ curl wrapper
      Command Execution
```

### Potential Vulnerabilities

1. **YAML Deserialization** (`js-yaml`)
   - The prisoner-DB loads YAML files with `yaml.load()`
   - May be vulnerable to prototype pollution or code injection
   - YAML files contain prisoner profile data

2. **Command Injection via Curl Wrapper**
   - Custom CurlWrapper class in `curl.js`
   - May allow injection through HTTP parameters
   - Could lead to RCE if parameters aren't sanitized

3. **File Upload/Manipulation**
   - Application may allow creating/modifying prisoner entries
   - Could inject malicious YAML payloads
   - Potential path traversal

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.6+ (for exploit scripts)
- Node.js (for local testing)
- Network access to target

### Building Locally

```bash
# Navigate to challenge directory
cd Misc/prison_pipeline

# Build and run with Docker Compose
./build-docker.sh

# Or manually:
docker build -t misc_prison_pipeline .
docker run --rm -it -p 5000:5000 -p 8080:8080 misc_prison_pipeline
```

### Running the Solution

```bash
# Navigate to solution directory
cd solution/

# Install dependencies
pip3 install -r requirements.txt

# Run the exploit
python3 solve.py <target_host>

# Example:
python3 solve.py localhost
```

## 📁 Folder Structure

```
prison_pipeline/
├── README.md                      # This file
├── build-docker.sh               # Docker build script
├── Dockerfile                    # Container configuration
├── challenge/                    # Application source
│   ├── application/             # Main web application
│   │   ├── index.js            # Express app entry
│   │   ├── routes/             # API endpoints
│   │   ├── views/              # Templates
│   │   ├── static/             # Frontend assets
│   │   ├── prod.config.js      # Production config
│   │   └── dev.config.js       # Development config
│   └── prisoner-db/            # Database service
│       ├── index.js           # Database class
│       ├── curl.js            # HTTP wrapper (vulnerable?)
│       ├── package.json       
│       └── README.md
├── data/                        # Challenge data
│   └── flag.txt                # Test flag
├── docs/                        # Additional documentation
└── solution/                    # Solution scripts
    ├── solve.py                # Main exploit script
    ├── payloads/               # YAML payloads
    └── requirements.txt
```

## 🔧 Technical Details

### Application Stack

**Frontend:**
- Express.js
- Nunjucks templating
- Bootstrap UI
- jQuery

**Backend:**
- Node.js
- YAML processing (js-yaml)
- Custom curl wrapper
- File-based database

### Key Files Analysis

#### 1. prisoner-db/index.js - Database Class

```javascript
getPrisoner(id) {
    let prisoner = {id: null, raw: '', data: {}};
    if (this.metadata.prisoner_ids.includes(id)) {
        prisoner = {
            id: id,
            raw: this.readYAML(this.repository + '/' + id + '.yaml')
        };
        let details = yaml.load(prisoner.raw).prisoner_profile;
        prisoner.data = details;
    }
    return prisoner;
}
```

**Vulnerability:** `yaml.load()` without safe mode can deserialize arbitrary objects.

#### 2. prisoner-db/curl.js - HTTP Wrapper

Custom wrapper for making HTTP requests. Check for:
- Command injection in curl parameters
- Unsafe shell command construction
- Unvalidated user input

#### 3. application/routes/index.js - API Endpoints

Routes that handle prisoner data:
- Create prisoner
- Update prisoner
- Delete prisoner
- List prisoners

### YAML Deserialization Exploit

**Prototype Pollution Payload:**
```yaml
prisoner_profile:
  __proto__:
    isAdmin: true
    polluted: "yes"
  name: "Test"
  id: "12345"
```

**Code Execution (if vulnerable):**
```yaml
prisoner_profile: !!js/function >
  function() {
    require('child_process').exec('cat /flag.txt > /tmp/flag')
  }
```

### Exploitation Strategy

**Phase 1: Reconnaissance**
1. Enumerate prisoners via API
2. Analyze YAML structure
3. Identify writable endpoints

**Phase 2: Payload Crafting**
1. Create malicious YAML payload
2. Test for YAML deserialization
3. Escalate to command execution

**Phase 3: Exploitation**
1. Upload/inject payload
2. Trigger deserialization
3. Execute commands
4. Extract flag

## 🐛 Troubleshooting

### Multi-Service Issues

```bash
# Check both services are running
netstat -tlnp | grep -E '5000|8080'

# Test application
curl http://localhost:5000

# Test prisoner-db
curl http://localhost:8080
```

### Docker Networking

```bash
# View Docker networks
docker network ls

# Inspect container
docker inspect misc_prison_pipeline
```

### YAML Parsing Errors

If YAML payloads fail:
- Validate YAML syntax
- Check for special characters
- Test with simple payload first
- Review js-yaml version for known CVEs

## 💡 Learning Points

1. **YAML Deserialization:** Understanding unsafe YAML.load() risks
2. **Prototype Pollution:** Exploiting JavaScript object inheritance
3. **Service Communication:** Attacking multi-service architectures
4. **API Security:** Securing REST APIs and data validation
5. **Defense in Depth:** Why multiple security layers matter

## 🛡️ Mitigation

To secure this application:

```javascript
// 1. Use safe YAML loading
const yaml = require('js-yaml');
const doc = yaml.load(input, { schema: yaml.JSON_SCHEMA });

// 2. Validate input before processing
function validatePrisonerData(data) {
    // Whitelist allowed fields
    // Check data types
    // Sanitize all inputs
}

// 3. Use Object.freeze() to prevent prototype pollution
Object.freeze(Object.prototype);

// 4. Implement proper authentication and authorization
// 5. Use parameterized queries/safe APIs
// 6. Apply principle of least privilege
```

## 📖 Additional Resources

- [YAML Deserialization Attacks](https://book.hacktricks.xyz/pentesting-web/deserialization/nodejs-proto-prototype-pollution)
- [Prototype Pollution](https://portswigger.net/web-security/prototype-pollution)
- [js-yaml Security](https://github.com/nodeca/js-yaml/wiki/Security-vulnerabilities-and-security-related-bugs)

## ✅ Success Criteria

- Analyze the multi-service architecture
- Identify YAML deserialization vulnerability
- Craft appropriate exploit payload
- Achieve command execution
- Extract the flag
- Flag format: `HTB{...}`

## 🏆 Expected Output

```
[*] Prison Pipeline CTF Challenge - Exploit
[*] Target: http://target:5000
[*] Step 1: Enumerating prisoners...
[+] Found 3 prisoners
[*] Step 2: Crafting YAML payload...
[+] Payload ready
[*] Step 3: Injecting payload...
[+] Payload uploaded
[*] Step 4: Triggering deserialization...
[+] Command executed
[*] Step 5: Extracting flag...
[+] Flag: HTB{...}
```

---

**Challenge Type:** Web + YAML Deserialization + Multi-Service  
**Key Vulnerability:** Unsafe YAML.load() with prototype pollution  
**Difficulty:** Medium-Hard (requires understanding of YAML security and JS internals)  
**Architecture:** Microservices with internal API communication
