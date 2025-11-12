#!/usr/bin/env python3
"""
Stop, Drop, and Roll CTF Challenge - Solution Script

This script solves an interactive scenario-based challenge where rapid
responses to emergency situations are required.

Target: 94.237.55.38:58034
Category: Misc

Scenario Mappings:
- GORGE -> STOP
- PHREAK -> DROP
- FIRE -> ROLL
"""

import socket

# Target configuration
host = '94.237.55.38'
port = 58034

print("=" * 60)
print("Stop, Drop, and Roll - CTF Challenge Solver")
print("=" * 60)
print(f"Target: {host}:{port}")
print("Scenario Mappings: GORGE->STOP, PHREAK->DROP, FIRE->ROLL")
print("=" * 60)
print()

conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect((host, port))

# Receive until we see the question
data = b""
while b'(y/n)' not in data:
    chunk = conn.recv(1024)
    if not chunk:
        break
    data += chunk

print(data.decode())

# Send 'y' to start
conn.sendall(b'y\n')

# Mapping rules
mapping = {
    'GORGE': 'STOP',
    'PHREAK': 'DROP',
    'FIRE': 'ROLL'
}

try:
    while True:
        # Receive data
        data = b""
        while b'What do you do?' not in data:
            chunk = conn.recv(1024)
            if not chunk:
                print("Connection closed")
                break
            data += chunk
        
        decoded = data.decode()
        print(decoded)
        
        # Extract the line with the scenarios
        lines = decoded.strip().split('\n')
        scenario_line = None
        for line in lines:
            if any(word in line for word in ['GORGE', 'PHREAK', 'FIRE']):
                scenario_line = line.strip()
                break
        
        if scenario_line:
            # Parse the scenarios
            scenarios = [s.strip() for s in scenario_line.split(',')]
            
            # Map to responses
            responses = [mapping[s] for s in scenarios if s in mapping]
            
            # Join with hyphen
            response = '-'.join(responses)
            
            print(f"Sending: {response}")
            conn.sendall(response.encode() + b'\n')
        else:
            print("Could not find scenario line")
            break
            
except Exception as e:
    print(f"Error: {e}")
    # Try to receive any remaining data
    conn.settimeout(2)
    try:
        remaining = conn.recv(4096)
        print(remaining.decode())
    except:
        pass

conn.close()
