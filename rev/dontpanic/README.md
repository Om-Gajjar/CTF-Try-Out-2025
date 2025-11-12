# Don't Panic - CTF Challenge

## 📋 Challenge Information

**Category:** Reverse Engineering  
**Difficulty:** Very Easy  
**Challenge Type:** Basic Binary Analysis  

## 📝 Challenge Description

An introductory reverse engineering challenge. Analyze the binary to understand its behavior and extract the flag without running it on the actual challenge server.

## 🚀 Quick Start

```bash
cd rev/dontpanic

# Analyze with strings
strings data/dontpanic | grep HTB

# Disassemble
objdump -d data/dontpanic | less

# Or use Ghidra/IDA for decompilation
```

## 📁 Folder Structure

```
dontpanic/
├── README.md
├── solution/              # Solution scripts/notes
├── data/
│   └── dontpanic         # Target binary
├── docs/
│   └── SOLUTION_GUIDE.md
└── src/                   # Source (if available)
```

## 💡 Key Concepts

- Binary analysis
- String extraction
- Static analysis
- Disassembly basics

## 📖 Resources

- See `docs/SOLUTION_GUIDE.md` for complete walkthrough

---

**Type:** Static Analysis  
**Tools:** strings, objdump, Ghidra
