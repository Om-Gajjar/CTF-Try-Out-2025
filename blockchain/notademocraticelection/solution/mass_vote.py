#!/usr/bin/env python3
import subprocess
import sys

TARGET_CONTRACT = "0x19DD9425Aae45D29a5dAf219e390FfeeF24d72CD"
PRIVATE_KEY = "0x43a2d7b9e13653df0e42543559fc5b048e3adc0a2036344e5d0afaf3b039d90b"
RPC = "http://83.136.251.67:32011/"

# Vote 2000 times to be sure
total_votes = 2000

print(f"Voting {total_votes} times for CIM...")
print("This may take a few minutes...")

for i in range(1, total_votes + 1):
    if i % 50 == 0:
        print(f"Progress: {i}/{total_votes} votes sent...")
        sys.stdout.flush()
    
    cmd = [
        "cast", "send", TARGET_CONTRACT,
        "vote(bytes3,string,string)",
        "0x43494d", "A", "B",
        "--private-key", PRIVATE_KEY,
        "--rpc-url", RPC,
        "--gas-limit", "100000",
        "--legacy"
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, timeout=10, check=False)
    except Exception as e:
        if i % 50 == 0:
            print(f"Warning: {e}")
        continue

print("\n✓ Voting complete!")
print("\nChecking final votes...")

# Check votes
cmd = ["cast", "call", TARGET_CONTRACT, "getVotesCount(bytes3)(uint256)", "0x43494d", "--rpc-url", RPC]
result = subprocess.run(cmd, capture_output=True, text=True)
votes = result.stdout.strip()
print(f"CIM votes: {votes}")

# Check winner
cmd = ["cast", "call", TARGET_CONTRACT, "winner()(bytes3)", "--rpc-url", RPC]
result = subprocess.run(cmd, capture_output=True, text=True)
winner = result.stdout.strip()
print(f"Winner: {winner}")

if "43494d" in winner.lower():
    print("\n🎉 SUCCESS! CIM is the winner!")
else:
    print("\n⚠ Winner is not CIM yet")
