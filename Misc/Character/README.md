# Character - CTF Challenge

## 📋 Challenge Information

**Category:** Misc  
**Difficulty:** Easy  
**Target:** `83.136.255.235:56527`  
**Points:** TBD  

## 📝 Challenge Description

This challenge involves extracting a flag character by character from a remote service. The service provides characters at specific indices when queried, requiring you to build the flag incrementally by requesting each character position sequentially.

## 🎯 Solution Overview

The challenge requires connecting to a remote service and requesting characters one at a time by their index position. The solution:

1. Connects to the target server
2. Sends an index number
3. Receives the character at that position
4. Continues incrementing the index until the closing brace `}` is found
5. Assembles the complete flag

## 🚀 Quick Start

### Prerequisites

- Python 3.6+
- Network access to the target server

### Running the Solution

```bash
# Navigate to the challenge directory
cd Misc/Character

# Run the solve script
python3 solution/solve.py
```

### Expected Output

```
Prompt: [Connection established...]
Response: Character at Index 0: H
Index 0: 'H' -> Flag so far: H
Response: Character at Index 1: T
Index 1: 'T' -> Flag so far: HT
Response: Character at Index 2: B
Index 2: 'B' -> Flag so far: HTB
...
Index N: '}' -> Flag so far: HTB{...}

Complete flag: HTB{...}
```

## 📁 Folder Structure

```
Character/
├── README.md           # This file
├── solution/           # Solution scripts
│   └── solve.py       # Python exploit script
└── docs/              # Additional documentation (if needed)
```

## 🔧 Technical Details

### Attack Method
- **Type:** Index-based character extraction
- **Protocol:** TCP Socket connection
- **Method:** Sequential index queries

### Key Implementation Details

The solution script:
- Opens a socket connection for each character request
- Sends index numbers starting from 0
- Parses the response to extract the character
- Continues until the flag terminator `}` is found
- Handles connection errors gracefully

### Network Communication

```python
# Connect to service
conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect((host, port))

# Send index
conn.sendall(f"{index}\n".encode())

# Receive character
response = conn.recv(1024).decode()
```

## 🐛 Troubleshooting

### Connection Timeout
```bash
# Check if the server is reachable
nc -zv 83.136.255.235 56527

# Or use telnet
telnet 83.136.255.235 56527
```

### Python Dependencies
```bash
# No external dependencies required
# Only uses built-in socket module
python3 -c "import socket; print('✓ Socket module available')"
```

### Server Not Responding
- Verify the server is still online
- Check for firewall/network restrictions
- Ensure you're using the correct host and port

## 💡 Learning Points

1. **Socket Programming:** Understanding TCP socket connections in Python
2. **Protocol Interaction:** Learning to interact with custom network protocols
3. **Parsing:** Extracting data from structured text responses
4. **State Management:** Maintaining state across multiple connections
5. **Error Handling:** Gracefully handling network errors and timeouts

## ✅ Verification

Test your setup before running:

```bash
# Verify Python is available
python3 --version

# Test network connectivity
ping -c 1 83.136.255.235

# Test port connectivity
timeout 5 bash -c "</dev/tcp/83.136.255.235/56527" && echo "Port is open"
```

## 📖 Additional Resources

- [Python Socket Programming](https://docs.python.org/3/library/socket.html)
- [Network Protocol Analysis](https://en.wikipedia.org/wiki/Network_protocol)

## 🏆 Success Criteria

- Successfully extract all characters from index 0 to the closing brace
- Assemble the complete flag
- Flag format: `HTB{...}`

---

**Challenge Solved:** ✓  
**Solution Type:** Automated character extraction via socket protocol
