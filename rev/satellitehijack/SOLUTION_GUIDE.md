# Satellite Hijack - Solution Guide

## Challenge Overview
**Difficulty:** Hard  
**Points:** 975  
**Category:** Reverse Engineering

A binary that uses multi-layer obfuscation to hide flag validation logic.

---

## Solution Steps

### Step 1: Initial Analysis
```bash
file satellite
# satellite: ELF 64-bit LSB pie executable, x86-64, dynamically linked

file library.so  
# library.so: ELF 64-bit LSB shared object, x86-64, dynamically linked

# Check for anti-debugging or packing
strings satellite | grep -i upx  # No UPX packing
```

### Step 2: Identify Obfuscation Layers

#### Layer 1: Self-Modification (memfrob)
The binary uses `memfrob()` to XOR its own code section:
```bash
objdump -d library.so | grep memfrob
# Shows memfrob is called on library code
```

#### Layer 2: RC4 Encryption
After memfrob, the code is RC4-encrypted:
```bash
# Extract encrypted blob from library.so at offset 0x4020
dd if=library.so of=encrypted_blob.bin bs=1 skip=$((0x4020)) count=444
```

#### Layer 3: Dynamic Code Loading
The decrypted code is loaded into executable memory via `mmap()` with `PROT_EXEC`.

### Step 3: Extract and Decrypt the Code

Run the extraction script:
```python
python3 solver.py
```

Or manually:
```python
import struct

# RC4 decryption key (from analysis)
key = bytes.fromhex('...')  # See solver.py for full key

# After decryption, the code validates the flag using XOR
```

### Step 4: Analyze the Decrypted Code

The validation function at offset 0x8c in the decrypted code:
1. Loads a 28-byte key onto the stack (with overlapping memory writes)
2. For each character i (0 to 27):
   - Computes: `input[i] XOR key[i]`
   - Checks if result equals `i`
3. Returns success if all 28 characters pass

**Key Extraction:**
```asm
; Key is built with 4 movabs instructions with overlapping stack positions
movabs $0x37593076307b356c,%rax  ; 8 bytes at -0x28(%rsp)
movabs $0x3a7c3e753f665666,%rdx  ; 8 bytes at -0x20(%rsp)
movabs $0x784c7c214f3a7c3e,%rax  ; 8 bytes at -0x1b(%rsp) [overlaps!]
movabs $0x663b2c6a246f21,%rdx    ; 7 bytes at -0x13(%rsp) [overlaps!]
```

The overlapping writes are intentional and create the final key.

### Step 5: Calculate the Flag

Since the check is: `input[i] XOR key[i] == i`  
We can derive: `input[i] = key[i] XOR i`

```python
import struct

# Build key with overlaps
key_buffer = bytearray(32)
key_buffer[0:8] = struct.pack('<Q', 0x37593076307b356c)
key_buffer[8:16] = struct.pack('<Q', 0x3a7c3e753f665666)
key_buffer[13:21] = struct.pack('<Q', 0x784c7c214f3a7c3e)  # Overwrites bytes 13-20
key_buffer[21:28] = struct.pack('<Q', 0x663b2c6a246f21)[:-1]  # 7 bytes

# Calculate flag
flag = "HTB{" + ''.join(chr(key_buffer[i] ^ i) for i in range(28)) + "}"
print(flag)
```

---

## Final Flag
```
HTB{l4y3r5_0n_l4y3r5_0n_l4y3r5!}}
```

The flag itself hints at the solution: "layers on layers on layers!" - referring to the multiple layers of obfuscation.

---

## Key Learnings

1. **Multi-layer Obfuscation**: Combining self-modification, encryption, and dynamic code loading
2. **Memory Overlaps**: Intentional overlapping memory writes to obfuscate data
3. **XOR with Index**: A simple but effective flag validation technique
4. **Dynamic Analysis**: Setting the environment variable `SAT_PROD_ENVIRONRONMENT=1` triggers the backdoor logic

---

## Tools Used
- `objdump` - Disassembly
- `gdb` - Dynamic analysis
- `python3` - Decryption and flag calculation
- `ghidra` / `radare2` - Advanced RE (optional)

---

## Environment Variable
The challenge requires setting:
```bash
export SAT_PROD_ENVIRONRONMENT=1
```
Note the typo: "ENVIRONRONMENT" (three R's) - this is intentional!
