#!/usr/bin/env python3
"""
Find the path from Start (S) to Goal (G) in the 3D maze
"""

import re
from collections import deque

def parse_maze_data(filename):
    """Parse maze_data.c and extract cell information"""
    maze = {}
    start = None
    goal = None
    
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
        
        if cell_type == 0:  # Start
            start = (x, y, z)
        elif cell_type == 3:  # Goal
            goal = (x, y, z)
    
    return maze, start, goal

def can_move(maze, x, y, z):
    """Check if position is valid and not a wall"""
    if not (0 <= x < 20 and 0 <= y < 20 and 0 <= z < 20):
        return False
    cell_type = maze.get(z, {}).get(x, {}).get(y, 2)
    return cell_type != 2  # Not a wall

def bfs_find_path(maze, start, goal):
    """Find shortest path using BFS"""
    queue = deque([(start, [])])
    visited = {start}
    
    while queue:
        (x, y, z), path = queue.popleft()
        
        if (x, y, z) == goal:
            return path
        
        # Try all 6 directions
        moves = [
            (x+1, y, z, 'F'),  # Forward
            (x-1, y, z, 'B'),  # Backward
            (x, y+1, z, 'R'),  # Right
            (x, y-1, z, 'L'),  # Left
            (x, y, z+1, 'U'),  # Up
            (x, y, z-1, 'D'),  # Down
        ]
        
        for nx, ny, nz, direction in moves:
            if (nx, ny, nz) not in visited and can_move(maze, nx, ny, nz):
                visited.add((nx, ny, nz))
                queue.append(((nx, ny, nz), path + [direction]))
    
    return None

def print_path_visualization(maze, start, goal, path):
    """Print the path with coordinates"""
    print("\n" + "="*60)
    print(" SOLUTION PATH")
    print("="*60)
    
    x, y, z = start
    print(f"\nStart: ({x}, {y}, {z})")
    print(f"Goal:  {goal}")
    print(f"\nPath length: {len(path)} moves")
    print("\nMoves:")
    
    for i, move in enumerate(path, 1):
        # Update position
        if move == 'F':
            x += 1
        elif move == 'B':
            x -= 1
        elif move == 'R':
            y += 1
        elif move == 'L':
            y -= 1
        elif move == 'U':
            z += 1
        elif move == 'D':
            z -= 1
        
        direction_name = {
            'F': 'Forward', 'B': 'Backward',
            'R': 'Right', 'L': 'Left',
            'U': 'Up', 'D': 'Down'
        }[move]
        
        print(f"{i:3d}. {move} ({direction_name:8s}) -> ({x:2d}, {y:2d}, {z:2d})")
    
    print(f"\n{'='*60}")
    print("Solution string:")
    print(''.join(path))
    print("="*60)

# Main execution
print("Parsing maze data...")
maze, start, goal = parse_maze_data('maze_data.c')

print(f"Start position: {start}")
print(f"Goal position:  {goal}")

print("\nSearching for path...")
path = bfs_find_path(maze, start, goal)

if path:
    print(f"✓ Path found!")
    print_path_visualization(maze, start, goal, path)
    
    # Save to file
    with open('solution_path.txt', 'w') as f:
        f.write("MAZE SOLUTION\n")
        f.write("="*60 + "\n\n")
        f.write(f"Start: {start}\n")
        f.write(f"Goal:  {goal}\n")
        f.write(f"Path length: {len(path)} moves\n\n")
        f.write("Solution string:\n")
        f.write(''.join(path) + "\n\n")
        f.write("Legend: F=Forward, B=Backward, R=Right, L=Left, U=Up, D=Down\n")
    
    print("\n✓ Solution saved to solution_path.txt")
else:
    print("✗ No path found!")
