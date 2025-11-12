# Void - CTF Challenge

## 📋 Challenge Information

**Category:** Pwn / Binary Exploitation  
**Difficulty:** Medium  
**Challenge Type:** Advanced Buffer Overflow with Multiple Protections  

## 📝 Challenge Description

Navigate the void of modern security protections. This challenge combines multiple exploitation techniques to bypass NX, ASLR, PIE, and stack canaries to achieve code execution.

## 🚀 Quick Start

```bash
cd pwn/void
python3 solution/exploit_final.py
```

## 📁 Folder Structure

```
void/
├── README.md
├── solution/
│   └── exploit_final.py  # Final working exploit
├── data/
│   ├── void              # Target binary
│   ├── flag.txt
│   └── glibc/            # Library files
└── docs/
    ├── README.md         # Challenge info
    └── SOLUTION_GUIDE.md # Complete walkthrough
```

## 💡 Key Concepts

- Bypassing modern protections (NX, ASLR, PIE)
- ret2libc technique
- ROP chain construction
- Information leak exploitation
- Stack canary bypass

## 📖 Resources

- `docs/SOLUTION_GUIDE.md` - Detailed explanation
- `docs/README.md` - Challenge description
- `solution/exploit_final.py` - Complete exploit

## 🔧 Technical Stack

- NX (No-Execute) enabled
- ASLR (Address Space Layout Randomization)
- PIE (Position Independent Executable)
- Stack canaries
- Partial RELRO

---

**Difficulty:** Medium  
**Type:** Multi-Protection Bypass / ret2libc
