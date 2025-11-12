# Getting Started - CTF Challenge

## 📋 Challenge Information

**Category:** Pwn / Binary Exploitation  
**Difficulty:** Very Easy  
**Points:** 975  
**Challenge Type:** Buffer Overflow (Introduction)  

## 📝 Challenge Description

An introductory buffer overflow challenge designed to teach the fundamentals of memory corruption. Learn how programs store data in memory and exploit weaknesses to retrieve a hidden flag by overflowing a buffer to overwrite a target value.

## 🎯 Solution Overview

This classic buffer overflow challenge demonstrates:
1. Understanding memory layout (stack, buffers)
2. Identifying overflow vulnerabilities
3. Calculating buffer sizes
4. Overwriting target variables
5. Retrieving the flag

## 🚀 Quick Start

### Prerequisites
- Python 3 with pwntools
- Basic understanding of C and memory
- GDB (for debugging)

### Installation
```bash
pip install pwntools
```

### Running the Solution
```bash
cd pwn/getting_started
python3 solution/wrapper.py
```

## 📁 Folder Structure

```
getting_started/
├── README.md              # This file
├── solution/              # Exploit scripts
│   └── wrapper.py        # Python exploit
├── data/                  # Challenge files
│   ├── gs                # Target binary
│   ├── flag.txt          # Flag file
│   └── glibc/            # Library files
├── docs/                  # Documentation
│   └── SOLUTION_GUIDE.md # Complete walkthrough
└── src/                   # Source code (if available)
```

## 🔧 Technical Details

### The Vulnerability
Classic stack-based buffer overflow where input exceeds buffer size, allowing adjacent memory to be overwritten.

### Exploit Method
1. Identify buffer size
2. Calculate offset to target variable
3. Craft payload with overflow data
4. Send payload to overwrite target
5. Trigger flag reveal

## 💡 Learning Points

1. **Buffer Overflows:** Understanding memory corruption
2. **Stack Layout:** How variables are stored
3. **Pwntools:** Using Python for exploitation
4. **Binary Analysis:** Reading assembly/debugging
5. **Memory Safety:** Importance of bounds checking

## 📖 Additional Resources

- See `docs/SOLUTION_GUIDE.md` for detailed walkthrough
- [Pwntools Documentation](https://docs.pwntools.com/)
- [Buffer Overflow Basics](https://owasp.org/www-community/vulnerabilities/Buffer_Overflow)

---

**Challenge Type:** Binary Exploitation / Stack Overflow  
**Key Skills:** Memory layout, buffer overflow, pwntools  
**Difficulty:** Very Easy (introductory level)
