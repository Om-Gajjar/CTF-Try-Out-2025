#!/bin/bash

# Challenge connection details
RPC_URL="http://94.237.62.103:52380"

echo "Connecting to challenge server..."
echo "RPC: $RPC_URL"

# Get setup contract address and private key from the server
# You'll need to interact with port 34182 to get these

echo ""
echo "=== EXPLOIT EXPLANATION ==="
echo "The vulnerability is in depositVoteCollateral():"
echo "- It checks uniqueness with: uniqueVoters[_name][_surname]"
echo "- But stores weight with: voters[abi.encodePacked(_name, _surname)]"
echo ""
echo "This means different (name, surname) pairs can map to the same voter signature!"
echo "Example: ('A', 'B') and ('AB', '') both produce voterSig 'AB'"
echo ""
echo "Exploit steps:"
echo "1. Deposit 500 ether as ('A', 'B')"
echo "2. Deposit 500 ether as ('AB', '') - bypasses uniqueness check!"
echo "3. Vote for CIM with ('A', 'B') - gets 1000 ether weight"
echo "4. CIM wins with 1000 ether >= 1000 ether target"
