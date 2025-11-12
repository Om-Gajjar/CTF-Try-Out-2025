#!/usr/bin/env python3
from pwn import *

def solve_min_path(rows, cols, grid):
    dp = [[float('inf')] * cols for _ in range(rows)]
    dp[0][0] = grid[0][0]
    
    for j in range(1, cols):
        dp[0][j] = dp[0][j-1] + grid[0][j]
    
    for i in range(1, rows):
        dp[i][0] = dp[i-1][0] + grid[i][0]
    
    for i in range(1, rows):
        for j in range(1, cols):
            dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])
    
    return dp[rows-1][cols-1]

conn = remote('94.237.49.128', 52257)

# Read initial prompt
conn.recvuntil(b'Test 1/100\n')

for test in range(1, 101):
    log.info(f"Test {test}/100")
    
    # Read dimensions
    dims = conn.recvline().decode().strip()
    rows, cols = map(int, dims.split())
    log.info(f"Dimensions: {rows}x{cols}")
    
    # Read values
    values = conn.recvline().decode().strip()
    nums = list(map(int, values.split()))
    
    # Build grid
    grid = []
    idx = 0
    for i in range(rows):
        row = []
        for j in range(cols):
            row.append(nums[idx])
            idx += 1
        grid.append(row)
    
    # Solve
    result = solve_min_path(rows, cols, grid)
    log.success(f"Answer: {result}")
    
    # Send answer
    conn.sendline(str(result).encode())
    
    # Check response
    response = conn.recvline(timeout=2).decode()
    log.info(response.strip())
    
    if 'HTB{' in response:
        log.success(f"FLAG: {response}")
        break
    elif 'wrong' in response.lower() or 'caught' in response.lower():
        log.error("Wrong answer!")
        break

conn.interactive()
conn.close()
