#!/usr/bin/env python3
import socket
import time

def solve_min_path(rows, cols, grid):
    """
    Find minimum path sum from top-left to bottom-right.
    Can only move right or down.
    """
    # Create DP table
    dp = [[0] * cols for _ in range(rows)]
    
    # Initialize first cell
    dp[0][0] = grid[0][0]
    
    # Fill first row (can only come from left)
    for j in range(1, cols):
        dp[0][j] = dp[0][j-1] + grid[0][j]
    
    # Fill first column (can only come from top)
    for i in range(1, rows):
        dp[i][0] = dp[i-1][0] + grid[i][0]
    
    # Fill rest of the table
    for i in range(1, rows):
        for j in range(1, cols):
            dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])
    
    return dp[rows-1][cols-1]

def main():
    HOST = '94.237.49.128'
    PORT = 52257
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.settimeout(5)
    
    buffer = ""
    
    # Receive initial message
    while ">" not in buffer:
        chunk = sock.recv(4096).decode('utf-8', errors='ignore')
        buffer += chunk
        print(chunk, end='', flush=True)
    
    # Process 100 test cases
    for test_num in range(1, 101):
        print(f"\n=== Processing Test {test_num}/100 ===", flush=True)
        
        # Parse what's already in buffer after ">"
        lines = buffer.split('\n')
        
        # Find dimensions and values
        dims_line = None
        values_line = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not any(x in line for x in ['Test', 'Example', 'grid', '>', 'Optimal']):
                parts = line.split()
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    dims_line = line
                    if i + 1 < len(lines):
                        values_line = lines[i + 1].strip()
                    break
        
        if not dims_line or not values_line:
            # Need to read more
            buffer = ""
            chunk = sock.recv(4096).decode('utf-8', errors='ignore')
            buffer += chunk
            lines = buffer.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if line and not any(x in line for x in ['Test', 'Example', 'grid', '>', 'Optimal']):
                    parts = line.split()
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        dims_line = line
                        if i + 1 < len(lines):
                            values_line = lines[i + 1].strip()
                        break
        
        print(f"Dimensions: {dims_line}", flush=True)
        rows, cols = map(int, dims_line.split())
        
        print(f"Values: {values_line}", flush=True)
        nums = list(map(int, values_line.split()))
        
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
        print(f"Answer: {result}", flush=True)
        
        # Send answer
        sock.sendall(f"{result}\n".encode())
        
        # Read response
        buffer = ""
        try:
            while ">" not in buffer and "HTB{" not in buffer:
                chunk = sock.recv(4096).decode('utf-8', errors='ignore')
                if not chunk:
                    break
                buffer += chunk
                print(chunk, end='', flush=True)
                if "HTB{" in chunk:
                    break
        except socket.timeout:
            pass
        
        # Check for flag
        if "HTB{" in buffer:
            print("\n=== FLAG FOUND ===")
            break
    
    sock.close()

if __name__ == "__main__":
    main()
