# HTB Regularity - Complete Solution Package

## 📁 Contents

This directory contains everything you need to understand and replicate the solution for the HTB Regularity pwn challenge.

### Documentation Files

1. **SOLUTION.md** - Complete detailed writeup
   - Full technical analysis
   - Step-by-step exploitation guide
   - Concepts explained for beginners
   - ~14KB, perfect for deep learning

2. **QUICK_REFERENCE.md** - Quick reference guide
   - Cheat sheet format
   - Key addresses and commands
   - One-liner exploit
   - ~5KB, perfect for quick lookups

3. **README.md** - This file
   - Overview and file descriptions
   - Quick start guide

### Exploit Files

1. **final_working_exploit.py** - Production exploit
   - Well-commented and explained
   - Command-line argument support
   - Error handling included
   - Ready to use!

2. **exploit.py** - Original development version
3. **interactive_exploit.py** - Interactive shell version
4. **srop_attempt.py** - Alternative technique exploration

### Binary Files

1. **regularity** - The vulnerable binary
2. **flag.txt** - Local test flag

---

## 🚀 Quick Start

### For Complete Beginners (2nd Year BScIT Students)

**Start here in this order:**

1. Read **SOLUTION.md** sections:
   - Overview
   - Understanding the Vulnerability
   - Key Concepts Explained

2. Read **QUICK_REFERENCE.md** for visual aids

3. Run the exploit:
   ```bash
   python3 final_working_exploit.py <host> <port>
   ```

4. Go back to **SOLUTION.md** and read:
   - Binary Analysis
   - Exploitation Technique

### For Quick Solution

If you just need to solve the challenge:

```bash
python3 final_working_exploit.py 83.136.249.223 56191
```

Or use the one-liner from **QUICK_REFERENCE.md**

---

## 🎯 Challenge Details

- **Name**: Regularity
- **Category**: Pwn
- **Difficulty**: Very Easy (★☆☆☆☆)
- **Points**: 975
- **Skills**: Buffer overflow, Assembly basics, Register manipulation

**Flag**: `HTB{juMp1nG_w1tH_tH3_r3gIsT3rS?_f2f06e7ebdddb7d46d7e2def9bc16714}`

---

## 🧠 What You'll Learn

### Technical Skills
- Buffer overflow exploitation
- Return to register (ret2reg) technique
- x86-64 assembly basics
- Stack structure and manipulation
- Shellcode development

### Tools
- `objdump` - Binary disassembly
- `readelf` - ELF file analysis
- `gdb` - Debugging
- Python - Exploit development
- `struct` module - Binary data packing

---

## 📖 Recommended Reading Order

### Complete Learning Path (2-3 hours)

1. **Start**: Read SOLUTION.md "Overview" and "Understanding the Vulnerability"
   - *Time: 15 minutes*
   - *Goal: Understand buffer overflows*

2. **Analysis**: Read SOLUTION.md "Binary Analysis"
   - *Time: 20 minutes*
   - *Goal: Learn how to analyze binaries*
   - *Hands-on: Try the commands yourself*

3. **Technique**: Read SOLUTION.md "Exploitation Technique: Ret2Reg"
   - *Time: 20 minutes*
   - *Goal: Understand the clever solution*

4. **Practice**: Run the exploit
   - *Time: 10 minutes*
   - *Goal: Get the flag!*

5. **Deep Dive**: Read SOLUTION.md "Key Concepts Explained"
   - *Time: 30 minutes*
   - *Goal: Understand all the details*

6. **Reference**: Keep QUICK_REFERENCE.md handy
   - *Time: Ongoing*
   - *Goal: Quick lookups when needed*

### Quick Solution Path (15 minutes)

1. Read QUICK_REFERENCE.md "Core Concept"
2. Read QUICK_REFERENCE.md "Memory Layout"
3. Run `python3 final_working_exploit.py`
4. Done!

---

## 🛠️ Requirements

### System Requirements
- Linux (Kali/Ubuntu/Debian recommended)
- Python 3.x
- Network access to HTB instance

### Python Libraries
```bash
# All standard library - no installation needed!
import socket    # Network connections
import struct    # Binary data packing
import time      # Timing delays
import sys       # System operations
```

---

## 💡 Key Insights

### The "Regularity" Hint

The challenge name "Regularity" hints at the solution:
- **Regular** = Predictable, unchanging
- The `jmp rsi` address at `0x401041` is **regular** (never changes)
- Even though stack addresses change (ASLR), code addresses don't (no PIE)
- This **regularity** is what we exploit!

### Why This Works When ASLR is On

```
❌ Traditional approach:
   Stack address changes → Can't find shellcode → Exploit fails

✅ Ret2Reg approach:
   Code address fixed → Register points to shellcode → Exploit works!
```

---

## 🎓 Educational Value

This challenge teaches:

1. **Fundamentals**: Basic binary exploitation concepts
2. **Problem Solving**: How to bypass modern protections
3. **Creative Thinking**: Using registers instead of guessing addresses
4. **Tools Usage**: Real-world security analysis tools
5. **Assembly**: Understanding low-level code

**Perfect for**: Computer Science students, Security beginners, CTF newcomers

---

## 🔧 Troubleshooting

### Common Issues

**Q: Exploit doesn't work?**
```
A: Check these:
   1. Is the instance still running?
   2. Correct IP and port?
   3. Payload is 264 bytes?
   4. Using little endian format?
```

**Q: How do I test locally?**
```
A: Disable ASLR first:
   echo 0 | sudo tee /proc/sys/kernel/randomize_va_space
   Then: (cat /tmp/payload; cat) | ./regularity
```

**Q: Can I use pwntools?**
```
A: Yes! The solution works with or without pwntools.
   Our version uses only standard library for simplicity.
```

---

## 📊 File Sizes

```
regularity                  9.1K  (Binary)
flag.txt                    27B   (Local test flag)
SOLUTION.md                 14K   (Complete guide)
QUICK_REFERENCE.md          5.6K  (Quick ref)
final_working_exploit.py    4.3K  (Production exploit)
README.md                   This file
```

---

## 🌟 Next Steps

After completing this challenge:

### Similar HTB Challenges
- **Racecar** - Another easy pwn
- **Delulu** - Format string basics
- **Tutorial** - More buffer overflows

### Advanced Topics to Study
- ROP (Return Oriented Programming)
- Format string vulnerabilities
- Heap exploitation
- Kernel exploitation

### Practice Resources
- **pwnable.kr** - Korean pwn challenges
- **exploit.education** - Free exploitation exercises
- **picoCTF** - Beginner CTF platform

---

## 👥 Credits

- **Challenge**: Hack The Box
- **Solution**: Community writeups
- **Documentation**: Created for educational purposes
- **Target Audience**: 2nd year BScIT students and beginners

---

## 📝 Notes

- Exploit tested and working as of Nov 2025
- All code is commented for educational purposes
- Screenshots and diagrams in SOLUTION.md
- Feel free to modify and learn from the code!

---

## 🤝 Contributing

Found a better way to explain something? Have suggestions?
Feel free to:
- Add more comments to code
- Improve documentation clarity
- Add visual diagrams
- Translate to other languages

---

## ⚖️ Disclaimer

This solution is for **educational purposes only**. Only use these techniques on:
- Your own systems
- Systems you have permission to test
- Authorized CTF challenges (like HTB)

**Never** use these techniques on systems without authorization.

---

## 📞 Support

If you're stuck:
1. Re-read SOLUTION.md carefully
2. Check QUICK_REFERENCE.md for quick help
3. Run `python3 final_working_exploit.py` with default values
4. Review the "Troubleshooting" section

---

**Happy Hacking! 🚀**

*Remember: Every expert was once a beginner. Take your time, understand each step, and enjoy the learning process!*
