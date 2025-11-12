# HTB Abyss - Pwn Challenge (INCOMPLETE)

## Challenge Information
- **Name:** Abyss
- **Category:** Pwn (Binary Exploitation)
- **Difficulty:** Easy
- **Points:** 1000

## Status
⚠️ **Challenge analysis in progress** - Exploit development incomplete

---

## Vulnerability Analysis

### Source Code Review

The challenge provides source code (`source.c`) with a clear buffer overflow vulnerability in the `cmd_login()` function:

```c
i = 5;
while (buf[i] != '\0')
{
    user[i - 5] = buf[i];
    i++;
}
user[i - 5] = '\0';
```

**Critical Issues:**
1. No bounds checking on the copy operation
2. If `buf` doesn't contain a null terminator, the loop continues reading past the buffer
3. The loop variable `i` is stored on the stack and can be overwritten

### Stack Layout

From disassembly analysis:
```
rbp-0x610: buf[512]
rbp-0x410: pass[512]
rbp-0x210: user[512]
rbp-0x010: i (loop variable, 4 bytes)
rbp:       saved rbp
rbp+8:     return address
```

### Exploit Strategy

According to writeups:
1. Fill the `user` buffer completely (507 bytes from `buf[5:511]`)
2. Overflow to overwrite the variable `i` with a crafted value
3. Control `i` to make subsequent writes target the return address
4. Overwrite return address to jump to `0x401500` (cmd_read after logged_in check)
5. Use READ command to retrieve flag

---

## Files Analyzed

### source.c
- `cmd_login()`: Vulnerable authentication function
- `cmd_read()`: File read function (requires logged_in = 1)
- `main()`: Command loop

### Binary (abyss)
- 64-bit ELF
- Dynamically linked
- Not stripped
- No stack canary (vulnerable to buffer overflow)

### Key Addresses
- `logged_in` global: `0x4040c0`
- `cmd_read` (after check): `0x401500`
- Set `logged_in=1`: `0x401485`

---

## Challenges Encountered

1. **Buffer constraints**: `read()` only reads 512 bytes maximum
2. **Self-terminating overflow**: `pass` buffer is zero-initialized, causing early termination
3. **Precise offset calculation**: Need exact offset to overwrite `i` correctly
4. **ROP chain construction**: Limited payload space

---

## References

- [HTB Business CTF 2024 - Abyss Writeup](https://blog.ukatemi.com/blog/2024-05-17-hackthebox-business-pwn-abyss/)
- [Motasem's Abyss Writeup](https://motasem-notes.net/hackthebox-abyss-writeup-binary-exploitation-ctf/)

---

## TODO

- [ ] Complete precise offset calculation
- [ ] Test exploit with correct `i` overwrite value  
- [ ] Verify ROP chain reaches target
- [ ] Capture flag and document solution
- [ ] Create clean, working exploit script
- [ ] Add educational documentation

---

## Notes for Future Solving

The key insight is **overwriting the loop variable `i`** to control where subsequent data is written. This is a unique variation on standard buffer overflows that requires:

1. Understanding stack variable layout
2. Calculating precise offsets
3. Crafting payload within the 512-byte constraint
4. Testing with trial and error or debugging with GDB

**Lesson**: Always analyze loop variables in buffer overflow scenarios - they can be powerful exploit primitives!

---

*Challenge attempted but not completed - requires further debugging and testing*
*Created: 2024-11-10*
