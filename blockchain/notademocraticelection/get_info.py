#!/usr/bin/env python3
import socket
import time
import json
import sys

def interact_with_server(host, port):
    """Connect to the challenge server and get credentials"""
    print(f"Connecting to {host}:{port}...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        sock.connect((host, port))
        print("Connected!")
        
        # Read initial menu
        time.sleep(1)
        data = sock.recv(4096).decode('utf-8', errors='ignore')
        print("Received:")
        print(data)
        
        # Send option 1 to get connection info
        print("\nSending option 1...")
        sock.send(b"1\n")
        time.sleep(2)
        
        # Read response
        response = sock.recv(8192).decode('utf-8', errors='ignore')
        print("Response:")
        print(response)
        
        # Parse the response to extract key info
        lines = response.split('\n')
        private_key = None
        setup_addr = None
        target_addr = None
        rpc_url = None
        
        for line in lines:
            if 'private key' in line.lower() or '0x' in line:
                # Try to extract addresses
                parts = line.split()
                for part in parts:
                    if part.startswith('0x') and len(part) == 66:
                        if private_key is None:
                            private_key = part
                    elif part.startswith('0x') and len(part) == 42:
                        if 'setup' in line.lower() or 'Setup' in line:
                            setup_addr = part
                        elif 'target' in line.lower() or 'TARGET' in line:
                            target_addr = part
            if 'http' in line.lower():
                parts = line.split()
                for part in parts:
                    if part.startswith('http'):
                        rpc_url = part.rstrip('.,;')
        
        return {
            'private_key': private_key,
            'setup': setup_addr,
            'target': target_addr,
            'rpc': rpc_url,
            'raw_response': response
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        sock.close()

def main():
    host = "94.237.62.103"
    port = 34182
    
    info = interact_with_server(host, port)
    
    if info:
        print("\n" + "="*60)
        print("EXTRACTED INFO:")
        print("="*60)
        print(f"Private Key: {info.get('private_key', 'NOT FOUND')}")
        print(f"Setup Address: {info.get('setup', 'NOT FOUND')}")
        print(f"Target Address: {info.get('target', 'NOT FOUND')}")
        print(f"RPC URL: {info.get('rpc', 'NOT FOUND')}")
        print("="*60)
        
        # Save to file for later use
        with open('challenge_info.json', 'w') as f:
            json.dump(info, f, indent=2)
        print("\nSaved to challenge_info.json")
    else:
        print("Failed to get info from server")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
