#!/usr/bin/env python3
"""
Character CTF Challenge - Solution Script

This script extracts a flag character by character from a remote service
by querying sequential index positions.

Target: 83.136.255.235:56527
Category: Misc
"""

import socket
import time

# Target configuration
host = '83.136.255.235'
port = 56527

# State variables
flag = ''
index = 0

print("=" * 60)
print("Character CTF Challenge - Flag Extraction")
print("=" * 60)
print(f"Target: {host}:{port}")
print(f"Starting extraction...\n")

while True:
    try:
        # Connect to the service
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((host, port))
        conn.settimeout(5)
        
        # Receive the prompt
        data = conn.recv(1024).decode()
        print(f"Prompt: {data[:50]}...")
        
        # Send the index
        conn.sendall(f"{index}\n".encode())
        time.sleep(0.2)
        
        # Receive the response
        response = conn.recv(1024).decode()
        print(f"Response: {response[:100]}...")
        
        # Extract character from response
        if 'Character at Index' in response:
            # Parse "Character at Index X: Y"
            lines = response.split('\n')
            for line in lines:
                if 'Character at Index' in line:
                    char = line.split(':')[-1].strip()
                    if char:
                        flag += char
                        print(f"Index {index}: '{char}' -> Flag so far: {flag}")
                        index += 1
                        
                        # Stop if we've reached the closing brace
                        if char == '}':
                            print(f"\nComplete flag: {flag}")
                            conn.close()
                            exit(0)
                        break
            else:
                print("Could not parse character from response")
                break
        else:
            print("No 'Character at Index' found, assuming end of flag")
            break
        
        conn.close()
            
    except Exception as e:
        print(f"Error at index {index}: {e}")
        break

print(f"\nFinal flag: {flag}")
