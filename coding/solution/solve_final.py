#!/usr/bin/env python3
import socket

def solve_min_path(rows, cols, grid):
    dp = [[0] * cols for _ in range(rows)]
    dp[0][0] = grid[0][0]
    
    for j in range(1, cols):
        dp[0][j] = dp[0][j-1] + grid[0][j]
    
    for i in range(1, rows):
        dp[i][0] = dp[i-1][0] + grid[i][0]
    
    for i in range(1, rows):
        for j in range(1, cols):
            dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])
    
    return dp[rows-1][cols-1]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('94.237.49.128', 52257))
f = sock.makefile('rw', buffering=1)

# Read header
while True:
    line = f.readline()
    print(line, end='')
    if 'Test 1/100' in line:
        break

for test in range(1, 101):
    print(f"\n=== Test {test}/100 ===")
    
    # Read dimensions (skip any Test x/100 lines)
    dims_line = f.readline().strip()
    while dims_line.startswith('Test') or dims_line == '':
        dims_line = f.readline().strip()
    rows, cols = map(int, dims_line.split())
    
    # Read values
    values_line = f.readline().strip()
    nums = list(map(int, values_line.split()))
    
    # Build grid
    grid = [[nums[i * cols + j] for j in range(cols)] for i in range(rows)]
    
    # Solve
    result = solve_min_path(rows, cols, grid)
    print(f"{rows}x{cols} -> Answer: {result}")
    
    # Send answer
    f.write(f"{result}\n")
    f.flush()
    
    # Read response
    response = f.readline()
    print(f"Response: {response.strip()}")
    
    if 'HTB{' in response:
        print(f"\n===FLAG: {response}===")
        break
    if 'wrong' in response.lower() or 'caught' in response.lower():
        print("Wrong answer!")
        break

f.close()
sock.close()
