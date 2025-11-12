# Abyss - CTF Challenge

## 📋 Challenge Information

**Category:** Pwn / Binary Exploitation  
**Difficulty:** Easy  
**Challenge Type:** Format String Vulnerability / Stack Exploitation  

## 📝 Challenge Description

Advanced pwn challenge involving format string vulnerabilities and stack manipulation. Exploit printf format string bugs to leak information and control program execution.

## 🚀 Quick Start

```bash
cd pwn/abyss
# Build Docker (if needed)
bash data/build-docker.sh
# See docs/ for complete solution guides
```

## 📁 Folder Structure

```
abyss/
├── README.md
├── solution/              # Exploit scripts
├── data/                  # Docker, build files
├── docs/                  # Multiple guides (INDEX, VISUAL_GUIDE, etc.)
└── src/                   # Source code
    ├── source.c          # Vulnerable C code
    ├── abyss             # Binary
    ├── flag.txt
    ├── ANALYSIS.md
    └── TOOLS_*.md
```

## 💡 Key Concepts

- Format string vulnerabilities
- Stack manipulation
- Information disclosure
- Control flow hijacking

## 📖 Documentation

Multiple comprehensive guides in `docs/`:
- INDEX.md - Main guide
- VISUAL_GUIDE.md - Visual explanations
- QUICK_REFERENCE.md - Quick commands
- SOLUTION_COMPLETE.md - Full solution

---

**Difficulty:** Easy  
**Type:** Format String Exploitation
