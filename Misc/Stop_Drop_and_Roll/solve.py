#!/usr/bin/env python3

import socket

# Connect to the server
host = '94.237.55.38'
port = 58034

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
