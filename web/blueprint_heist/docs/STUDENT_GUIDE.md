# Blueprint Heist - Simple Explanation for Students

## What is this challenge?

Imagine you're trying to break into a building (the web server) to steal a secret document (the flag). The building has several rooms (endpoints) and security systems (authentication), but there's a way to trick the security and get inside.

---

## The Application - Like a Building with Rooms

### **Main Entrance (Public Areas)**
Anyone can access these:
- **Lobby (/)**: The homepage, nothing special
- **Security Desk (/getToken)**: Get a visitor badge (JWT token with "user" role)
- **Copy Room (/download)**: A machine that converts web pages to PDF - **THIS IS YOUR WAY IN!**
- **Public Reports (/report/*)**: Some public documents

### **Restricted Area (Admin Only)**
You need special clearance:
- **Executive Office (/admin)**: Admin dashboard
- **Database Room (/graphql)**: Direct access to company database
- **Requirements**: 
  1. Admin badge (JWT token with "admin" role)
  2. Must be physically inside the building (request from 127.0.0.1)

### **The Vault**
- **Top Secret File**: `/root/flag.txt` (the flag)
- **Master Key**: `/readflag` (a special program that can open the vault)

---

## The Security System - How Authentication Works

### **Visitor Badge (JWT Token)**
Think of this like an ID card:

```
┌─────────────────────────┐
│    VISITOR BADGE        │
│                         │
│  Name: Guest            │
│  Role: user             │
│  Signature: [encrypted] │
└─────────────────────────┘
```

- The signature is created using a **secret password**
- Only if you know the secret can you create fake badges
- The building has TWO types of badges: "user" and "admin"

### **The Security Check**
When you try to enter the admin area:
```javascript
1. Do you have a badge? (token exists?)
2. Is your badge real? (valid JWT signature?)
3. Is your badge level "admin"? (role === "admin")
4. Are you physically in the building? (request from 127.0.0.1?)
```

---

## The Vulnerability - The Copy Machine Exploit

### **What is SSRF?**
**S**erver-**S**ide **R**equest **F**orgery

The copy machine (/download endpoint) can fetch ANY web page and convert it to PDF:

```
You → Web Server → Copy Machine → Fetches URL → Creates PDF → Returns to you
```

**The Problem**: You control what URL the copy machine fetches!

### **Normal Use:**
```javascript
POST /download?token=USER_TOKEN
{
  "url": "https://google.com"
}
```
Result: PDF of Google homepage

### **Malicious Use:**
```javascript
POST /download?token=USER_TOKEN
{
  "url": "http://127.0.0.1:1337/admin?token=ADMIN_TOKEN"
}
```
Result: The copy machine (from inside the building) accesses the admin page for you!

---

## Why This Is Dangerous

### 1. **Accessing Internal Services**
The copy machine is INSIDE the building, so it can access restricted areas:

```
External Attacker (You) 
    ↓
    Makes request to /download
    ↓
Web Server (Inside building)
    ↓
    Copy Machine accesses http://127.0.0.1:1337/admin
    ↓
    Bypasses "must be from localhost" check!
```

### 2. **Reading Secret Files**
The copy machine can read files on the server:

```javascript
{
  "url": "file:///etc/passwd"  // Linux password file
}
```

### 3. **Attacking Other Services**
Using special protocols like `gopher://`, you can send commands to other services:

```javascript
{
  "url": "gopher://127.0.0.1:3306/..."  // Send commands to MySQL database
}
```

---

## The Challenge - Why It's Hard

### **What You Need:**
1. Execute the `/readflag` program
2. Capture its output (the flag)
3. The program needs to RUN, not just be read

### **The Problems:**

#### Problem 1: Can't Execute Directly
- The web app doesn't have any endpoint that runs system commands
- MySQL database can't execute programs as root
- wkhtmltopdf can only READ files, not EXECUTE them

#### Problem 2: Can't Read the Flag Directly
```bash
ls -l /root/flag.txt
-rw-r----- 1 root root 38 Nov 10 /root/flag.txt
         ↑
         Only root can read this!
```

#### Problem 3: Need Admin Access
- To do anything interesting with GraphQL, you need admin token
- Admin token requires knowledge of the secret
- The remote server uses a DIFFERENT secret than the one in the files

#### Problem 4: JavaScript Doesn't Run
- The admin page has JavaScript that might be exploitable
- BUT wkhtmltopdf doesn't execute JavaScript
- So you can't trigger the vulnerable code

---

## Potential Solution Paths

### Path 1: MySQL Gopher Attack (Most Likely)
```
1. Craft a special gopher:// URL that talks to MySQL
2. Authenticate with MySQL using the known password
3. Use MySQL to write a file somewhere accessible
4. Maybe trigger execution of /readflag somehow
5. Read the output
```

**Why Hard:** MySQL protocol is binary and complex, requires deep understanding

### Path 2: Find JWT Secret
```
1. Find a way to read the real JWT secret from memory/environment
2. Forge an admin token
3. Use SSRF to access admin endpoints with forged token
4. Exploit something in GraphQL to gain command execution
```

**Why Hard:** Can't read protected files like .env

### Path 3: Undiscovered Vulnerability
```
Maybe there's another endpoint or vulnerability not found yet?
```

---

## Key Concepts for Students

### 1. **SSRF (Server-Side Request Forgery)**
When a server makes requests on behalf of users, and the URL is user-controlled:
- Can access internal services
- Can read local files  
- Can bypass IP-based restrictions

### 2. **JWT (JSON Web Tokens)**
A way to prove who you are:
- Contains claims (like role: "admin")
- Signed with a secret key
- If you know the secret, you can forge tokens

### 3. **SQL Injection**
Putting malicious SQL code into input fields:
```sql
-- Safe query:
SELECT * FROM users WHERE name = 'John'

-- Injected:
SELECT * FROM users WHERE name = 'John'; DROP TABLE users; --'
```

### 4. **GraphQL**
A query language for APIs (alternative to REST):
```graphql
{
  getDataByName(name: "John") {
    name
    department
  }
}
```

### 5. **SUID Binaries**
Programs that run with owner's permissions:
- `/readflag` is owned by root
- Has SUID bit set (4755)
- When anyone runs it, it executes as root
- This is why we need to EXECUTE it, not just read it

---

## Testing It Yourself

### Step 1: Get a Token
```bash
curl http://target:port/getToken
```

### Step 2: Test SSRF
```bash
curl -X POST http://target:port/download?token=YOUR_TOKEN \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1:1337/"}'
```

### Step 3: Read a File
```bash
curl -X POST http://target:port/download?token=YOUR_TOKEN \
  -H "Content-Type: application/json" \
  -d '{"url":"file:///etc/passwd"}' \
  --output result.pdf
```

Then open `result.pdf` to see the file contents!

---

## What You Learned

1. **Input Validation Matters**: The `/download` endpoint doesn't properly validate URLs
2. **Defense in Depth**: Multiple security layers are needed (not just one check)
3. **Localhost != Secure**: Services on localhost can still be attacked via SSRF
4. **Principle of Least Privilege**: Services should run with minimal permissions
5. **Secrets Must Be Secret**: Hardcoded secrets in config files are dangerous

---

## Real-World Impact

This type of vulnerability has been found in:
- Cloud metadata services (AWS, Azure, GCP)
- Internal admin panels
- Payment processing systems
- Corporate intranets

**Famous Example**: Capital One Breach (2019)
- Attacker used SSRF to access AWS metadata
- Stole data of 100 million customers
- Cost: $80 million fine

---

## Questions to Think About

1. How could the `/download` endpoint be made safer?
2. Why is it dangerous to allow `file://` and `gopher://` protocols?
3. What if the JWT secret was longer and random - would that solve everything?
4. How can you protect MySQL from gopher protocol attacks?
5. Is it safe to run wkhtmltopdf on user-supplied URLs?

**Bonus Question**: What's the difference between SSRF and XSS?

---

## Resources to Learn More

- OWASP SSRF Guide: https://owasp.org/www-community/attacks/Server_Side_Request_Forgery
- PortSwigger SSRF Tutorial: https://portswigger.net/web-security/ssrf
- HackTheBox Academy: Web Exploitation modules
- Try similar challenges on: HackTheBox, TryHackMe, PentesterLab
