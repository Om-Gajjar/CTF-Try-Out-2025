#!/usr/bin/env python3
import socket
import re

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

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('94.237.49.128', 52257))
    
    # Read until first test
    buffer = ""
    while "Test 1/100" not in buffer:
        chunk = sock.recv(4096).decode('utf-8', errors='ignore')
        buffer += chunk
        print(chunk, end='', flush=True)
    
    for test in range(1, 101):
        print(f"\n=== Test {test}/100 ===", flush=True)
        
        # Read next lines
        line1 = ""
        while '\n' not in line1:
            line1 += sock.recv(1).decode('utf-8', errors='ignore')
        
        line2 = ""
        while '\n' not in line2:
            line2 += sock.recv(1).decode('utf-8', errors='ignore')
        
        dims = line1.strip()
        values = line2.strip()
        
        print(f"Dims: {dims}", flush=True)
        print(f"Values: {values[:50]}...", flush=True)
        
        rows, cols = map(int, dims.split())
        nums = list(map(int, values.split()))
        
        # Build grid
        grid = [[nums[i * cols + j] for j in range(cols)] for i in range(rows)]
        
        # Solve
        result = solve_min_path(rows, cols, grid)
        print(f"Answer: {result}", flush=True)
        
        # Send
        sock.sendall(f"{result}\n".encode())
        
        # Read response  
        response = ""
        while '>' not in response and 'HTB{' not in response:
            char = sock.recv(1).decode('utf-8', errors='ignore')
            if not char:
                break
            response += char
            if char == '\n':
                break
        
        print(f"Response: {response.strip()}", flush=True)
        
        if 'HTB{' in response:
            # Read rest
            rest = sock.recv(4096).decode('utf-8', errors='ignore')
            print(rest, flush=True)
            print(f"\n=== FLAG FOUND: {response} ===", flush=True)
            break
        elif 'wrong' in response.lower() or 'caught' in response.lower():
            print("ERROR: Wrong answer!", flush=True)
            break
    
    sock.close()

if __name__ == "__main__":
    main()
