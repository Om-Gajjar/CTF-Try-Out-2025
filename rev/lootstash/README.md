# Loot Stash - CTF Challenge

## 📋 Challenge Information

**Category:** Reverse Engineering  
**Difficulty:** Easy  
**Challenge Type:** Binary Analysis / Pattern Recognition  

## 📝 Challenge Description

Discover hidden loot in the binary by analyzing its structure and finding the stashed flag through careful reverse engineering.

## 🚀 Quick Start

```bash
cd rev/lootstash

# Analyze binary
file data/stash
strings data/stash
objdump -d data/stash

# Or use Ghidra/IDA
```

## 📁 Folder Structure

```
lootstash/
├── README.md
├── solution/              # Solution scripts
├── data/
│   └── stash             # Target binary
├── docs/
│   └── SOLUTION_GUIDE.md
└── src/                   # Source (if available)
```

## 💡 Key Concepts

- Binary structure analysis
- Hidden data extraction
- Reverse engineering methodology

## 📖 Resources

- See `docs/SOLUTION_GUIDE.md` for walkthrough

---

**Type:** Binary Analysis  
**Tools:** strings, objdump, Ghidra
