import json
import time
import socket

from functools import reduce
from pwn import process, sys, remote, log, context

from py_ecc.bls.ciphersuites import G2ProofOfPossession as bls
from py_ecc.bls.g2_primitives import G1_to_pubkey, pubkey_to_G1
from py_ecc.bls.point_compression import decompress_G1
from py_ecc.bls.typing import G1Compressed

from py_ecc.optimized_bls12_381.optimized_curve import add, G1, multiply, neg, normalize, Z1

from sage.all import EllipticCurve, GF, identity_matrix, PolynomialRing, Sequence, zero_matrix, ZZ


def get_process():
    # Connect to the CTF server with error handling and stable connection settings
    try:
        log.info("Connecting to remote server...")
        conn = remote('83.136.251.67', 36730, timeout=30)
        
        # Enable TCP keepalive to maintain connection
        try:
            sock = conn.sock
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            # Set keepalive options (platform-specific)
            if hasattr(socket, 'TCP_KEEPIDLE'):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
            if hasattr(socket, 'TCP_KEEPINTVL'):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
            if hasattr(socket, 'TCP_KEEPCNT'):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 6)
            
            # Disable Nagle's algorithm for lower latency
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            
            # Set socket buffer sizes
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
            
            log.success("Connected with stable connection settings!")
        except Exception as e:
            log.warning(f"Could not set all socket options: {e}")
            log.success("Connected successfully!")
        
        return conn
    except Exception as e:
        log.failure(f"Connection failed: {e}")
        raise


def sr(io, data):
    """Send and receive with retries on transient errors"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            io.sendlineafter(b'> ', json.dumps(data).encode())
            response = io.recvline(timeout=10).decode()
            return json.loads(response)
        except EOFError:
            log.failure("Connection closed by server (EOF)")
            raise
        except socket.timeout:
            if attempt < max_retries - 1:
                log.warning(f"Timeout, retrying... ({attempt + 1}/{max_retries})")
                time.sleep(1)
                continue
            else:
                log.failure("Communication timeout after retries")
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                log.warning(f"Communication error, retrying: {e}")
                time.sleep(1)
                continue
            else:
                log.failure(f"Communication error after retries: {e}")
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


def run_attempt(attempt_num, max_attempts):
    """Run a single attempt of the solver"""
    io = None
    try:
        log.info("="*60)
        if attempt_num == 1:
            log.info("Blessed CTF Challenge - Solver with Auto-Retry")
        else:
            log.info(f"RETRY ATTEMPT {attempt_num}/{max_attempts}")
        log.info("="*60)

        io = get_process()

        log.info("Step 1: Creating robot...")
        res = sr(io, {'cmd': 'create'})
        sk = int(res.get('sk'), 16)
        robot_id = int(res.get('robot_id'), 16)
        log.success(f"Created robot ID: {hex(robot_id)[:20]}...")

        log.info("Step 2: Listing all robots...")
        cmd = 'list'
        sig = bls.Sign(sk, cmd.encode())
        res = sr(io, {'cmd': cmd, 'robot_id': hex(robot_id), 'sig': sig.hex()})

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
        res = sr(io, {'cmd': 'join', 'pk': pk_prime.hex()})
        robot_id = int(res.get('robot_id'), 16)
        ids.append(robot_id)
        assert len(ids) == 6
        log.success(f"Rogue robot joined: {hex(robot_id)[:20]}...")

        log.info("Step 5: Cracking EC-LCG PRNG...")
        Wn = crack_ec_lcg([i << 32 for i in ids])
        log.success('Cracked EC-LCG!')

        log.info("Step 6: Starting ZKP verification (64 rounds)...")

        # Send verify command
        io.sendlineafter(b'> ', json.dumps({'cmd': 'verify', 'robot_id': hex(robot_id)}).encode())

        # Receive the initial message from verify()
        init_msg = io.recvline(timeout=10).decode().strip()
        log.info(f"Server: {init_msg}")
        
        # Send a heartbeat-like acknowledgment by flushing buffers
        time.sleep(0.5)

        round_num = 0
        for i in range(64 // 2):
            Wn += G

            for c in Wn.xy():
                round_num += 1
                bit = (int(c) >> 32) & 1
                
                log.info(f"Round {round_num}/64 - Predicted bit: {bit}, coordinate MSB: {hex(int(c) >> 32)}")
                
                try:
                    # Wait for server prompt with extended timeout
                    log.info(f"  Waiting for C prompt...")
                    prompt = io.recvuntil(b'Take a random value x and send me C = x * G1 (hex): ', timeout=15)
                    log.info(f"  ✓ Received C prompt")
                    
                    # Prepare response based on predicted bit
                    if bit == 1:
                        # Server will ask for x
                        x = 1337
                        C = multiply(Pk_prime, x)
                        C_hex = bytes(G1_to_pubkey(C)).hex()
                        
                        log.info(f"  Predicting 'x' challenge (bit=1), sending C=x*Pk_prime")
                        io.sendline(C_hex.encode())
                        time.sleep(1.0)
                        
                        log.info(f"  Waiting for 'Give me x' prompt...")
                        prompt2 = io.recvuntil(b'Give me x (hex): ', timeout=15)
                        log.success(f"  ✓ Got expected 'x' prompt - prediction CORRECT!")
                        time.sleep(1.0)
                        
                        io.sendline(hex(x).encode())
                        time.sleep(0.5)
                        
                    else:
                        # Server will ask for (sk + x)
                        sk_x = 1337
                        C = add(multiply(G1, sk_x), neg(Pk_prime))
                        C_hex = bytes(G1_to_pubkey(C)).hex()
                        
                        log.info(f"  Predicting '(sk+x)' challenge (bit=0), sending C=sk_x*G-Pk_prime")
                        io.sendline(C_hex.encode())
                        time.sleep(1.0)
                        
                        log.info(f"  Waiting for 'Give me (sk + x)' prompt...")
                        prompt2 = io.recvuntil(b'Give me (sk + x) (hex): ', timeout=15)
                        log.success(f"  ✓ Got expected '(sk+x)' prompt - prediction CORRECT!")
                        time.sleep(1.0)
                        
                        io.sendline(hex(sk_x).encode())
                        time.sleep(0.5)
                    
                    log.success(f"✓ Round {round_num}/64 completed successfully")
                    
                except EOFError:
                    log.failure(f"✗ Connection lost at round {round_num}/64")
                    
                    # Try to read error message
                    try:
                        remaining = io.recvall(timeout=1).decode()
                        if remaining:
                            log.info(f"Server response: {remaining}")
                            try:
                                error_data = json.loads(remaining)
                                if 'error' in error_data:
                                    log.failure(f"Server error: {error_data['error']}")
                            except:
                                pass
                    except:
                        pass
                    
                    if io:
                        io.close()
                    return False  # Failed attempt
                    
                except Exception as e:
                    log.failure(f"Error in round {round_num}/64: {e}")
                    if io:
                        io.close()
                    return False  # Failed attempt

        # After all rounds, receive the verification result
        verify_result_line = io.recvline(timeout=10).decode()
        log.info(f"Server response: {verify_result_line}")
        verify_result = json.loads(verify_result_line)

        if 'error' in verify_result:
            log.failure(f"ZKP failed: {verify_result}")
            io.close()
            return False

        log.success('✓ ALL 64 ZKP rounds PASSED!')

        log.info("Step 7: Unveiling secrets with forged signature...")
        res = sr(io, {'cmd': cmd, 'sig': sig.hex()})

        if 'flag' in res:
            log.success("="*60)
            log.success(f"FLAG: {res.get('flag')}")
            log.success("="*60)
            sr(io, {'cmd': 'exit'})
            io.close()
            return True  # Success!
        else:
            log.error(f"Response: {res}")
            io.close()
            return False

    except Exception as e:
        log.failure(f"Attempt failed with error: {e}")
        if io:
            try:
                io.close()
            except:
                pass
        return False


def main():
    MAX_ATTEMPTS = 200
    
    # Set pwntools context for more stable connections
    context.log_level = 'info'
    
    for attempt in range(1, MAX_ATTEMPTS + 1):
        success = run_attempt(attempt, MAX_ATTEMPTS)
        
        if success:
            log.success("="*60)
            log.success(f"SUCCESS on attempt {attempt}/{MAX_ATTEMPTS}!")
            log.success("="*60)
            return
        
        if attempt < MAX_ATTEMPTS:
            wait_time = 3  # Increased wait time between attempts
            log.info(f"Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
    
    log.failure("="*60)
    log.failure(f"Failed after {MAX_ATTEMPTS} attempts")
    log.failure("="*60)
    sys.exit(1)


if __name__ == '__main__':
    main()
