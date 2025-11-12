#!/usr/bin/env python3
"""
3D Maze Visualizer for Tunnel Challenge
Reads maze_data.c and generates visual representations of each Z-level
"""

import re
import os

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
    if cell_type == 0:
        return 'S'  # Start
    elif cell_type == 1:
        return '.'  # Path
    elif cell_type == 2:
        return '#'  # Wall
    elif cell_type == 3:
        return 'G'  # Goal
    else:
        return '?'

def get_cell_color(cell_type):
    """Get ANSI color code for cell type"""
    if cell_type == 0:
        return '\033[92m'  # Green for start
    elif cell_type == 1:
        return '\033[97m'  # White for path
    elif cell_type == 2:
        return '\033[90m'  # Dark gray for wall
    elif cell_type == 3:
        return '\033[93m'  # Yellow for goal
    else:
        return '\033[0m'

def print_level(maze, z, use_color=True):
    """Print a single Z-level of the maze"""
    reset = '\033[0m' if use_color else ''
    
    print(f"\n{'='*44}")
    print(f" Z-Level {z:2d}")
    print(f"{'='*44}")
    print("  ", end="")
    for y in range(20):
        print(f"{y%10}", end=" ")
    print()
    
    for x in range(20):
        print(f"{x:2d} ", end="")
        for y in range(20):
            cell_type = maze.get(z, {}).get(x, {}).get(y, 2)
            char = get_cell_char(cell_type)
            
            if use_color:
                color = get_cell_color(cell_type)
                print(f"{color}{char}{reset}", end=" ")
            else:
                print(char, end=" ")
        print()

def find_interesting_levels(maze):
    """Find Z-levels that have paths or goals (not just walls)"""
    interesting = []
    
    for z in sorted(maze.keys()):
        has_path = False
        for x in maze[z]:
            for y in maze[z][x]:
                if maze[z][x][y] in [0, 1, 3]:  # Start, path, or goal
                    has_path = True
                    break
            if has_path:
                break
        
        if has_path:
            interesting.append(z)
    
    return interesting

def print_summary(maze):
    """Print summary statistics"""
    total_cells = 0
    type_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    
    for z in maze:
        for x in maze[z]:
            for y in maze[z][x]:
                cell_type = maze[z][x][y]
                type_counts[cell_type] = type_counts.get(cell_type, 0) + 1
                total_cells += 1
    
    print("\n" + "="*44)
    print(" MAZE STATISTICS")
    print("="*44)
    print(f"Total cells: {total_cells}")
    print(f"Start cells (S): {type_counts.get(0, 0)}")
    print(f"Path cells  (.): {type_counts.get(1, 0)}")
    print(f"Wall cells  (#): {type_counts.get(2, 0)}")
    print(f"Goal cells  (G): {type_counts.get(3, 0)}")
    print("\nLegend:")
    print("  S = Start (type 0)")
    print("  . = Path  (type 1)")
    print("  # = Wall  (type 2)")
    print("  G = Goal  (type 3)")

def save_to_file(maze, output_file):
    """Save maze visualization to a text file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        # Summary
        f.write("="*44 + "\n")
        f.write(" 3D MAZE VISUALIZATION\n")
        f.write("="*44 + "\n\n")
        
        f.write("Legend:\n")
        f.write("  S = Start (type 0)\n")
        f.write("  . = Path  (type 1)\n")
        f.write("  # = Wall  (type 2)\n")
        f.write("  G = Goal  (type 3)\n\n")
        
        # Find interesting levels
        interesting = find_interesting_levels(maze)
        f.write(f"Levels with paths: {interesting}\n\n")
        
        # Print all levels
        for z in range(20):
            f.write("\n" + "="*44 + "\n")
            f.write(f" Z-Level {z:2d}\n")
            f.write("="*44 + "\n")
            f.write("  ")
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

def main():
    maze_file = 'maze_data.c'
    
    if not os.path.exists(maze_file):
        print(f"Error: {maze_file} not found!")
        return
    
    print("Parsing maze data...")
    maze = parse_maze_data(maze_file)
    
    print_summary(maze)
    
    # Find levels with actual paths
    interesting = find_interesting_levels(maze)
    print(f"\nLevels with paths or goals: {interesting}")
    
    # Display options
    print("\n" + "="*44)
    print("DISPLAY OPTIONS")
    print("="*44)
    print("1. Show all levels (0-19)")
    print("2. Show only interesting levels")
    print("3. Show specific level")
    print("4. Save all levels to file")
    print("5. Exit")
    
    while True:
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            for z in range(20):
                print_level(maze, z)
                if z < 19:
                    input("\nPress Enter for next level...")
        
        elif choice == '2':
            for z in interesting:
                print_level(maze, z)
                if z != interesting[-1]:
                    input("\nPress Enter for next level...")
        
        elif choice == '3':
            try:
                z = int(input("Enter Z-level (0-19): "))
                if 0 <= z <= 19:
                    print_level(maze, z)
                else:
                    print("Invalid level! Must be 0-19")
            except ValueError:
                print("Invalid input!")
        
        elif choice == '4':
            output_file = 'maze_visualization.txt'
            print(f"Saving to {output_file}...")
            save_to_file(maze, output_file)
            print(f"Done! Visualization saved to {output_file}")
        
        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice!")

if __name__ == '__main__':
    main()
