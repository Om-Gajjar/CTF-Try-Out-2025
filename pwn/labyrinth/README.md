# Labyrinth - CTF Challenge

## 📋 Challenge Information

**Category:** Pwn / Binary Exploitation  
**Difficulty:** Easy-Medium  
**Challenge Type:** Stack-based Buffer Overflow with Canary Bypass  

## 📝 Challenge Description

Navigate through a labyrinth of security protections. This challenge involves bypassing stack canaries and exploiting buffer overflows in a more realistic scenario with modern protections enabled.

## 🚀 Quick Start

```bash
cd pwn/labyrinth
python3 solution/exploit.py
```

## 📁 Folder Structure

```
labyrinth/
├── README.md
├── solution/
│   └── exploit.py        # Python exploit
├── data/
│   ├── labyrinth         # Target binary
│   ├── flag.txt
│   └── glibc/            # Library files
└── docs/
    ├── README.md         # Additional info
    └── SOLUTION_GUIDE.md # Complete walkthrough
```

## 💡 Key Concepts

- Stack canaries and bypass techniques
- Return-oriented programming (ROP)
- Information leaks
- ASLR and PIE

## 📖 Resources

- See `docs/SOLUTION_GUIDE.md` for detailed walkthrough
- Exploit script in `solution/exploit.py`

---

**Difficulty:** Easy-Medium  
**Type:** Stack Overflow + Canary Bypass
