# Blueprint Heist - Challenge Directory

**HackTheBox CTF Try Out (Event 1434) - Web Exploitation Challenge**

## 🎯 Challenge Information

- **Name:** Blueprint Heist
- **Category:** Web Exploitation
- **Difficulty:** Easy
- **Points:** 1000
- **Status:** ✅ SOLVED
- **Flag:** `HTB{ch41ning_m4st3rs_b4y0nd_1m4g1nary_7f3e2b14969335049b602fd88507b1f5}`

---

## 📁 Directory Structure

```
blueprint_heist/
├── README.md                    # This file - directory index
├── WRITEUP.md                   # Complete detailed writeup (START HERE!)
├── CHALLENGE_SUMMARY.md         # Quick overview and stats
├── flag.txt                     # The captured flag
│
├── 📚 Documentation/
│   ├── CODE_ANALYSIS.md         # Full code analysis and vulnerabilities
│   ├── COMPLETE_SOLUTION.md     # Step-by-step solution guide
│   ├── STUDENT_GUIDE.md         # Beginner-friendly explanation
│   ├── QUICK_REFERENCE.md       # Commands and quick reference
│   ├── SOLUTION_DIAGRAM.txt     # Visual attack flow diagrams
│   ├── FINAL_INSTRUCTIONS.md    # Setup and execution guide
│   ├── NGROK_ISSUE.md           # Tunneling troubleshooting
│   └── ANALYSIS.md              # Initial reconnaissance notes
│
├── 🔧 Exploit Scripts/
│   ├── final_exploit.py         # Working Python exploit (MAIN EXPLOIT)
│   ├── exploit.sh               # Bash exploit wrapper
│   ├── run_exploit.sh           # Full automated exploit with setup
│   └── redirect.php             # HTTP redirect helper for SSRF
│
├── 🐳 Docker Environment/
│   ├── Dockerfile               # Container build file
│   ├── build-docker.sh          # Docker build script
│   └── entrypoint.sh            # Container entrypoint
│
├── 💻 Application Source/
│   ├── app/                     # Node.js application
│   │   ├── index.js             # Main application entry
│   │   ├── package.json         # Dependencies
│   │   ├── .env                 # Environment variables (JWT secret!)
│   │   ├── controllers/         # Request handlers
│   │   │   ├── authController.js       # JWT authentication
│   │   │   ├── downloadController.js   # PDF generation (VULNERABLE!)
│   │   │   └── errorController.js      # Error handling (VULNERABLE!)
│   │   ├── routes/              # API endpoints
│   │   │   ├── public.js        # Public routes
│   │   │   └── internal.js      # Admin routes
│   │   ├── schemas/             # GraphQL schemas
│   │   │   └── schema.js        # GraphQL queries (SQL INJECTION!)
│   │   ├── models/              # Data models
│   │   │   └── users.js         # User model
│   │   ├── utils/               # Utilities
│   │   │   ├── database.js      # MySQL connection
│   │   │   └── security.js      # Security functions (REGEX BYPASS!)
│   │   ├── views/               # EJS templates
│   │   │   ├── index.ejs        # Homepage
│   │   │   ├── admin.ejs        # Admin dashboard
│   │   │   ├── errors/          # Error templates
│   │   │   │   ├── 400.ejs      # Bad Request
│   │   │   │   ├── 401.ejs      # Unauthorized
│   │   │   │   ├── 403.ejs      # Forbidden
│   │   │   │   ├── 500.ejs      # Internal Server Error
│   │   │   │   └── error.ejs    # Generic error
│   │   │   │   # NOTE: 404.ejs is missing (EXPLOIT TARGET!)
│   │   │   └── reports/         # Report templates
│   │   ├── static/              # Static assets
│   │   │   ├── css/             # Stylesheets
│   │   │   ├── js/              # JavaScript
│   │   │   │   └── admin.js     # Admin page JS (GraphQL injection!)
│   │   │   └── images/          # Images
│   │   └── uploads/             # PDF output directory
│   │
│   ├── config/                  # Configuration files
│   │   ├── readflag.c           # SUID binary source (reads flag)
│   │   └── supervisord.conf     # Process supervisor config
│   │
│   └── database/                # Database setup
│       └── db.sql               # Initial database schema
│
└── 📊 Analysis Files/
    └── (See Documentation section above)
```

---

## 🚀 Quick Start

### 1. Read the Writeup
```bash
cat WRITEUP.md
# OR open in your editor:
code WRITEUP.md
```

### 2. Understand the Vulnerabilities
```bash
cat CODE_ANALYSIS.md
```

### 3. Run the Exploit
```bash
# Make sure you have Python 3 and dependencies
pip3 install jwt requests

# Run the exploit
python3 final_exploit.py

# Expected output: The flag!
```

---

## 🔗 Vulnerability Chain

```
┌──────────────────────────────────────────────────────────┐
│  1. SSRF via wkhtmltopdf                                 │
│     /download endpoint accepts user URLs                 │
│     wkhtmltopdf 0.12.5 fetches and converts to PDF      │
│     ↓                                                    │
│  2. HTTP Redirect to file:// (CVE-2020-21365)           │
│     redirect.php returns: Location: file:///app/.env    │
│     wkhtmltopdf follows redirect and reads local file   │
│     ↓                                                    │
│  3. JWT Secret Extraction                                │
│     .env contains: secret=Str0ng_K3y_N0_l3ak_pl3ase?    │
│     Can now forge admin JWT tokens                       │
│     ↓                                                    │
│  4. SQL Injection with Newline Bypass                    │
│     Regex /^.*[special_chars]/ doesn't match \n         │
│     Payload: "safe\n' UNION SELECT ..."                 │
│     ↓                                                    │
│  5. EJS Template Injection                               │
│     Write malicious template to 404.ejs via SQLi        │
│     Template: <%= execSync("/readflag") %>              │
│     ↓                                                    │
│  6. Command Execution                                     │
│     Access /nonexistent → 404 error                      │
│     Loads 404.ejs → Executes JavaScript                  │
│     Runs /readflag as root (SUID binary)                 │
│     ↓                                                    │
│  7. FLAG! 🎉                                             │
│     HTB{ch41ning_m4st3rs_b4y0nd_1m4g1nary_...}          │
└──────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Files to Examine

### Critical Vulnerabilities

1. **app/controllers/downloadController.js** - SSRF vulnerability
   ```javascript
   // Line 4-14: User-controlled URL passed to wkhtmltopdf
   const { url } = req.body;  // NO VALIDATION!
   wkhtmltopdf(url, { output: pdfPath });
   ```

2. **app/schemas/schema.js** - SQL Injection
   ```javascript
   // Line 37: String interpolation = SQLi
   query(`SELECT * FROM users WHERE name like '%${args.name}%'`)
   ```

3. **app/utils/security.js** - Regex Bypass
   ```javascript
   // Line 15: Vulnerable regex (. doesn't match \n)
   const pattern = /^.*[!#$%^&*()\-_=+{}\[\]\\|;:'\",.<>\/?]/
   ```

4. **app/controllers/errorController.js** - Template Injection
   ```javascript
   // Line 11-17: Dynamic template loading
   let templatePath = path.join(templateDir, `${errorCode}.ejs`);
   // 404.ejs doesn't exist - we can create it!
   ```

5. **app/.env** - Secrets Exposure
   ```env
   secret=Str0ng_K3y_N0_l3ak_pl3ase?  # JWT secret
   DB_PASSWORD=Secr3tP4ssw0rdNoGu35s!  # MySQL password
   ```

---

## 🛠️ Tools Required

- **Python 3** with libraries:
  - `jwt` - JWT token manipulation
  - `requests` - HTTP requests
  
- **Cloudflare Tunnel** or similar:
  - For hosting redirect.php publicly
  - Alternative: ngrok (paid), VPS, SSH tunnel
  
- **PHP** - For redirect server
  ```bash
  php -S 0.0.0.0:8000
  ```

- **pdftotext** (optional) - For PDF analysis
  ```bash
  apt install poppler-utils
  ```

---

## 📖 Documentation Guide

### For Complete Understanding:
1. **WRITEUP.md** (22KB) - Read this first for full walkthrough

### For Quick Reference:
2. **CHALLENGE_SUMMARY.md** (6KB) - Stats, tools, timeline
3. **QUICK_REFERENCE.md** (9KB) - Commands and payloads

### For Learning:
4. **STUDENT_GUIDE.md** (8KB) - Beginner-friendly with analogies
5. **CODE_ANALYSIS.md** (15KB) - Deep technical analysis

### For Execution:
6. **COMPLETE_SOLUTION.md** (8KB) - Step-by-step guide
7. **FINAL_INSTRUCTIONS.md** (5KB) - Setup instructions

### For Troubleshooting:
8. **NGROK_ISSUE.md** (3KB) - Tunneling problems and solutions
9. **SOLUTION_DIAGRAM.txt** (13KB) - Visual diagrams

---

## 💻 Exploit Scripts

### Main Exploit (Recommended)
```bash
python3 final_exploit.py
```
This is the working exploit based on the official HTB solution.

### Features:
- ✅ Gets guest token automatically
- ✅ Forges admin JWT token
- ✅ Crafts SQL injection payload with base64 encoding
- ✅ Executes via SSRF to localhost GraphQL
- ✅ Triggers template execution
- ✅ Returns the flag!

### Supporting Scripts:
- **exploit.sh** - Bash version (manual steps)
- **run_exploit.sh** - Full automation with Cloudflare setup
- **redirect.php** - HTTP→file:// redirect helper

---

## 🎓 Skills Demonstrated

This challenge teaches:

✅ **Web Application Security**
- SSRF exploitation
- Local File Inclusion
- SQL Injection bypass techniques
- Template injection
- JWT token forgery

✅ **Penetration Testing**
- Reconnaissance and enumeration
- Source code analysis
- Vulnerability chaining
- Exploit development

✅ **System Security**
- SUID binary exploitation
- Privilege escalation concepts
- Defense in depth understanding

---

## 🔐 Security Lessons

### Vulnerabilities Identified:

1. **SSRF** - User-controlled URLs without validation
2. **LFI** - wkhtmltopdf follows redirects to file://
3. **Regex Bypass** - Pattern doesn't account for newlines
4. **SQL Injection** - String interpolation instead of parameterized queries
5. **Template Injection** - Dynamic template paths with user control
6. **Secret Exposure** - Credentials in version-controlled .env

### Prevention Measures:

✅ Use `--disable-local-file-access` for wkhtmltopdf  
✅ Validate and sanitize ALL user input  
✅ Use parameterized queries (prepared statements)  
✅ Fix regex patterns (use multiline mode or allowlists)  
✅ Never trust user-controlled template paths  
✅ Rotate secrets regularly, use environment variables  
✅ Implement defense in depth  
✅ Keep software updated  

---

## 🏆 Achievement

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              🎉 BLUEPRINT HEIST SOLVED! 🎉                ║
║                                                            ║
║  Challenge: Blueprint Heist                                ║
║  Platform:  HackTheBox CTF Try Out (Event 1434)           ║
║  Category:  Web Exploitation                               ║
║  Difficulty: Easy                                          ║
║  Points:    1000                                           ║
║                                                            ║
║  Flag: HTB{ch41ning_m4st3rs_b4y0nd_1m4g1nary_...}         ║
║                                                            ║
║  Status: ✅ COMPLETED                                      ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

## 📞 Support

If you need help understanding any part of this challenge:

1. **Start with:** WRITEUP.md (complete walkthrough)
2. **For beginners:** STUDENT_GUIDE.md (simplified explanation)
3. **For reference:** QUICK_REFERENCE.md (commands)
4. **For code:** CODE_ANALYSIS.md (technical details)

---

## 📝 Notes

- All exploit scripts are ready to run
- Documentation is comprehensive and beginner-friendly
- Challenge files are organized for easy navigation
- Source code is fully annotated with vulnerabilities
- Multiple learning paths provided (beginner to advanced)

---

## ⚠️ Legal Disclaimer

This content is for **educational purposes only**. 

- ✅ Use on authorized CTF platforms (HackTheBox, etc.)
- ✅ Use in personal lab environments
- ✅ Use for learning and skill development
- ❌ Do NOT use on systems without explicit permission
- ❌ Do NOT use for malicious purposes

Always practice **ethical hacking** with proper authorization.

---

## 🙏 Credits

**Challenge Author:** lordrukie (HackTheBox)  
**Platform:** HackTheBox CTF Try Out (Event 1434)  
**Solver:** AI Security Analyst  
**Date Solved:** November 10, 2025  

---

## 📚 Additional Resources

- [Official HTB Repository](https://github.com/hackthebox/business-ctf-2024)
- [OWASP SSRF Guide](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery)
- [GraphQL Security](https://cheatsheetseries.owasp.org/cheatsheets/GraphQL_Cheat_Sheet.html)
- [SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

---

**Last Updated:** November 10, 2025  
**Version:** 1.0  
**Status:** Complete ✅

---

*Happy Hacking! 🚀*
