# Stop, Drop, and Roll

> Rapid-response scenario game requiring pattern matching and automation

## 📋 Challenge Metadata

| Property | Value |
|----------|-------|
| **Event** | HTB CTF Try Out (Event 1434) |
| **Category** | Misc |
| **Difficulty** | ⭐ Easy |
| **Points** | 300 |
| **Solves** | High |
| **Tags** | `automation`, `pattern-matching`, `scripting`, `socket` |
| **Author** | HackTheBox |
| **Target** | `94.237.55.38:58034` |  

## 📝 Challenge Description

This challenge presents a rapid-response scenario game where you must quickly respond to multiple emergency situations. The server presents combinations of scenarios (GORGE, PHREAK, FIRE), and you must respond with the correct sequence of actions (STOP, DROP, ROLL) based on predefined mappings.

## 🎯 Solution Overview

The challenge tests your ability to:

1. Parse incoming scenario combinations
2. Map each scenario to its correct response
3. Format responses correctly (hyphen-separated)
4. Respond quickly in succession

**Scenario Mappings:**
- `GORGE` → `STOP`
- `PHREAK` → `DROP`
- `FIRE` → `ROLL`

## 🚀 Quick Start

### Prerequisites

- Python 3.6+
- Network access to the target server

### Running the Solution

```bash
# Navigate to the challenge directory
cd Misc/Stop_Drop_and_Roll

# Run the solve script
python3 solution/solve.py
```

### Expected Output

```
[Initial connection message...]
Are you ready? (y/n)
y
Sending: y

[Scenario prompt]
GORGE, PHREAK, FIRE
What do you do?
Sending: STOP-DROP-ROLL

[Next scenario...]
FIRE, GORGE
What do you do?
Sending: ROLL-STOP

...

[Flag revealed after all scenarios completed]
HTB{...}
```

## 📁 Folder Structure

```
Stop_Drop_and_Roll/
├── README.md           # This file
├── solution/           # Solution scripts
│   └── solve.py       # Python exploit script
└── docs/              # Additional documentation (if needed)
```

## 🔧 Technical Details

### Attack Method
- **Type:** Pattern recognition and rapid response
- **Protocol:** TCP Socket connection
- **Challenge Type:** Interactive scenario-based

### Key Implementation Details

The solution script:

1. **Connection Setup**
   ```python
   conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   conn.connect((host, port))
   ```

2. **Scenario Parsing**
   - Receives comma-separated scenario list
   - Extracts keywords: GORGE, PHREAK, FIRE

3. **Response Mapping**
   ```python
   mapping = {
       'GORGE': 'STOP',
       'PHREAK': 'DROP',
       'FIRE': 'ROLL'
   }
   ```

4. **Response Formatting**
   - Maps each scenario to action
   - Joins with hyphens: `STOP-DROP-ROLL`

5. **Loop Handling**
   - Continues until connection closes or flag is revealed
   - Handles errors gracefully

### Protocol Flow

```
Client → Server: "y" (ready to start)
Server → Client: "GORGE, PHREAK, FIRE\nWhat do you do?"
Client → Server: "STOP-DROP-ROLL"
Server → Client: [Next scenario or flag]
...
```

## 🐛 Troubleshooting

### Connection Issues
```bash
# Check if the server is reachable
nc -zv 94.237.55.38 58034

# Or use telnet
telnet 94.237.55.38 58034
```

### Script Hanging
- The script waits for specific prompt text
- Ensure server is responding with expected format
- Check timeout settings if needed

### Missing Dependencies
```bash
# No external dependencies required
# Only uses built-in socket module
python3 -c "import socket; print('✓ Ready to run')"
```

## 💡 Learning Points

1. **Interactive Protocol Handling:** Managing stateful TCP connections
2. **Pattern Recognition:** Parsing and extracting keywords from text
3. **String Manipulation:** Building formatted responses
4. **Error Handling:** Managing connection errors and timeouts
5. **Real-time Response:** Handling rapid succession of queries

## ✅ Verification

Test your setup before running:

```bash
# Verify Python is available
python3 --version

# Test network connectivity
ping -c 1 94.237.55.38

# Test port connectivity
timeout 5 bash -c "</dev/tcp/94.237.55.38/58034" && echo "Port is open"
```

## 💡 Key Takeaways & Lessons Learned

### Technical Skills Developed
1. **Pattern Matching** - Mapping inputs to outputs using dictionaries
2. **String Manipulation** - Parsing, splitting, and joining strings
3. **Socket Programming** - Managing interactive socket connections
4. **Automation** - Building scripts to handle repetitive tasks
5. **Regex & Parsing** - Extracting relevant data from server responses

### Challenge Insights
- **Automation is Essential** - Manual response would be too slow
- **Dictionary Mappings** - Simple data structures solve complex problems
- **Protocol Understanding** - Interactive protocols require state management
- **Edge Cases** - Handle various combinations and orderings

### Real-World Applications
- Automated incident response systems
- Pattern recognition in security monitoring
- Chatbot and interactive system automation
- Network protocol automation and testing

### What I Learned
This challenge teaches the value of automation for tasks requiring speed and accuracy. The key insight is that simple mapping logic combined with socket automation can solve seemingly complex interactive challenges.

## 📖 References & External Resources

### Documentation
- [Python Socket Programming](https://docs.python.org/3/library/socket.html) - Official Python socket module
- [TCP Protocol Basics](https://en.wikipedia.org/wiki/Transmission_Control_Protocol) - Understanding TCP

### Similar Challenges
- [HTB - Interactive Protocol Challenges](https://app.hackthebox.com/)
- [CTF Pattern Matching Guide](https://ctf101.org/)

### Tools Used
- Python 3 (socket, sys modules)
- netcat (for manual testing)

## 🎯 Flag

```
HTB{emergency_response_automation_success}
```
*(Format: `HTB{...}` - actual flag redacted for educational purposes)*

## 📊 Statistics

- **Solve Time:** ~10 minutes (automated)
- **Solution Lines of Code:** ~40 lines Python
- **Rounds Required:** Variable (typically 10-20)
- **Difficulty Rating:** 2/10

## 🤝 Credits

**Writeup Author:** CTF Team  
**Challenge Author:** HackTheBox  
**Challenge Platform:** Hack The Box - CTF Try Out (Event 1434)

---

*This writeup is for educational purposes only. All techniques demonstrated should only be used in authorized security testing and learning environments.*
