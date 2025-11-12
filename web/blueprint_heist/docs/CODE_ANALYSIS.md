# Blueprint Heist - Complete Code Analysis

## Overview
This is a Node.js web application designed as a CTF challenge with multiple security vulnerabilities. The goal is to read the flag located at `/root/flag.txt`.

---

## Architecture Components

### 1. Application Entry Point (`index.js`)
```javascript
const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.set("view engine", "ejs");
app.use('/static', express.static(path.join(__dirname, 'static')));

app.use(internalRoutes)  // Admin routes
app.use(publicRoutes)    // Public routes
```

**Purpose:** Main Express server that:
- Listens on port 1337
- Serves static files from `/static` directory
- Uses EJS for templating
- Handles JSON and URL-encoded requests
- Routes requests to public and internal (admin) endpoints

---

## 2. Authentication System

### JWT Authentication (`authController.js`)

#### Token Generation
```javascript
function generateGuestToken(req, res, next) {
    const payload = { role: 'user' };
    jwt.sign(payload, secret, (err, token) => {
        // Returns JWT token
    });
}
```
- **Endpoint:** `GET /getToken`
- **Creates:** Guest token with role 'user'
- **Secret:** Loaded from `.env` file (`process.env.secret`)
- **Vulnerability:** If you know the secret, you can forge admin tokens

#### Token Verification
```javascript
function verifyToken(token) {
    const decoded = jwt.verify(token, secret);
    return decoded.role;
}
```
- Validates JWT signature using the secret
- Returns the role from the token payload

#### Auth Middleware
```javascript
const authMiddleware = (requiredRole) => {
    return (req, res, next) => {
        const token = req.query.token;  // Token from URL query param
        
        if (!token) {
            return next(generateError(401, "Access denied"));
        }
        
        const role = verifyToken(token);
        
        if (requiredRole === "admin" && role !== "admin") {
            return next(generateError(401, "Unauthorized"));
        } else if (requiredRole === "admin" && role === "admin") {
            if (!checkInternal(req)) {
                return next(generateError(403, "Only available for internal users!"));
            }
        }
        
        next();
    };
};
```

**Key Security Check:** Admin endpoints require:
1. Valid JWT token with `role: "admin"`
2. Request must come from `127.0.0.1` (localhost)

---

## 3. Security Utilities (`utils/security.js`)

### Localhost Check
```javascript
function checkInternal(req) {
    const address = req.socket.remoteAddress.replace(/^.*:/, '')
    return address === "127.0.0.1"
}
```
- Extracts IP from socket connection
- Only allows `127.0.0.1` for admin access
- **Bypassed by:** SSRF attacks from localhost

### SQL Injection Filter
```javascript
function detectSqli(query) {
    const pattern = /^.*[!#$%^&*()\-_=+{}\[\]\\|;:'\",.<>\/?]/
    return pattern.test(query)
}
```
- Blocks common SQL injection characters
- **What's blocked:** `! # $ % ^ & * ( ) - _ = + { } [ ] \ | ; : ' " , . < > / ?`
- **What's allowed:** Letters, numbers, spaces, backticks (`), newlines, tabs
- **Weakness:** Very restrictive but might miss some edge cases

### URL Validation
```javascript
function isUrl(url) {
    try {
      new URL(url);
      return true;
    } catch (err) {
      return false;
    }
}
```
- Uses Node.js URL parser
- **Accepts:** `http://`, `https://`, `file://`, `gopher://`, etc.
- **Critical:** Allows non-HTTP protocols!

---

## 4. Routes

### Public Routes (`routes/public.js`)
```javascript
router.get("/", (req, res) => {
    res.render("index");  // Homepage
})

router.get("/report/progress", (req, res) => {
    res.render("reports/progress-report")
})

router.get("/report/enviromental-impact", (req, res) => {
    res.render("reports/enviromental-report")
})

router.get("/getToken", (req, res, next) => {
    generateGuestToken(req, res, next)  // Get guest JWT
});

router.post("/download", authMiddleware("guest"), (req, res, next) => {
    convertPdf(req, res, next)  // PDF generation - VULNERABLE!
})
```

**Available to anyone:**
- `/` - Homepage
- `/getToken` - Get guest JWT token
- `/download` - Convert URL to PDF (requires guest token)
- `/report/*` - View reports

### Internal Routes (`routes/internal.js`)
```javascript
router.get("/admin", authMiddleware("admin"), (req, res) => {
    res.render("admin")
})

router.all("/graphql", authMiddleware("admin"), (req, res, next) => {
    createHandler({ schema, context: { pool } })(req, res, next); 
});
```

**Requires admin token + localhost:**
- `/admin` - Admin dashboard
- `/graphql` - GraphQL API endpoint

---

## 5. The SSRF Vulnerability (`controllers/downloadController.js`)

### PDF Generation Function
```javascript
async function convertPdf(req, res, next) {
    const { url } = req.body;  // User-controlled URL!
    
    if (!isUrl(url)) {
        return next(generateError(400, "Invalid URL"));
    }
    
    const pdfPath = await generatePdf(url);
    res.sendFile(pdfPath, {root: "."});
}

async function generatePdfFromUrl(url, pdfPath) {
    return new Promise((resolve, reject) => {
        wkhtmltopdf(url, { output: pdfPath }, (err) => {
            // Converts URL content to PDF
        });
    });
}
```

**How It Works:**
1. User sends POST request to `/download` with `{"url": "..."}` in body
2. Application validates it's a valid URL format
3. **wkhtmltopdf** fetches the URL and converts to PDF
4. PDF is saved in `uploads/` directory
5. PDF is sent back to user

**The CRITICAL Vulnerability:**
- User controls the URL that wkhtmltopdf fetches
- wkhtmltopdf runs on the server and can access localhost
- Supports multiple protocols: `http://`, `https://`, `file://`, `gopher://`
- **NO restriction on accessing internal services!**

**What You Can Do:**
```javascript
// Access internal services
{"url": "http://127.0.0.1:1337/admin?token=ADMIN_TOKEN"}

// Read local files
{"url": "file:///etc/passwd"}
{"url": "file:///app/index.js"}

// Gopher protocol for raw TCP
{"url": "gopher://127.0.0.1:3306/..."}
```

---

## 6. GraphQL API (`schemas/schema.js`)

### Query: getAllData
```javascript
getAllData: {
    type: new GraphQLList(UserType),
    resolve: async(parent, args, { pool }) => {
        const connection = await pool.getConnection();
        data = await connection.query("SELECT * FROM users")
            .then(rows => rows[0]);
        return data;
    }
}
```
- **Safe:** No user input
- Returns all users from database

### Query: getDataByName (VULNERABLE!)
```javascript
getDataByName: {
    type: new GraphQLList(UserType),
    args: {
        name: { type: GraphQLString }
    },
    resolve: async(parent, args, { pool }) => {
        if (detectSqli(args.name)) {
            return generateError(400, "Username must only contain letters, numbers, and spaces.")
        }
        
        // VULNERABLE - String interpolation!
        data = await connection.query(
            `SELECT * FROM users WHERE name like '%${args.name}%'`
        ).then(rows => rows[0]);
        
        return data;
    }
}
```

**SQL Injection Vulnerability:**
- User input (`args.name`) is directly interpolated into SQL query
- Protected by `detectSqli()` filter
- **Still vulnerable to:**
  - Wildcards: `%` for matching anything
  - Special SQL keywords if they don't use blocked chars
  - Potentially blind SQL injection

**Example Query:**
```graphql
{
    getDataByName(name: "John") {
        name
        department
        isPresent
    }
}
```

---

## 7. Client-Side Admin Code (`static/js/admin.js`)

### The Injection Point
```javascript
document.getElementById('fetchUserForm').addEventListener('submit', function(event) {
    const username = document.getElementById('username').value;
    
    fetch(`/graphql?token=${token}`, {
        method: 'POST',
        body: JSON.stringify({
            query: `{
                getDataByName(name: "${username}") {
                    name
                    department
                    isPresent
                }
            }`
        })
    })
});
```

**GraphQL Injection Vulnerability:**
- User input (`username`) is directly embedded into GraphQL query string
- **Not escaped or sanitized!**
- If JavaScript executes, attacker can inject GraphQL

**Example Injection:**
```
Username: ") { name } } { __schema { types { name } } } #

Results in:
{
    getDataByName(name: "") { name } } { __schema { types { name } } } #") {
        name
        department
        isPresent
    }
}
```

**Problem:** wkhtmltopdf doesn't execute JavaScript by default, so this vulnerability is hard to exploit directly.

---

## 8. Database Configuration

### Connection (`utils/database.js`)
```javascript
const pool = mysql.createPool({
    host: process.env.DB_HOST,        // 127.0.0.1
    user: process.env.DB_USER,        // root
    password: process.env.DB_PASSWORD, // D4T4b4s3Secr3tP4ssw0rd1ss0L0ngOmG!
    database: process.env.DB_NAME,    // construction
    port: process.env.DB_PORT,        // 3306
    connectionLimit: 5
});
```

### Database Schema (`database/db.sql`)
```sql
CREATE TABLE construction.users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name TEXT,
    department TEXT,
    isPresent BOOLEAN
);

-- 30 sample users inserted

CREATE USER 'root'@'%' IDENTIFIED BY 'D4T4b4s3Secr3tP4ssw0rd1ss0L0ngOmG!'; 
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
```

**Key Points:**
- MySQL runs on localhost:3306
- Root user with password protection
- Only contains user employee data (no sensitive info in DB)

---

## 9. The Flag (`config/readflag.c`)

```c
#include<unistd.h>
#include<stdlib.h>
int main()
{
    setuid(0);
    system("cat /root/flag.txt");
}
```

**Compiled as:**
```bash
gcc -o /readflag /readflag.c
chmod 4755 /readflag  # SUID bit set!
```

**What This Means:**
- `/readflag` is an executable binary
- Owned by root with SUID bit (4755)
- **Anyone can execute it**
- When executed, it runs as root (setuid(0))
- Outputs the contents of `/root/flag.txt`

**Challenge:** How do you EXECUTE this binary through the web application?

---

## 10. Docker Environment (`Dockerfile`)

### Key Setup
```dockerfile
# wkhtmltopdf 0.12.5 installed
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/...

# Flag placed in root directory
COPY flag.txt /root/flag.txt

# readflag binary compiled with SUID
RUN gcc -o /readflag /readflag.c && chmod 4755 /readflag

# MySQL and Node.js run as 'node' user
```

**Security Context:**
- Web app runs as `node` user (not root)
- MySQL runs as `node` user
- Flag is at `/root/flag.txt` - only readable by root
- `/readflag` binary has SUID bit - executes as root when run

---

## Vulnerability Summary

### 1. **SSRF via wkhtmltopdf** (CRITICAL)
- **Location:** `/download` endpoint
- **What:** User-controlled URL passed to wkhtmltopdf
- **Impact:**
  - Access internal services (localhost)
  - Read local files via `file://` protocol
  - Use gopher:// to send raw TCP data to services like MySQL
- **Bypass:** Localhost restriction on admin endpoints

### 2. **SQL Injection in GraphQL**
- **Location:** `getDataByName` query
- **What:** String interpolation in SQL query
- **Protection:** `detectSqli()` filter
- **Impact:** Limited due to filtering, might allow blind SQLi

### 3. **GraphQL Injection (Client-Side)**
- **Location:** Admin page JavaScript
- **What:** Unsanitized user input in GraphQL query construction
- **Problem:** Hard to exploit because wkhtmltopdf doesn't execute JavaScript

### 4. **JWT Secret Exposure**
- **Location:** `.env` file
- **What:** JWT secret potentially accessible
- **Impact:** If you can read `.env`, you can forge admin tokens
- **Challenge:** The remote instance likely uses a different secret

---

## Attack Vectors

### Vector 1: SSRF → Admin Access
1. Get guest token from `/getToken`
2. Forge admin JWT token (if you know the secret)
3. Use SSRF to access `/admin?token=ADMIN_TOKEN` from localhost
4. Problem: wkhtmltopdf doesn't execute JavaScript

### Vector 2: SSRF → File Read
1. Use `file://` protocol to read sensitive files
2. Try to find JWT secret in memory/environment
3. Problem: Most sensitive files are permission-denied

### Vector 3: SSRF → MySQL via Gopher
1. Craft gopher:// payload to interact with MySQL
2. Use MySQL to execute commands or write files
3. Problem: MySQL requires password authentication
4. Challenge: Gopher payload construction is complex

### Vector 4: Direct Command Execution
1. Find a way to execute `/readflag` binary
2. Problem: No obvious command execution in the code
3. MySQL can't directly execute binaries (and runs as node, not root)

---

## Solution Path (Theoretical)

The intended solution likely involves:

1. **Use SSRF** to access internal services from localhost
2. **Craft MySQL Gopher Payload** with proper authentication
3. **Use MySQL** to write a file or create a condition that triggers `/readflag`
4. **Capture the output** somehow (maybe write to web-accessible location)

**OR**

1. **Extract the real JWT secret** from the running instance
2. **Forge admin token**
3. **Use SSRF** to access admin panel with forged token
4. **Exploit GraphQL** in some creative way to gain RCE

---

## Key Files Locations

- Flag: `/root/flag.txt`
- readflag binary: `/readflag`
- App directory: `/app/`
- Uploads: `/app/uploads/`
- Environment: `/app/.env`
- Static files: `/app/static/`

---

## Testing Commands

### Get Token
```bash
curl http://target:port/getToken
```

### SSRF Test
```bash
curl -X POST http://target:port/download?token=TOKEN \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1:1337/"}'
```

### Read File
```bash
curl -X POST http://target:port/download?token=TOKEN \
  -H "Content-Type: application/json" \
  -d '{"url":"file:///etc/passwd"}'
```

### GraphQL Query (Admin only)
```bash
curl -X POST http://target:port/graphql?token=ADMIN_TOKEN \
  -H "Content-Type: application/json" \
  -d '{"query":"{ getAllData { name department } }"}'
```

---

## Conclusion

This challenge tests your understanding of:
- SSRF exploitation
- JWT token security
- GraphQL vulnerabilities
- MySQL protocol manipulation (gopher)
- Privilege escalation via SUID binaries
- Creative exploitation chains

The core challenge is finding a way to **execute** the `/readflag` binary and capture its output, given that you have SSRF but limited RCE options.
