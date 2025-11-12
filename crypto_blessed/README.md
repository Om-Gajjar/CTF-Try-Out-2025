# Blessed CTF Challenge - Quick Start Guide

## 📁 What's in this folder

- **`server.py`** - Challenge source code (for reference)
- **`solver.py`** - Complete exploit script (requires SageMath)
- **`setup.sh`** - Automated setup script for WSL Ubuntu
- **`requirements.txt`** - Python dependencies
- **`SOLUTION_WRITEUP.md`** - Full technical writeup
- **`README.md`** - This file

## 🚀 Quick Start (WSL Ubuntu)

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./setup.sh

# If using conda Sage, activate it:
source ~/miniconda3/bin/activate
conda activate sage

# Run the exploit
sage -python solver.py

# Wait 1-2 minutes for the flag!
```

### Option 2: Manual Setup

```bash
# Install SageMath
sudo apt update
sudo apt install sagemath -y

# OR if not available, use conda:
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b
~/miniconda3/bin/conda init bash
source ~/.bashrc
conda create -n sage -c conda-forge sage python=3.11 -y
conda activate sage

# Install Python dependencies
pip install -r requirements.txt

# Run exploit
sage -python solver.py
```

### Option 3: Docker (No Installation Required)

```bash
# Pull SageMath Docker image
docker pull sagemath/sagemath

# Run exploit in Docker
docker run -it --rm \
  -v $(pwd):/home/sage/work \
  -w /home/sage/work \
  sagemath/sagemath \
  sage -python solver.py
```

## 📊 What the exploit does

The solver performs a sophisticated multi-stage attack:

1. **Connect to server** (83.136.254.84:54006)
2. **Create robot** - Get BLS secret key
3. **List robots** - Collect PRNG outputs (robot IDs)
4. **Compute rogue key** - BLS signature forgery setup
5. **Crack EC-LCG** - Break PRNG using LLL lattice (10-30 sec)
6. **Cheat ZKP** - Predict 64 random challenges (30-60 sec)
7. **Get flag** - Forge aggregate signature

**Total time:** 1-2 minutes

## 🔧 Troubleshooting

### SageMath not found
```bash
# Try conda installation
conda create -n sage -c conda-forge sage -y
conda activate sage
```

### Import errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Connection timeout
```bash
# Check if server is running
nc -zv 83.136.254.84 54006
```

### Docker permission denied
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

## 📖 Understanding the Attack

This challenge combines three advanced cryptographic attacks:

### 1. EC-LCG PRNG Breaking
- **Target:** Elliptic curve linear congruential generator
- **Weakness:** Leaks upper 32 bits of EC point coordinates
- **Attack:** LLL lattice reduction to recover full points
- **Tool:** SageMath (required)

### 2. BLS Rogue Key Attack  
- **Target:** BLS signature aggregation
- **Weakness:** No proof-of-possession required
- **Attack:** Craft malicious public key that cancels others
- **Result:** Forge aggregate signature with only our key

### 3. Zero-Knowledge Proof Cheating
- **Target:** Interactive ZKP for key ownership
- **Weakness:** Challenges use predictable PRNG
- **Attack:** Predict 64 random challenges
- **Result:** Pass verification without knowing private key

## 🎯 Expected Output

```
[*] Step 1: Creating robot to get signing capability...
[+] Created robot ID: 0x1234567890abcdef...
[*] Step 2: Listing all robots...
[+] Found 5 robots (4 pre-existing + 1 ours)
[*] Step 3: Computing rogue public key for BLS attack...
[+] Rogue public key computed and verified!
[*] Step 4: Joining with rogue key...
[+] Rogue robot joined: 0xfedcba0987654321...
[*] Step 5: Cracking EC-LCG PRNG (this takes 10-30 seconds)...
[*] Setting up polynomial ring and equations...
[*] Building lattice matrix...
[*] Running LLL lattice reduction...
[+] Recovered EC point W3: (12345..., 67890...)
[+] EC-LCG PRNG cracked! Can now predict random bits.
[*] Step 6: Starting ZKP verification (64 rounds)...
[+] ZKP rounds: 64/64
[+] ZKP verification passed!
[*] Step 7: Unveiling secrets with forged signature...
[+] ============================================================
[+] FLAG: HTB{...}
[+] ============================================================

HTB{...}
```

## 📚 Learn More

- Read `SOLUTION_WRITEUP.md` for detailed technical explanation
- Review `server.py` to understand the vulnerabilities
- Study the `solver.py` code to see attack implementation

## 🐛 Need Help?

If you encounter issues:
1. Check that SageMath is properly installed: `sage --version`
2. Verify Python packages: `pip list | grep -E "py_ecc|pwntools"`
3. Test connection: `nc 83.136.254.84 54006`
4. Try Docker method (no local installation needed)

## ✅ Verification

Before running, verify setup:
```bash
# Check SageMath
sage --version

# Check Python packages
python3 -c "import py_ecc, pwn; print('✓ Dependencies OK')"

# Check server
nc -zv 83.136.254.84 54006
```

---

**Challenge:** Blessed (Hard - 1000 points)  
**Category:** Cryptography  
**Target:** 83.136.254.84:54006  
**Time:** ~2 minutes to flag with proper setup
