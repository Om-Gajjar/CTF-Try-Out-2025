# Satellite Hijack - CTF Challenge

## 📋 Challenge Information

**Category:** Reverse Engineering  
**Difficulty:** Medium  
**Challenge Type:** Shared Library Analysis / Dynamic Analysis  

## 📝 Challenge Description

Hijack satellite communication by reverse engineering the satellite binary and its associated library. Understand the protocol and craft the correct input to retrieve the flag.

## 🚀 Quick Start

```bash
cd rev/satellitehijack

# Run solver
python3 solution/solver.py

# Analyze binary and library
objdump -d data/satellite
objdump -d data/library.so
```

## 📁 Folder Structure

```
satellitehijack/
├── README.md
├── solution/
│   └── solver.py         # Python solver
├── data/
│   ├── satellite         # Main binary
│   └── library.so        # Shared library
└── docs/
    └── SOLUTION_GUIDE.md
```

## 💡 Key Concepts

- Shared library analysis
- Dynamic linking
- Protocol reverse engineering
- Inter-process communication

---

**Type:** Dynamic Analysis + Shared Libraries  
**Tools:** Python, objdump, ltrace, strace
