# Void - PWN Challenge

**Status:** ✅ SOLVED  
**Difficulty:** Medium (1000 points)  
**Flag:** `HTB{pwnt00l5_h0mep4g3_15_u54ful}`

## Quick Start

```bash
# Run the exploit
python3 exploit_final.py
```

## Challenge Summary

This is an advanced buffer overflow challenge with a unique constraint: **no leak primitive**. The binary only imports `read()`, making traditional ret2libc attacks impossible without knowing libc addresses.

### The Vulnerability
- **Buffer:** 64 bytes allocated
- **Read:** 200 bytes accepted (0xc8)
- **Overflow:** 136 bytes beyond buffer
- **Protections:** No canary, NX enabled, No PIE, Partial RELRO

### The Challenge
- ❌ No `write()`, `puts()`, or `printf()` to leak addresses
- ❌ ASLR enabled on remote server
- ❌ Brute-force impractical (4096 attempts × slow connections)

### The Solution: Ret2dlresolve
Instead of leaking addresses, we exploit the **dynamic linker** itself:
1. Create fake dynamic linker structures
2. Trick `_dl_runtime_resolve()` into resolving `system`
3. Call `system("/bin/sh")` without knowing libc addresses

## Files

- `void` - The vulnerable binary
- `exploit_final.py` - Working exploit using ret2dlresolve
- `SOLUTION_GUIDE.md` - Complete walkthrough (16KB)
- `glibc/` - Provided libc files

## Key Concepts Learned

1. **Ret2dlresolve** - Advanced exploitation without leaks
2. **Dynamic Linking** - How `_dl_runtime_resolve()` works
3. **ELF Structures** - Symbol tables, relocation entries
4. **Multi-stage Exploits** - ROP + data injection
5. **Pwntools Advanced** - `Ret2dlresolvePayload` class

## How It Works

```
┌─────────────────────┐
│ 1. Buffer Overflow  │  Overwrite return address
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ 2. ROP Chain        │  Call read() to input fake structures
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ 3. Fake Structures  │  Elf64_Sym, Elf64_Rela, String table
│     in .bss         │  Tell linker about "system"
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ 4. _dl_runtime      │  Linker resolves "system"
│     _resolve()      │  Calls system("/bin/sh")
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ 5. Shell!           │  cat flag.txt
└─────────────────────┘
```

## Exploit Breakdown

### Memory Layout
```
Stack:
[64 bytes buffer] [8 bytes RBP] [Return Address] ← Offset 72
                                      ↓
                                  ROP chain

.bss Section:
[Fake Elf64_Sym] [String: "system\x00/bin/sh\x00"] [Fake Elf64_Rela]
```

### ROP Chain
```python
# Stage 1: Read fake structures into .bss
read(0, dlresolve.data_addr, size)

# Stage 2: Trigger dynamic linker
_dl_runtime_resolve(FAKE_INDEX) → resolves to system("/bin/sh")
```

## Why "Void"?

The challenge name has multiple meanings:
- `void vuln()` - The function type
- A "void" where leak functions should be
- Exploiting the "void" of the `.bss` section
- Filling the "void" with fake structures

## Techniques Comparison

| Technique | Requires Leak? | Complexity | This Challenge |
|-----------|---------------|------------|----------------|
| ret2libc | ✅ Yes | Easy | ❌ No leak available |
| ASLR Brute-force | ❌ No | Medium | ⏱️ Too slow |
| ret2dlresolve | ❌ No | Hard | ✅ Perfect fit |

## Next Steps

After mastering this challenge:
1. **SROP** - Sigreturn-oriented programming
2. **ret2csu** - Using `__libc_csu_init` gadgets
3. **Format String** - Different vulnerability class
4. **Heap Exploitation** - UAF, double-free, etc.

## Resources

- **Pwntools Docs:** https://docs.pwntools.com/en/stable/rop/ret2dlresolve.html
- **ret2ld.com:** Visual guide to ret2dlresolve
- **GOT/PLT Guide:** Understanding dynamic linking

---

**See SOLUTION_GUIDE.md for the complete detailed walkthrough!**
