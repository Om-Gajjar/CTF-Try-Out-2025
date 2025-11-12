# HTB Abyss - Pwn Challenge

## Challenge Information
- **Name:** Abyss
- **Category:** Pwn (Binary Exploitation)
- **Difficulty:** Easy
- **Points:** 1000
- **Connection:** 83.136.249.223:53373

## Status
⚠️ **In Progress** - Vulnerability identified, exploit under development

---

## Files

### Challenge Files
- `abyss` - Vulnerable binary (17KB)
- `source.c` - Source code (provided)
- `flag.txt` - Local test flag

### Documentation
- `README.md` - This file
- `ANALYSIS.md` - Vulnerability analysis and exploit strategy
- `TOOLS_LIST.md` - Comprehensive PWN tools reference
- `TOOLS_INSTALLATION.md` - Installation guide for all tools

---

## Quick Start

### 1. Verify Tools Installation
```bash
# Check pwntools
python3 -c "from pwn import *; print(context)"

# Check ROPgadget
ROPgadget --version

# Check GDB enhancement
gdb -q  # Should show pwndbg
```

### 2. Analyze the Binary
```bash
# Check protections
python3 -c "from pwn import *; print(checksec('./abyss'))"

# Disassemble
objdump -d abyss -M intel | less

# View source code
cat source.c
```

### 3. Debug with GDB
```bash
gdb ./abyss

# Set breakpoint at vulnerable function
b *cmd_login

# Run with test input
r < payload.bin

# Examine stack
telescope $rsp 20
```

---

## Vulnerability Summary

### Type
Buffer overflow in `cmd_login()` function

### Location
```c
i = 5;
while (buf[i] != '\0')
{
    user[i - 5] = buf[i];
    i++;
}
```

### Issue
- No bounds checking on copy operation
- Loop variable `i` can be overwritten
- Allows controlling return address

### Stack Layout
```
rbp-0x610: buf[512]
rbp-0x410: pass[512]
rbp-0x210: user[512]
rbp-0x010: i (loop variable)
rbp:       saved rbp
rbp+8:     return address
```

---

## Exploit Strategy

According to writeups, the exploit involves:

1. **Overflow user buffer** to overwrite loop variable `i`
2. **Control `i` value** to make subsequent writes target return address
3. **Overwrite return address** to jump to `0x401500` (cmd_read after logged_in check)
4. **Use READ command** to retrieve flag without authentication

### Key Addresses
- `logged_in` global: `0x4040c0`
- `cmd_read` (after check): `0x401500`
- Set `logged_in=1`: `0x401485`

---

## Tools Used

### Essential
- **pwntools** - Exploit development framework
- **pwndbg** - Enhanced GDB
- **ROPgadget** - ROP gadget finder

### Supporting
- **strace** - System call tracer
- **ltrace** - Library call tracer
- **objdump** - Disassembler
- **one_gadget** - One-shot RCE finder

See `TOOLS_LIST.md` for detailed tool documentation.

---

## References

- [HTB CTF Try Out Event 1434](https://ctf.hackthebox.com/event/1434)
- [Motasem's Abyss Writeup](https://motasem-notes.net/hackthebox-abyss-writeup-binary-exploitation-ctf/)

---

## TODO

- [ ] Calculate precise offset for `i` overwrite
- [ ] Craft working payload with correct offsets
- [ ] Test exploit locally
- [ ] Test exploit remotely
- [ ] Capture flag
- [ ] Create final working exploit script
- [ ] Document complete solution

---

## Notes

The key insight for this challenge is **overwriting the loop variable `i`** to control where subsequent data is written. This is a unique variation on buffer overflows that requires:

1. Understanding stack variable layout
2. Calculating precise offsets
3. Crafting payload within 512-byte constraint
4. Testing with GDB for offset verification

---

**Status**: Tools installed ✅ | Analysis complete ✅ | Exploit pending ⚠️

**Last Updated**: 2024-11-10
