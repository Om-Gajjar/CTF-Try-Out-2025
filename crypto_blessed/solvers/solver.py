#!/usr/bin/env python3
"""
Blessed CTF Challenge - Complete Solver
========================================

This script exploits three cryptographic vulnerabilities to authenticate as a "blessed" robot:
1. BLS Rogue Key Attack - Forge aggregated signatures without knowing the server's secret
2. EC-LCG PRNG Crack - Recover PRNG state using lattice reduction (LLL algorithm)
3. ZKP Cheating - Pass 64 rounds of zero-knowledge proof using predicted challenge bits

Author: Om Gajjar (with GitHub Copilot assistance)
Challenge: HackTheBox - Blessed (Hard, 1000 points)
Status: ✅ Solved
Flag: HTB{uNv31leD_5eCre7s_0f_BLS_r0gu3_k3y_4t7aCk_w1th_cu5t0m_zkp_4nd_ec-lcg!!_8a843007ff4c20838af600a77a14533e}

Usage:
    python solver.py                                    # Connect to default CTF server
    CTF_HOST=<ip> CTF_PORT=<port> python solver.py    # Connect to custom server
    DEBUG=1 python solver.py                            # Enable debug mode
"""

import json
import time

from functools import reduce
from pwn import process, sys, remote, log

# BLS signature operations (for Phase 1: Signature Forgery)
from py_ecc.bls.ciphersuites import G2ProofOfPossession as bls
from py_ecc.bls.g2_primitives import G1_to_pubkey, pubkey_to_G1
from py_ecc.bls.point_compression import decompress_G1
from py_ecc.bls.typing import G1Compressed

# Elliptic curve operations (for all phases)
from py_ecc.optimized_bls12_381.optimized_curve import add, G1, multiply, neg, normalize, Z1

# SageMath for lattice reduction (for Phase 2: PRNG Crack)
from sage.all import EllipticCurve, GF, identity_matrix, PolynomialRing, Sequence, zero_matrix, ZZ


def get_process():
    """
    Establish connection to the CTF server.
    
    Environment Variables:
        CTF_HOST: Server IP address (default: 83.136.253.5)
        CTF_PORT: Server port (default: 47445)
        DEBUG: Set to '1' or 'true' to enable raw protocol debugging
    
    Returns:
        pwntools remote connection object
    
    Raises:
        Exception: If connection fails
    """
    import os
    host = os.getenv('CTF_HOST', '83.136.253.5')
    port = int(os.getenv('CTF_PORT', '47445'))
    
    log.info(f"Connecting to {host}:{port}...")
    try:
        conn = remote(host, port, timeout=30)
        # Enable debug mode to see raw responses
        if os.getenv('DEBUG', '').lower() in ['1', 'true']:
            conn.debug()
        return conn
    except Exception as e:
        log.failure(f"Connection failed: {e}")
        log.info("If the server is down, you can test locally by running server.py")
        log.info("Then run: CTF_HOST=127.0.0.1 CTF_PORT=<port> python solver.py")
        raise


def sr(data):
    """
    Send JSON request and receive JSON response from server.
    
    Args:
        data: Dictionary to send as JSON
    
    Returns:
        Parsed JSON response from server
    """
    io.sendlineafter(b'> ', json.dumps(data).encode())
    return json.loads(io.recvline().decode())


# ============================================================================
# Elliptic Curve Parameters (P-256 / secp256r1)
# ============================================================================
# These parameters define the elliptic curve used by the EC-LCG PRNG
# Curve equation: y² = x³ + ax + b (mod p)

p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff  # Prime modulus
K = GF(p)  # Finite field
a = K(0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc)  # Curve parameter a
b = K(0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b)  # Curve parameter b
E = EllipticCurve(K, (a, b))  # Define the curve

# Generator point G
G = E(0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296, 
      0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)

# Set curve order
E.set_order(0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551 * 0x1)


def crack_ec_lcg(values):
    """
    Phase 2: Crack the EC-LCG PRNG using lattice reduction.
    
    The server uses an Elliptic Curve Linear Congruential Generator (EC-LCG)
    defined by: W[n+1] = a * W[n] where a is a secret multiplier.
    
    We only observe the x-coordinates (upper 32 bits of robot IDs), but we can:
    1. Recover full points using the curve equation
    2. Build a lattice that encodes the EC-LCG relationships
    3. Use LLL algorithm to find short vectors revealing the multiplier
    4. Predict all future PRNG outputs
    
    Args:
        values: List of 6 observed x-coordinates (upper 32 bits of robot IDs)
    
    Returns:
        W3: The recovered PRNG state point, allowing future predictions
    
    Algorithm:
        - Builds a lattice based on the hidden number problem
        - Uses LLL (Lenstra-Lenstra-Lovász) algorithm to find short basis
        - Extracts the EC-LCG multiplier from the reduced lattice
    """
    assert len(values) == 6, "Need exactly 6 samples to crack EC-LCG"
    
    # Split observed coordinates into pairs
    u1, v1, u2, v2, u3, v3 = values
    
    # Create polynomial ring for the unknown offsets
    # We're recovering the y-coordinates which differ from observed by small offsets
    a1, b1, a2, b2, a3, b3 = PolynomialRing(K, 'a1, b1, a2, b2, a3, b3').gens()

    # Constraint 1-3: Points must lie on the curve
    # y² = x³ + ax + b for each point
    ec1 = (v1 + b1) ** 2 - (u1 + a1) ** 3 - a * (u1 + a1) - b
    ec2 = (v2 + b2) ** 2 - (u2 + a2) ** 3 - a * (u2 + a2) - b
    ec3 = (v3 + b3) ** 2 - (u3 + a3) ** 3 - a * (u3 + a3) - b

    # Constraint 4-5: EC-LCG relationship W[i+1] = a * W[i]
    # These encode the addition formulas on elliptic curves
    ec4 = ((u1 + a1) + (u2 + a2) + G.x()) * ((u2 + a2) - (u1 + a1)) ** 2 - ((v2 + b2) + (v1 + b1)) ** 2
    ec5 = ((u2 + a2) + (u3 + a3) + G.x()) * ((u3 + a3) - (u2 + a2)) ** 2 - ((v3 + b3) + (v2 + b2)) ** 2
    
    # Constraint 6-7: Initial condition W[0] = G (generator point)
    ec6 = (G.y() - (v1 + b1)) * ((u2 + a2) - (u1 + a1)) - ((v2 + b2) + (v1 + b1)) * ((u1 + a1) - G.x())
    ec7 = (G.y() - (v2 + b2)) * ((u3 + a3) - (u2 + a2)) - ((v3 + b3) + (v2 + b2)) * ((u2 + a2) - G.x())

    # Build coefficient matrix from polynomial system
    A, v = Sequence([ec1, ec2, ec3, ec4, ec5, ec6, ec7]).coefficients_monomials(sparse=False)
    A = A.change_ring(ZZ)  # Convert to integer ring

    # Construct lattice basis matrix
    # Upper part: scaled identity matrix (modular reduction)
    # Lower part: coefficient matrix with scaling
    A = (identity_matrix(7) * p).augment(A)
    A = A.stack(zero_matrix(len(v), 7).augment(identity_matrix(len(v))))
    A[-1, -1] = 2 ** 256  # Add scaling factor for better LLL performance

    # Apply LLL algorithm to find short vectors
    L = A.T.LLL()
    
    # Extract solution from shortest vector
    assert L[-1][-1] == 2 ** 256, "LLL didn't converge properly"
    a1, b1, a2, b2, a3, b3 = L[-1][-7:-1]

    # Recover the actual EC points
    W1 = E(u1 + a1, v1 + b1)
    W2 = E(u2 + a2, v2 + b2)
    W3 = E(u3 + a3, v3 + b3)
    
    # Return the latest state for future predictions
    return W3


# ============================================================================
# MAIN EXECUTION
# ============================================================================

# Establish connection to CTF server
io = get_process()

# ----------------------------------------------------------------------------
# Phase 1: BLS Signature Forgery (Rogue Key Attack)
# ----------------------------------------------------------------------------
log.info("Phase 1: BLS Signature Forgery")

# Step 1: Create our own robot and get initial credentials
res = sr({'cmd': 'create'})
sk = int(res.get('sk'), 16)  # Our secret key
robot_id = int(res.get('robot_id'), 16)  # Our robot ID

# Step 2: List all existing robots to collect their public keys
cmd = 'list'
sig = bls.Sign(sk, cmd.encode())  # Sign the list command
res = sr({'cmd': cmd, 'robot_id': hex(robot_id), 'sig': sig.hex()})

# Collect robot IDs and public keys
ids, Pks = [], []
for r in res:
    ids.append(int(r.get('robot_id'), 16))
    Pks.append(decompress_G1(G1Compressed(int(r.get('pk'), 16))))

# Step 3: Perform rogue key attack
# Choose arbitrary secret key
sk = 1337

# Create command we want to execute (admin command)
cmd = 'unveil_secrets'

# Compute our public key normally
pk = bls.SkToPk(sk)
sig = bls.Sign(sk, cmd.encode())
Pk = pubkey_to_G1(pk)

# ATTACK: Compute rogue public key
# Instead of Pk' = sk * G, we compute: Pk' = sk * G - Σ(other Pks)
# This makes: Pk_agg = Σ(other Pks) + Pk' = sk * G
# So our signature (sk * H(m)) validates against Pk_agg!
Pk_prime = add(Pk, neg(reduce(add, Pks, Z1)))
pk_prime = G1_to_pubkey(Pk_prime)

# Verify the attack worked (aggregated PK equals our chosen PK)
assert normalize(add(reduce(add, Pks), Pk_prime)) == normalize(Pk), "Rogue key attack failed!"
log.success('Forged signature!')

# Step 4: Join with our rogue public key
res = sr({'cmd': 'join', 'pk': pk_prime.hex()})
log.info(f"Join response: {res}")
robot_id = int(res.get('robot_id'), 16)
ids.append(robot_id)

# Now we have 6 robot IDs for the next phase
assert len(ids) == 6, f"Expected 6 IDs, got {len(ids)}"
log.info(f"Collected {len(ids)} robot IDs for EC-LCG crack")

# ----------------------------------------------------------------------------
# Phase 2: EC-LCG PRNG Crack (Lattice Attack)
# ----------------------------------------------------------------------------
log.info("Phase 2: EC-LCG PRNG State Recovery")

# Robot IDs contain x-coordinates from EC-LCG
# Upper 32 bits of each ID is the x-coordinate
# Recover the full PRNG state using lattice attack
Wn = crack_ec_lcg([i << 32 for i in ids])
log.success('Cracked EC-LCG!')
log.info(f"Recovered PRNG state: W_n = ({Wn[0]}, {Wn[1]})")

# ----------------------------------------------------------------------------
# Phase 3: Zero-Knowledge Proof Cheating (64 rounds)
# ----------------------------------------------------------------------------
log.info("Phase 3: Cheating ZKP Verification")
prog = log.progress('Cheating ZKP')

# Send verify command - use hex() format like working solvers
verify_cmd = {'cmd': 'verify', 'robot_id': hex(robot_id)}
log.info(f"Sending verify command...")
io.sendlineafter(b'> ', json.dumps(verify_cmd).encode())

# Receive the initial message from verify()
init_msg = io.recvline(timeout=30).decode().strip()
log.info(f"Server: {init_msg}")

# Small delay before starting ZKP rounds
time.sleep(0.5)

# Execute 64 rounds of ZKP (32 iterations × 2 coordinates)
# For each round, we:
#   1. Predict the challenge bit using the cracked PRNG
#   2. Craft a commitment that passes verification without knowing the secret key
#   3. Respond appropriately to the challenge
round_num = 0
for i in range(64 // 2):  # 32 iterations
    # Advance PRNG state: W[n+1] = W[n] + G (addition in EC-LCG)
    Wn += G
    
    # Process both x and y coordinates (2 rounds per iteration)
    for c in Wn.xy():
        round_num += 1
        
        # Predict challenge bit from PRNG output
        # bit = (x-coordinate >> 32) & 1
        bit = (int(c) >> 32) & 1
        
        log.info(f"Round {round_num}/64 - Predicted bit: {bit}")
        
        try:
            # Use unique x value for each round
            # This prevents C value collisions and potential pattern detection
            x = 1337 + round_num
            
            # Wait for server's commitment prompt
            prompt = io.recvuntil(b'Take a random value x and send me C = x * G1 (hex): ', timeout=30)
            log.debug(f"  Server prompt: {prompt[-80:]}")
            
            if bit == 1:
                # Challenge bit is 1: Server will ask for x
                # Honest response: C = x * G1, then reveal x
                # This works because we can actually provide x
                C = multiply(G1, x)
                C_hex = bytes(G1_to_pubkey(C)).hex()
                
                log.info(f"  Sending C (x*G1): {C_hex[:40]}...")
                io.sendline(C_hex.encode())
                time.sleep(0.3)
                
                # Server verifies: C == x * G1
                prompt2 = io.recvuntil(b'Give me x (hex): ', timeout=30)
                log.debug(f"  Server prompt 2: {prompt2}")
                
                log.info(f"  Sending x: {hex(x)}")
                io.sendline(hex(x).encode())
                time.sleep(0.3)
                
            else:
                # Challenge bit is 0: Server will ask for (sk + x)
                # Problem: We don't know sk!
                # Solution: Craft C such that we can still pass verification
                #
                # Server verifies: C + Pk_prime == (sk + x) * G1
                # We want to send x as (sk + x), so:
                #   C + Pk_prime == x * G1
                #   C == x * G1 - Pk_prime
                #
                # By setting C = x*G1 - Pk_prime and sending x as (sk+x),
                # the server's check passes without us knowing sk!
                C = add(multiply(G1, x), neg(Pk_prime))
                C_hex = bytes(G1_to_pubkey(C)).hex()
                
                log.info(f"  Sending C (x*G1-Pk): {C_hex[:40]}...")
                io.sendline(C_hex.encode())
                time.sleep(0.3)
                
                # Server verifies: C + Pk_prime == (sk + x) * G1
                prompt2 = io.recvuntil(b'Give me (sk + x) (hex): ', timeout=30)
                log.debug(f"  Server prompt 2: {prompt2}")
                
                # Send x (pretending it's sk+x, but our C makes it work!)
                log.info(f"  Sending (sk+x) as x: {hex(x)}")
                io.sendline(hex(x).encode())
                time.sleep(0.3)
                
        except Exception as e:
            # Handle any protocol errors
            import traceback
            log.failure(f"Error in round {round_num}: {type(e).__name__}: {e}")
            log.info(f"Traceback: {traceback.format_exc()}")
            
            # Try to receive any remaining data from server for debugging
            try:
                remaining = io.recv(timeout=2)
                if remaining:
                    log.info(f"Remaining data from server: {remaining}")
            except:
                pass
            
            io.close()
            exit(1)

# After all 64 rounds, receive the verification result
verify_result = json.loads(io.recvline().decode())
if 'error' in verify_result:
    log.failure(f"ZKP failed: {verify_result}")
    io.close()
    exit(1)

prog.success()
log.success("All 64 ZKP rounds completed successfully!")

# ----------------------------------------------------------------------------
# Final Step: Retrieve the Flag
# ----------------------------------------------------------------------------
log.info("Retrieving flag...")
res = sr({'cmd': cmd, 'sig': sig.hex()})
log.success(f"FLAG: {res.get('flag')}")

# Clean disconnect
sr({'cmd': 'exit'})
io.close()

log.success("Challenge completed successfully!")
log.success("=" * 60)
io.close()