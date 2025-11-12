# TunnelMadness - HackTheBox Challenge

> 3D Maze Navigation Reverse Engineering Challenge

![Status](https://img.shields.io/badge/Status-SOLVED-success)
![Difficulty](https://img.shields.io/badge/Difficulty-Medium-yellow)
![Points](https://img.shields.io/badge/Points-975-blue)
![Category](https://img.shields.io/badge/Category-Pwn%2FReversing-purple)

---

## 📋 Challenge Information

- **Name:** TunnelMadness
- **Category:** Pwn / Reversing
- **Difficulty:** Medium
- **Points:** 975
- **Status:** ✅ SOLVED (2025-11-09)

### Description

> Within Vault 8707 are master keys used to access any vault in the country. Unfortunately, the entrance was caved in long ago. There are decades old rumors that the few survivors managed to tunnel out deep underground and make their way to safety. Can you uncover their tunnel and break back into the vault?

---

## 🎯 Quick Solution

### **Flag**
```
HTB{tunn3l1ng_ab0ut_in_3d_c803667e2c7cd64d19bee68bc36db107}
```

### **Solution Path** (63 moves)
```
UUURUFURRFFRRUFUFFFUFUUUUFRRUUUFURFDFFRRRRRFRR
```

### **Automated Solver**
```bash
python3 solve_remote.py
```

---

## 📁 Repository Contents

### Source Code
- **tunnel** - Original binary (141 KB)
- **tunnel_reconstructed.c** - Reconstructed C source code
- **maze_data.c** - Complete maze array (8000 cells)
- **tunnel_rebuilt** - Recompiled binary (142 KB)

### Documentation
- **README.md** - This file
- **SOLUTION_GUIDE.md** - Detailed solution walkthrough
- **COMPLETE_SOURCE_CODE.md** - Complete code documentation
- **README_CODE.md** - Technical reverse engineering details

### Scripts
- **solve_remote.py** - Automated solver (Python)
- **solve_maze.py** - Local maze solver
- **visualize_maze.py** - Maze visualization tool
- **solution_path.txt** - Verified solution with annotations

### Build Files
- **Makefile** - Compilation configuration

---

## 🚀 Getting Started

### 1. Explore the Binary

```bash
# Check binary info
file tunnel
nm tunnel | grep -E "flag|maze|main"

# Disassemble
objdump -d tunnel > tunnel.asm

# Extract strings
strings tunnel
```

### 2. Compile Reconstructed Code

```bash
make
./tunnel_rebuilt
```

### 3. Solve the Challenge

```bash
# Automated
python3 solve_remote.py

# Manual
nc 83.136.252.27 57790
# Enter: UUURUFURRFFRRUFUFFFUFUUUUFRRUUUFURFDFFRRRRRFRR
```

---

## 🧩 Challenge Breakdown

### Architecture

- **Binary:** ELF 64-bit Linux executable
- **Language:** C (reconstructed from assembly)
- **Maze:** 20×20×20 3D grid (8000 cells)
- **Goal:** Navigate from (0,0,0) to (19,19,19)

### Key Functions

```c
Cell* get_cell(Position* pos)           // Maze indexing
void get_flag()                         // Flag reader
void prompt_and_update_pos(Position*)   // Movement handler
int main()                              // Game loop
```

### Movement System

| Command | Action | Delta |
|---------|--------|-------|
| F | Forward | x+1 |
| B | Backward | x-1 |
| R | Right | y+1 |
| L | Left | y-1 |
| U | Up | z+1 |
| D | Down | z-1 |
| Q | Quit | exit |

### Cell Types

- **0** = Start position (0,0,0)
- **1** = Passable cell
- **2** = Wall (blocked)
- **3** = Goal (19,19,19)

---

## 🔍 Reverse Engineering Process

### Step 1: Binary Analysis

```bash
# Identify key functions
nm tunnel | grep ' T '

# Find maze data location
readelf -S tunnel | grep rodata
# Found: .rodata at 0x2000, maze at 0x20e0
```

### Step 2: Extract Maze Data

```python
import struct

with open('tunnel', 'rb') as f:
    f.seek(0x20e0)
    maze_data = f.read(8000 * 16)
    
    for i in range(8000):
        cell = struct.unpack('iiii', maze_data[i*16:(i+1)*16])
        print(f"Cell {i}: x={cell[0]}, y={cell[1]}, z={cell[2]}, type={cell[3]}")
```

### Step 3: Understand Index Calculation

From assembly at `get_cell` (0x11b5):

```asm
lea    (%rax,%rax,4),%rax    ; rax = x * 5
lea    (%rax,%rax,4),%rax    ; rax = x * 25
shl    $0x4,%rax              ; rax = x * 400
lea    (%rdx,%rdx,4),%rdx    ; rdx = y * 5
lea    (%rax,%rdx,4),%rax    ; rax = x*400 + y*20
add    %rdx,%rax              ; rax = x*400 + y*20 + z
shl    $0x4,%rax              ; rax *= 16
```

**Formula:** `index = (x * 400 + y * 20 + z) * 16`

### Step 4: Reconstruct C Code

Translated assembly to readable C:

```c
typedef struct {
    int x, y, z, type;
} Cell;

Cell* get_cell(Position* pos) {
    int index = pos->x * 400 + pos->y * 20 + pos->z;
    return &maze[index];
}
```

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Maze Dimensions | 20×20×20 |
| Total Cells | 8,000 |
| Passable Cells | 64 |
| Wall Cells | 7,935 |
| Start Cell | 1 |
| Goal Cell | 1 |
| Solution Length | 63 moves |
| Binary Size | 141 KB |
| Source Code Lines | ~240 |

---

## 🛠️ Tools Used

- **objdump** - Disassembly
- **nm** - Symbol table extraction
- **readelf** - ELF header analysis
- **strings** - String extraction
- **Python** - Data extraction & solving
- **GCC** - Recompilation
- **netcat** - Network interaction

---

## 📚 Documentation

### Detailed Guides

1. **SOLUTION_GUIDE.md**
   - Challenge walkthrough
   - Dynamic maze exploration
   - BFS/DFS algorithms
   - Complete solution

2. **COMPLETE_SOURCE_CODE.md**
   - Full C code listing
   - Data structures
   - Algorithm explanations
   - Usage examples

3. **README_CODE.md**
   - Technical reverse engineering
   - Assembly analysis
   - Index calculation details
   - Memory layout

---

## 🎓 Learning Objectives

### Skills Demonstrated

✅ **Binary Reverse Engineering**
- ELF format analysis
- Assembly → C translation
- Symbol table interpretation

✅ **Data Structure Recovery**
- Array indexing algorithms
- Structure field identification
- Memory layout reconstruction

✅ **Algorithm Implementation**
- 3D pathfinding (BFS/DFS)
- Maze navigation
- Optimal path finding

✅ **Network Programming**
- Socket communication
- Protocol interaction
- Automated solving

---

## 🔐 Security Analysis

### Vulnerabilities

1. **Input Validation**
   - `scanf` without bounds checking
   - No input sanitization

2. **Information Disclosure**
   - Symbols not stripped
   - Maze data in plaintext
   - Predictable structure

3. **Path Traversal**
   - Hardcoded `/flag.txt`
   - No access control

### Mitigations (Production)

- Strip binary symbols
- Encrypt sensitive data
- Use `fgets` instead of `scanf`
- Add input validation
- Implement proper access controls

---

## 🧪 Testing

### Local Testing

```bash
# Test movement
echo -e "U\nU\nU\nQ" | ./tunnel_rebuilt

# Test with flag
echo "HTB{test}" > flag.txt
./tunnel_rebuilt
```

### Remote Testing

```bash
# Test connection
nc 83.136.252.27 57790

# Submit solution
python3 solve_remote.py
```

---

## 📝 Solution Verification

### Manual Verification

```bash
# Connect to server
nc 83.136.252.27 57790

# Enter moves (one per line):
# U U U R U F U R R F F R
# R U F U F F F U F U U U U U
# F R R U U U F U R F D F F
# U F F R R R R R F R R

# Expected output:
# You break into the vault and read the secrets within...
# HTB{tunn3l1ng_ab0ut_in_3d_c803667e2c7cd64d19bee68bc36db107}
```

### Automated Verification

```bash
./solve_remote.py
# Should print flag if server is running
```

---

## 🏆 Challenge Complete

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     ✅ CHALLENGE SOLVED - FLAG CAPTURED                  ║
║                                                           ║
║     HTB{tunn3l1ng_ab0ut_in_3d_c803667e2c7cd64d19bee68bc36db107}
║                                                           ║
║     Points: 975                                           ║
║     Difficulty: Medium                                    ║
║     Category: Pwn/Reversing                               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 📞 Support

For questions or issues:
- Review documentation in this repository
- Check solution guide for detailed walkthrough
- Examine reconstructed source code
- Analyze original binary with provided tools

---

## 📄 License

Educational purposes only. Original challenge © HackTheBox.

---

## 👥 Credits

- **Challenge Creator:** HackTheBox Team
- **Solution & Documentation:** Reverse Engineering Analysis
- **Date Solved:** November 9, 2025

---

**Version:** 1.1  
**Last Updated:** 2025-11-09  
**Status:** ✅ SOLVED & DOCUMENTED
