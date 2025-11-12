# Tunnel Madness - CTF Challenge

## 📋 Challenge Information

**Category:** Reverse Engineering  
**Difficulty:** Medium  
**Challenge Type:** Maze Solving / Path Finding  

## 📝 Challenge Description

Navigate through a complex tunnel system by reverse engineering the maze logic. Reconstruct the tunnel structure and find the correct path to the flag.

## 🚀 Quick Start

```bash
cd rev/tunnelmadness

# Run remote solver
python3 solution/solve_remote.py

# View reconstructed code
cat data/tunnel_reconstructed.c

# View maze visualization
cat data/maze_combined.txt
```

## 📁 Folder Structure

```
tunnelmadness/
├── README.md
├── solution/
│   ├── solve_remote.py       # Remote solver
│   └── create_combined_view.py  # Maze visualizer
├── data/
│   ├── tunnel_rebuilt        # Rebuilt binary
│   ├── tunnel_reconstructed.c # Reconstructed source
│   ├── maze_combined.txt     # Maze visualization
│   └── maze_paths_only.txt   # Path data
├── docs/
│   ├── README.md             # Challenge description
│   ├── README_CODE.md        # Code documentation
│   └── SOLUTION_GUIDE.md     # Solution walkthrough
└── src/
    └── maze_data.c           # Maze data structure
```

## 💡 Key Concepts

- Code reconstruction
- Maze solving algorithms
- Path finding
- Logic analysis

---

**Type:** Algorithm Analysis + Path Finding  
**Tools:** Python, C compiler, visualization scripts
