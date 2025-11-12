#!/usr/bin/env python3
"""
Create a combined view of the maze showing the path through all levels
"""

import re

def parse_maze_data(filename):
    """Parse maze_data.c and extract cell information"""
    maze = {}
    
    with open(filename, 'r') as f:
        content = f.read()
    
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

# Parse maze
print("Parsing maze data...")
maze = parse_maze_data('maze_data.c')

# Create combined view showing only cells with paths
print("Creating combined view...")

with open('maze_combined.txt', 'w', encoding='utf-8') as f:
    f.write("="*80 + "\n")
    f.write(" COMBINED 3D MAZE VIEW - All Paths Shown Together\n")
    f.write("="*80 + "\n\n")
    
    f.write("Legend: S=Start  .=Path  #=Wall  G=Goal  (space)=Wall on all levels\n")
    f.write("This view shows what the maze looks like if you collapse all Z-levels.\n")
    f.write("A '.' means there's a path at ANY z-level at that (x,y) position.\n\n")
    
    # Create a 2D projection showing if there's a path at any Z level
    f.write("="*80 + "\n")
    f.write(" 2D PROJECTION: Path exists at (x,y) on ANY z-level\n")
    f.write("="*80 + "\n")
    f.write("   ")
    for y in range(20):
        f.write(f"{y%10} ")
    f.write("\n")
    
    for x in range(20):
        f.write(f"{x:2d} ")
        for y in range(20):
            has_path = False
            cell_char = ' '
            
            # Check all z-levels for this x,y position
            for z in range(20):
                cell_type = maze.get(z, {}).get(x, {}).get(y, 2)
                if cell_type == 0:  # Start
                    cell_char = 'S'
                    has_path = True
                    break
                elif cell_type == 3:  # Goal
                    cell_char = 'G'
                    has_path = True
                    break
                elif cell_type == 1:  # Path
                    has_path = True
                    cell_char = '.'
            
            if not has_path:
                cell_char = '#'
            
            f.write(cell_char + " ")
        f.write("\n")
    
    # Now create a side view (X-Z plane, Y fixed)
    f.write("\n\n" + "="*80 + "\n")
    f.write(" SIDE VIEW (X-Z plane, showing multiple Y slices)\n")
    f.write("="*80 + "\n\n")
    
    # Show a few interesting Y slices
    interesting_y = [0, 1, 5, 10, 12, 18, 19]
    
    for y_slice in interesting_y:
        has_any_path = False
        # Check if this Y slice has any paths
        for z in range(20):
            for x in range(20):
                cell_type = maze.get(z, {}).get(x, {}).get(y_slice, 2)
                if cell_type in [0, 1, 3]:
                    has_any_path = True
                    break
            if has_any_path:
                break
        
        if not has_any_path:
            continue
            
        f.write(f"\nY-slice {y_slice:2d} (X=rows, Z=columns):\n")
        f.write("    ")
        for z in range(20):
            f.write(f"{z%10} ")
        f.write("\n")
        
        for x in range(20):
            f.write(f"{x:2d}  ")
            for z in range(20):
                cell_type = maze.get(z, {}).get(x, {}).get(y_slice, 2)
                cell_char = get_cell_char(cell_type)
                f.write(cell_char + " ")
            f.write("\n")
    
    # Create a vertical view (Y-Z plane, X fixed)
    f.write("\n\n" + "="*80 + "\n")
    f.write(" VERTICAL VIEW (Y-Z plane, showing multiple X slices)\n")
    f.write("="*80 + "\n\n")
    
    interesting_x = [0, 1, 6, 9, 12, 17, 19]
    
    for x_slice in interesting_x:
        has_any_path = False
        # Check if this X slice has any paths
        for z in range(20):
            for y in range(20):
                cell_type = maze.get(z, {}).get(x_slice, {}).get(y, 2)
                if cell_type in [0, 1, 3]:
                    has_any_path = True
                    break
            if has_any_path:
                break
        
        if not has_any_path:
            continue
            
        f.write(f"\nX-slice {x_slice:2d} (Y=rows, Z=columns):\n")
        f.write("    ")
        for z in range(20):
            f.write(f"{z%10} ")
        f.write("\n")
        
        for y in range(20):
            f.write(f"{y:2d}  ")
            for z in range(20):
                cell_type = maze.get(z, {}).get(x_slice, {}).get(y, 2)
                cell_char = get_cell_char(cell_type)
                f.write(cell_char + " ")
            f.write("\n")
    
    # Create an isometric-style view
    f.write("\n\n" + "="*80 + "\n")
    f.write(" PATH SUMMARY: List of all path coordinates\n")
    f.write("="*80 + "\n\n")
    
    path_cells = []
    for z in range(20):
        for x in range(20):
            for y in range(20):
                cell_type = maze.get(z, {}).get(x, {}).get(y, 2)
                if cell_type in [0, 1, 3]:
                    char = get_cell_char(cell_type)
                    path_cells.append((x, y, z, char))
    
    f.write(f"Total path cells: {len(path_cells)}\n\n")
    f.write("Format: (X, Y, Z) Type\n\n")
    
    for x, y, z, char in sorted(path_cells, key=lambda c: (c[2], c[0], c[1])):
        type_name = {'S': 'START', '.': 'PATH', 'G': 'GOAL'}[char]
        f.write(f"({x:2d}, {y:2d}, {z:2d}) {char} {type_name:5s}")
        if char == 'S':
            f.write(" <-- Starting position")
        elif char == 'G':
            f.write(" <-- Goal/Vault")
        f.write("\n")

print("Done! Combined view saved to maze_combined.txt")
