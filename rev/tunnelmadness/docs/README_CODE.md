# Tunnel Challenge - Complete Source Code Reconstruction

## Overview

This directory contains the complete reconstructed C source code for the "Tunnel" binary from HackTheBox.

## Files

1. **tunnel_reconstructed.c** - Main source code with all game logic
2. **maze_data.c** - Maze data array (8000 cells, 128KB)
3. **Makefile** - Build configuration
4. **README_CODE.md** - This file

## Compilation

```bash
make
```

This will compile both `tunnel_reconstructed.c` and `maze_data.c` together into the `tunnel_rebuilt` executable.

## File Structure

### tunnel_reconstructed.c

Contains:
- `Cell` structure - Represents one maze cell (x, y, z, type)
- `Position` structure - Player position
- `get_cell()` - Calculates maze array index from 3D coordinates
- `get_flag()` - Reads and displays /flag.txt
- `prompt_and_update_pos()` - Handles user input and movement
- `main()` - Game loop

### maze_data.c

Contains:
- Complete maze array with 8000 cells
- Each cell has coordinates (x, y, z) and type:
  - Type 0: Start position (0,0,0)
  - Type 1: Passable cell
  - Type 2: Wall (blocked)
  - Type 3: Goal (19,19,19)

## How It Works

### Maze Structure

The maze is a 3D grid of 20×20×20 cells (coordinates 0-19).

**Index Calculation:**
```c
index = x * 400 + y * 20 + z
```

This comes from the assembly:
```asm
lea    (%rax,%rax,4),%rax    ; rax = x * 5
lea    (%rax,%rax,4),%rax    ; rax = x * 25
shl    $0x4,%rax              ; rax = x * 400
lea    (%rdx,%rdx,4),%rdx    ; rdx = y * 5
lea    (%rax,%rdx,4),%rax    ; rax = x*400 + y*20
add    %rdx,%rax              ; rax = x*400 + y*20 + z
```

### Movement System

- **F** = Forward (x+1)
- **B** = Backward (x-1)
- **R** = Right (y+1)
- **L** = Left (y-1)
- **U** = Up (z+1)
- **D** = Down (z-1)
- **Q** = Quit

Each move:
1. Checks bounds (0-19)
2. Checks target cell type
3. If type != 2 (wall), moves player
4. Otherwise prints "Cannot move that way"

### Win Condition

When player reaches a cell with type == 3, the game:
1. Prints success message
2. Calls `get_flag()` to read `/flag.txt`
3. Exits

## Reverse Engineering Process

### Step 1: Identify Key Functions

```bash
nm tunnel | grep -E "flag|maze|main"
```

Found:
- `get_flag` at 0x1446
- `get_cell` at 0x11b5
- `prompt_and_update_pos` at 0x11e3
- `main` at 0x1538
- `maze` data at 0x20e0

### Step 2: Disassemble Functions

```bash
objdump -d tunnel > disasm.txt
```

Analyzed each function's assembly to understand logic.

### Step 3: Extract Maze Data

```python
with open('tunnel', 'rb') as f:
    f.seek(0x20e0)  # .rodata offset
    maze_data = f.read(8000 * 16)  # 8000 cells × 16 bytes
```

### Step 4: Reconstruct C Code

Translated assembly back to C, preserving:
- Data structures
- Algorithm logic
- Control flow
- String constants

## Differences from Original

1. **Code Style**: Cleaned up for readability
2. **Comments**: Added explanatory comments
3. **Structure**: Split into logical functions
4. **No Optimization**: Unoptimized for clarity

The logic and behavior are identical to the original binary.

## Testing

Create a test flag file and run:

```bash
echo "HTB{test_flag}" > flag.txt
make test
```

## Usage

```bash
./tunnel_rebuilt
```

Enter directions to navigate the 3D maze:
- Start at (0, 0, 0)
- Goal is at (19, 19, 19)
- Find the path through passable cells

## Solving the Maze

Since the maze data is known, you can write a solver:

```python
from collections import deque

def solve():
    start = (0, 0, 0)
    goal = (19, 19, 19)
    
    # BFS to find shortest path
    queue = deque([(start, [])])
    visited = {start}
    
    while queue:
        pos, path = queue.popleft()
        if pos == goal:
            return path
        
        # Try all 6 directions...
```

See `SOLUTION_GUIDE.md` for complete solver implementation.

## Binary Comparison

To verify the reconstruction:

```bash
# Compare behavior
echo "U\nU\nU\nQ" | ./tunnel > original.out
echo "U\nU\nU\nQ" | ./tunnel_rebuilt > rebuilt.out
diff original.out rebuilt.out
```

## Assembly Details

### get_cell Function

Original assembly at 0x11b5:
```asm
mov    (%rdi),%eax           ; eax = pos->x
lea    (%rax,%rax,4),%rax    ; rax = x * 5
lea    (%rax,%rax,4),%rax    ; rax = x * 25
shl    $0x4,%rax              ; rax = x * 400
mov    0x4(%rdi),%edx        ; edx = pos->y
lea    (%rdx,%rdx,4),%rdx    ; rdx = y * 5
lea    (%rax,%rdx,4),%rax    ; rax = x*400 + y*20
mov    0x8(%rdi),%edx        ; edx = pos->z
add    %rdx,%rax              ; rax = x*400 + y*20 + z
shl    $0x4,%rax              ; rax *= 16 (cell size)
lea    0xf01(%rip),%rdx      ; rdx = &maze
add    %rdx,%rax              ; rax = &maze[index]
ret
```

Reconstructed C:
```c
Cell* get_cell(Position* pos) {
    int index = pos->x * 400 + pos->y * 20 + pos->z;
    return &maze[index];
}
```

### prompt_and_update_pos Function

Uses a jump table at 0x2080 for switch statement.

Original switch compilation:
1. Convert to uppercase with `toupper`
2. Subtract 'B' (0x42)
3. Compare with 0x13 (range check)
4. Index into jump table
5. Jump to case handler

Each case:
1. Checks bounds
2. Calculates target position
3. Calls `get_cell()`
4. Checks if type == 2 (wall)
5. Updates position if valid

## Educational Value

This reconstruction demonstrates:

1. **Reverse Engineering** - Assembly → C translation
2. **Data Structure Recovery** - Finding maze format
3. **Algorithm Analysis** - Understanding game logic
4. **Binary Analysis** - Using objdump, nm, strings
5. **Memory Layout** - .rodata, .text sections

## Security Notes

This is a CTF challenge designed for learning. The binary:

- Has no anti-debugging measures
- Contains symbols (not stripped)
- Uses simple validation logic
- Stores maze data in plaintext

Real-world applications would:
- Strip symbols
- Add anti-tampering
- Encrypt sensitive data
- Use code obfuscation

## References

- Original Binary: `tunnel` (ELF 64-bit)
- HackTheBox Challenge: "TunnelMadness"
- Difficulty: Medium (975 points)
- Category: Pwn/Reversing

## License

Educational use only. Original challenge © HackTheBox.

## Authors

- Original Challenge: HackTheBox Team
- Reconstruction: Reverse Engineering Analysis
- Date: November 2025
