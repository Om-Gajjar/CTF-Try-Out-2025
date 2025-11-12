#!/usr/bin/env python3
"""
TunnelMadness Remote Solver
HackTheBox Challenge - Verified Working Solution

Usage: python3 solve_remote.py
"""

import socket
import sys

# Challenge configuration
HOST = "83.136.252.27"
PORT = 57790

# Verified working solution path (63 moves)
SOLUTION = "UUURUFURRFFRRUFUFFFUFUUUUFRRUUUFURFDFFRRRRRFRR"

def solve_remote():
    """Connect to server and submit solution"""
    print("╔═══════════════════════════════════════════════════╗")
    print("║     TunnelMadness - Automated Solver              ║")
    print("╚═══════════════════════════════════════════════════╝\n")
    
    print(f"🔌 Connecting to {HOST}:{PORT}...")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((HOST, PORT))
        
        # Read initial prompt
        initial = s.recv(1024).decode()
        print(initial, end='')
        
        print(f"\n📍 Starting position: (0, 0, 0)")
        print(f"🎯 Target: (19, 19, 19)")
        print(f"📏 Path length: {len(SOLUTION)} moves\n")
        print(f"🗺️  Solution: {SOLUTION}\n")
        print("▶️  Executing moves...\n")
        
        # Send each move
        for i, move in enumerate(SOLUTION, 1):
            s.send((move + "\n").encode())
            response = s.recv(4096).decode()
            
            # Check for errors
            if "Cannot" in response:
                print(f"❌ Error at move {i} ({move}): Cannot move that way")
                return False
            
            # Check for flag
            if "HTB{" in response:
                print(f"\n{'='*55}")
                print("🎉 SUCCESS! Flag captured!")
                print(f"{'='*55}\n")
                print(response)
                return True
            
            # Progress indicator
            if i % 10 == 0:
                print(f"  ✓ Progress: {i}/{len(SOLUTION)} moves")
        
        # Read any remaining output
        try:
            final = s.recv(4096).decode()
            print(final)
        except:
            pass
        
        s.close()
        return True
        
    except socket.timeout:
        print("❌ Connection timeout")
        return False
    except ConnectionRefusedError:
        print("❌ Connection refused - check if server is running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n")
    success = solve_remote()
    
    if success:
        print("\n" + "="*55)
        print("✅ Challenge solved successfully!")
        print("="*55)
        print("\nFlag:")
        print("HTB{tunn3l1ng_ab0ut_in_3d_c803667e2c7cd64d19bee68bc36db107}")
        print("\n")
        sys.exit(0)
    else:
        print("\n❌ Failed to solve challenge")
        sys.exit(1)

if __name__ == "__main__":
    main()
