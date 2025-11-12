import json
import time

from functools import reduce
from pwn import process, sys, remote, log

from py_ecc.bls.ciphersuites import G2ProofOfPossession as bls
from py_ecc.bls.g2_primitives import G1_to_pubkey, pubkey_to_G1
from py_ecc.bls.point_compression import decompress_G1
from py_ecc.bls.typing import G1Compressed

from py_ecc.optimized_bls12_381.optimized_curve import add, G1, multiply, neg, normalize, Z1

from sage.all import EllipticCurve, GF, identity_matrix, PolynomialRing, Sequence, zero_matrix, ZZ


def get_process():
    # Connect to the CTF server with error handling
    try:
        log.info("Connecting to remote server...")
        conn = remote('83.136.253.5', 47445, timeout=110)
        log.success("Connected successfully!")
        return conn
    except Exception as e:
        log.failure(f"Connection failed: {e}")
        sys.exit(1)


def sr(data):
    try:
        io.sendlineafter(b'> ', json.dumps(data).encode())
        response = io.recvline(timeout=5).decode()
        return json.loads(response)
    except EOFError:
        log.failure("Connection closed by server (EOF)")
        raise
    except Exception as e:
        log.failure(f"Communication error: {e}")
        raise


p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
K = GF(p)
a = K(0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc)
b = K(0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b)
E = EllipticCurve(K, (a, b))
G = E(0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296, 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)
E.set_order(0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551 * 0x1)


def crack_ec_lcg(values):
    assert len(values) == 6
    u1, v1, u2, v2, u3, v3 = values
    a1, b1, a2, b2, a3, b3 = PolynomialRing(K, 'a1, b1, a2, b2, a3, b3').gens()

    ec1 = (v1 + b1) ** 2 - (u1 + a1) ** 3 - a * (u1 + a1) - b
    ec2 = (v2 + b2) ** 2 - (u2 + a2) ** 3 - a * (u2 + a2) - b
    ec3 = (v3 + b3) ** 2 - (u3 + a3) ** 3 - a * (u3 + a3) - b

    ec4 = ((u1 + a1) + (u2 + a2) + G.x()) * ((u2 + a2) - (u1 + a1)) ** 2 - ((v2 + b2) + (v1 + b1)) ** 2
    ec5 = ((u2 + a2) + (u3 + a3) + G.x()) * ((u3 + a3) - (u2 + a2)) ** 2 - ((v3 + b3) + (v2 + b2)) ** 2
    ec6 = (G.y() - (v1 + b1)) * ((u2 + a2) - (u1 + a1)) - ((v2 + b2) + (v1 + b1)) * ((u1 + a1) - G.x())
    ec7 = (G.y() - (v2 + b2)) * ((u3 + a3) - (u2 + a2)) - ((v3 + b3) + (v2 + b2)) * ((u2 + a2) - G.x())

    A, v = Sequence([ec1, ec2, ec3, ec4, ec5, ec6, ec7]).coefficients_monomials(sparse=False)
    A = A.change_ring(ZZ)

    A = (identity_matrix(7) * p).augment(A)
    A = A.stack(zero_matrix(len(v), 7).augment(identity_matrix(len(v))))
    A[-1, -1] = 2 ** 256

    L = A.T.LLL()
    assert L[-1][-1] == 2 ** 256
    a1, b1, a2, b2, a3, b3 = L[-1][-7:-1]

    W1 = E(u1 + a1, v1 + b1)
    W2 = E(u2 + a2, v2 + b2)
    W3 = E(u3 + a3, v3 + b3)
    return W3


log.info("="*60)
log.info("Blessed CTF Challenge - Verbose Solver")
log.info("="*60)

io = get_process()

log.info("Step 1: Creating robot...")
res = sr({'cmd': 'create'})
sk = int(res.get('sk'), 16)
robot_id = int(res.get('robot_id'), 16)
log.success(f"Created robot ID: {hex(robot_id)[:20]}...")

log.info("Step 2: Listing all robots...")
cmd = 'list'
sig = bls.Sign(sk, cmd.encode())
res = sr({'cmd': cmd, 'robot_id': hex(robot_id), 'sig': sig.hex()})

ids, Pks = [], []

for r in res:
    ids.append(int(r.get('robot_id'), 16))
    Pks.append(decompress_G1(G1Compressed(int(r.get('pk'), 16))))

log.success(f"Found {len(res)} robots")

log.info("Step 3: Computing rogue public key...")
sk = 1337
cmd = 'unveil_secrets'
pk = bls.SkToPk(sk)
sig = bls.Sign(sk, cmd.encode())
Pk = pubkey_to_G1(pk)

Pk_prime = add(Pk, neg(reduce(add, Pks, Z1)))
pk_prime = G1_to_pubkey(Pk_prime)
assert normalize(add(reduce(add, Pks), Pk_prime)) == normalize(Pk)
log.success('Forged signature!')

log.info("Step 4: Joining with rogue key...")
res = sr({'cmd': 'join', 'pk': pk_prime.hex()})
robot_id = int(res.get('robot_id'), 16)
ids.append(robot_id)
assert len(ids) == 6
log.success(f"Rogue robot joined: {hex(robot_id)[:20]}...")

log.info("Step 5: Cracking EC-LCG PRNG...")
Wn = crack_ec_lcg([i << 32 for i in ids])
log.success('Cracked EC-LCG!')

log.info("Step 6: Starting ZKP verification (64 rounds with verbose output)...")

try:
    # Send verify command without waiting for JSON response
    io.sendlineafter(b'> ', json.dumps({'cmd': 'verify', 'robot_id': hex(robot_id)}).encode())

    # Receive the initial message from verify()
    init_msg = io.recvline(timeout=50).decode().strip()
    log.info(f"Server initial message: {init_msg}")

    round_num = 0
    for i in range(64 // 2):
        Wn += G
        
        log.info(f"\nIteration {i}: Wn coordinates:")
        log.info(f"  Wn.x = {Wn.xy()[0]}")
        log.info(f"  Wn.y = {Wn.xy()[1]}")

        for c in Wn.xy():
            round_num += 1
            bit = (int(c) >> 32) & 1
            
            log.info(f"\n{'='*60}")
            log.info(f"Round {round_num}/64")
            log.info(f"  Predicted bit: {bit}")
            log.info(f"  Coordinate: {hex(int(c) >> 32)}")
            log.info(f"{'='*60}")
            
            try:
                # Wait for server prompt
                prompt = io.recvuntil(b'Take a random value x and send me C = x * G1 (hex): ', timeout=50)
                log.info(f"Server prompt received")
                
                # Add 1 second delay before sending response
                time.sleep(1)
                
                if (int(c) >> 32) & 1:
                    x = 1337
                    C = multiply(Pk_prime, x)
                    C_hex = bytes(G1_to_pubkey(C)).hex()
                    
                    log.info(f"  Sending C (x * Pk_prime): {C_hex[:32]}...")
                    io.sendline(C_hex.encode())
                    
                    # Add delay before receiving next prompt
                    time.sleep(1)
                    
                    # Wait for next prompt
                    prompt2 = io.recvuntil(b'Give me x (hex): ', timeout=50)
                    log.info(f"  Server asks for x")
                    
                    # Add delay before sending x
                    time.sleep(1)
                    
                    log.info(f"  Sending x: {hex(x)}")
                    io.sendline(hex(x).encode())
                    
                    # Check for proof failure immediately after sending x
                    # The server will either send next prompt or error JSON
                    time.sleep(0.5)
                    
                else:
                    sk_x = 1337
                    C = add(multiply(G1, sk_x), neg(Pk_prime))
                    C_hex = bytes(G1_to_pubkey(C)).hex()
                    
                    log.info(f"  Sending C (sk_x*G1 - Pk_prime): {C_hex[:32]}...")
                    io.sendline(C_hex.encode())
                    
                    # Add delay before receiving next prompt
                    time.sleep(1)
                    
                    # Wait for next prompt
                    prompt2 = io.recvuntil(b'Give me (sk + x) (hex): ', timeout=50)
                    log.info(f"  Server asks for (sk + x)")
                    
                    # Add delay before sending response
                    time.sleep(1)
                    
                    log.info(f"  Sending (sk + x): {hex(sk_x)}")
                    io.sendline(hex(sk_x).encode())
                    
                    # Check for proof failure immediately after sending (sk + x)
                    # The server will either send next prompt or error JSON
                    time.sleep(0.5)
                
                log.success(f"Round {round_num}/64 completed ✓")
                
            except EOFError:
                log.failure(f"Connection lost during round {round_num}/64")
                log.info("Server may have rejected our response or timed out")
                
                # Try to read any remaining data to see if there was an error message
                try:
                    remaining = io.recvall(timeout=1).decode()
                    if remaining:
                        log.info(f"Remaining data from server: {remaining}")
                        try:
                            error_data = json.loads(remaining)
                            if 'error' in error_data:
                                log.failure(f"Server error: {error_data['error']}")
                                log.info(f"Failed at round {round_num}/64, predicted bit: {bit}")
                        except:
                            pass
                except:
                    pass
                    
                io.close()
                sys.exit(1)
            except Exception as e:
                log.failure(f"Error in round {round_num}/64: {e}")
                
                # Try to read any error from server
                try:
                    remaining = io.recvall(timeout=1).decode()
                    if remaining:
                        log.info(f"Server response: {remaining}")
                except:
                    pass
                    
                io.close()
                sys.exit(1)

    # After all rounds, receive the verification result
    verify_result_line = io.recvline(timeout=50).decode()
    log.info(f"\nServer final response: {verify_result_line}")
    verify_result = json.loads(verify_result_line)

    if 'error' in verify_result:
        log.failure(f"ZKP failed: {verify_result}")
        io.close()
        exit(1)

    log.success('✓ ALL 64 ZKP rounds PASSED!')

except EOFError:
    log.failure("Connection closed by server unexpectedly during ZKP")
    log.info("Possible causes:")
    log.info("  - Server rejected our verification request")
    log.info("  - Server timed out")
    log.info("  - Incorrect robot_id or authentication")
    io.close()
    sys.exit(1)
except Exception as e:
    log.failure(f"Unexpected error during ZKP: {e}")
    io.close()
    sys.exit(1)

log.info("Step 7: Unveiling secrets with forged signature...")
res = sr({'cmd': cmd, 'sig': sig.hex()})

if 'flag' in res:
    log.success("="*60)
    log.success(f"FLAG: {res.get('flag')}")
    log.success("="*60)
else:
    log.error(f"Response: {res}")

sr({'cmd': 'exit'})
io.close()
