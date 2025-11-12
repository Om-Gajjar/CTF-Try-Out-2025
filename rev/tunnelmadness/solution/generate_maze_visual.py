#!/usr/bin/env python3
"""
Quick 3D Maze Visualizer - Automatically generates visualization
"""

import re

def parse_maze_data(filename):
    """Parse maze_data.c and extract cell information"""
    maze = {}
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Find all cell entries: { x, y, z, type}
    pattern = r'\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\}'
    matches = re.findall(pattern, content)
    
    for match in matches:
        x, y, z, cell_type = map(int, match)
        if z not in maze:
            maze[z] = {}
        if x not in maze[z]:
            maze[z][x] = {}
        maze[z][x][y] = cell_type
    
    return maze

def get_cell_char(cell_type):
    """Convert cell type to display character"""
    chars = {0: 'S', 1: '.', 2: '#', 3: 'G'}
    return chars.get(cell_type, '?')

def find_interesting_levels(maze):
    """Find Z-levels that have paths or goals"""
    interesting = []
    
    for z in sorted(maze.keys()):
        for x in maze[z]:
            for y in maze[z][x]:
                if maze[z][x][y] in [0, 1, 3]:
                    interesting.append(z)
                    break
            if z in interesting:
                break
    
    return interesting

# Parse maze
print("Parsing maze_data.c...")
maze = parse_maze_data('maze_data.c')

# Count cell types
type_counts = {0: 0, 1: 0, 2: 0, 3: 0}
for z in maze:
    for x in maze[z]:
        for y in maze[z][x]:
            type_counts[maze[z][x][y]] += 1

print(f"\nMaze Statistics:")
print(f"  Start cells (S): {type_counts[0]}")
print(f"  Path cells  (.): {type_counts[1]}")
print(f"  Wall cells  (#): {type_counts[2]}")
print(f"  Goal cells  (G): {type_counts[3]}")

# Find interesting levels
interesting = find_interesting_levels(maze)
print(f"\nLevels with paths: {interesting}")

# Generate visualization file
print("\nGenerating maze_visualization.txt...")
with open('maze_visualization.txt', 'w', encoding='utf-8') as f:
    f.write("="*60 + "\n")
    f.write(" 3D MAZE VISUALIZATION - Tunnel Challenge\n")
    f.write("="*60 + "\n\n")
    
    f.write("Legend:\n")
    f.write("  S = Start (type 0) - Starting position at (0,0,0)\n")
    f.write("  . = Path  (type 1) - Walkable path\n")
    f.write("  # = Wall  (type 2) - Cannot pass through\n")
    f.write("  G = Goal  (type 3) - Vault with the flag\n\n")
    
    f.write(f"Levels with paths: {interesting}\n\n")
    
    # Write all levels
    for z in range(20):
        f.write("\n" + "="*60 + "\n")
        f.write(f" Z-Level {z:2d} (Vertical Position)\n")
        f.write("="*60 + "\n")
        f.write("   ")
        for y in range(20):
            f.write(f"{y%10} ")
        f.write("\n")
        
        for x in range(20):
            f.write(f"{x:2d} ")
            for y in range(20):
                cell_type = maze.get(z, {}).get(x, {}).get(y, 2)
                char = get_cell_char(cell_type)
                f.write(char + " ")
            f.write("\n")

print("Done! Maze visualization saved to maze_visualization.txt")

# Also generate a summary of interesting levels only
print("\nGenerating maze_paths_only.txt (interesting levels only)...")
with open('maze_paths_only.txt', 'w', encoding='utf-8') as f:
    f.write("="*60 + "\n")
    f.write(" MAZE LEVELS WITH PATHS - Tunnel Challenge\n")
    f.write("="*60 + "\n\n")
    
    f.write("Legend: S=Start  .=Path  #=Wall  G=Goal\n\n")
    
    for z in interesting:
        f.write("\n" + "="*60 + "\n")
        f.write(f" Z-Level {z:2d}\n")
        f.write("="*60 + "\n")
        f.write("   ")
        for y in range(20):
            f.write(f"{y%10} ")
        f.write("\n")
        
        for x in range(20):
            f.write(f"{x:2d} ")
            for y in range(20):
                cell_type = maze.get(z, {}).get(x, {}).get(y, 2)
                char = get_cell_char(cell_type)
                f.write(char + " ")
            f.write("\n")

print("Done! Interesting levels saved to maze_paths_only.txt")
print("\nYou can now open these files to see the maze structure!")
