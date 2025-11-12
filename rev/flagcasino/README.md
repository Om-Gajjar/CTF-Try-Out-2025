# Flag Casino - CTF Challenge

## 📋 Challenge Information

**Category:** Reverse Engineering  
**Difficulty:** Easy  
**Challenge Type:** Algorithm Analysis / Bruteforce  

## 📝 Challenge Description

Reverse engineer a casino binary to understand its internal logic and find the winning combination that reveals the flag. Multiple solution approaches provided.

## 🚀 Quick Start

```bash
cd rev/flagcasino

# Compile and run solvers
gcc solution/solve.c -o solve
./solve

# Or try other solution versions
gcc solution/solve2.c -o solve2
gcc solution/solve3.c -o solve3
```

## 📁 Folder Structure

```
flagcasino/
├── README.md
├── solution/
│   ├── solve.c           # Solution approach 1
│   ├── solve2.c          # Solution approach 2
│   ├── solve3.c          # Solution approach 3
│   └── test_n.c          # Test cases
├── data/
│   └── casino            # Target binary
└── docs/
    └── SOLUTION_GUIDE.md
```

## 💡 Key Concepts

- Algorithm reversal
- Brute force techniques
- Program logic analysis
- Multiple solution paths

---

**Type:** Algorithm Analysis  
**Tools:** GCC, debugger, decompiler
