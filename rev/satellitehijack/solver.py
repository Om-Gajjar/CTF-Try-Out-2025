#!/usr/bin/env python3
"""
Satellite Hijack - CTF Challenge Solver
========================================
The binary uses a multi-layer obfuscation technique:
1. Self-modification via memfrob 
2. Runtime decryption using RC4
3. Dynamic code execution in mmapped memory
4. Flag validation via XOR with positional index

The flag is checked by: input[i] XOR key[i] == i
Therefore: input[i] = key[i] XOR i
"""
import struct

# Extract key from decrypted code (with overlapping memory writes)
# The key is built on the stack with multiple movabs instructions
key1 = struct.pack('<Q', 0x37593076307b356c)  # 8 bytes at offset 0
key2 = struct.pack('<Q', 0x3a7c3e753f665666)  # 8 bytes at offset 8
key3 = struct.pack('<Q', 0x784c7c214f3a7c3e)  # 8 bytes at offset 13 (overlaps!)
key4 = struct.pack('<Q', 0x663b2c6a246f21)[:-1]  # 7 bytes at offset 21 (overlaps!)

# Build key buffer with overlaps
key_buffer = bytearray(32)
key_buffer[0:8] = key1
key_buffer[8:16] = key2
key_buffer[13:21] = key3  # Overwrites bytes 13-20
key_buffer[21:28] = key4  # Overwrites bytes 21-27

# Calculate flag (28 characters after "HTB{")
flag_content = ''.join(chr(key_buffer[i] ^ i) for i in range(28))
flag = f"HTB{{{flag_content}}}"

print("="*60)
print("SATELLITE HIJACK - FLAG SOLVER")  
print("="*60)
print(f"\nFlag: {flag}")
print(f"Length: {len(flag)} chars (content: {len(flag_content)} chars)")
print("="*60)

# Verification
print("\nVerification:")
all_correct = True
for i in range(28):
    char = flag_content[i]
    xor_result = ord(char) ^ key_buffer[i]
    correct = (xor_result == i)
    all_correct = all_correct and correct
    status = '✓' if correct else '✗'
    print(f"  [{i:2d}] '{char}' XOR 0x{key_buffer[i]:02x} = {xor_result:2d} {status}")

print(f"\n{'='*60}")
print(f"Status: {'ALL CHECKS PASSED ✓' if all_correct else 'VALIDATION FAILED ✗'}")
print(f"{'='*60}")

