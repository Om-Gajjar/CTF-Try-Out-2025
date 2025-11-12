#!/bin/bash

# Blessed CTF Challenge - Setup Script for WSL Ubuntu
# This script installs all dependencies including SageMath

set -e  # Exit on error

echo "=========================================="
echo "Blessed CTF Challenge - Setup"
echo "=========================================="
echo ""

# Check if running on WSL
if ! grep -qi microsoft /proc/version; then
    echo "Warning: This script is designed for WSL Ubuntu"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "[*] Step 1: Updating package lists..."
sudo apt update

echo ""
echo "[*] Step 2: Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-dev build-essential git

echo ""
echo "[*] Step 3: Installing SageMath (this may take a while)..."
echo "    Option 1: Try apt (may not be available)"
if sudo apt install -y sagemath 2>/dev/null; then
    echo "    ✓ SageMath installed via apt"
    SAGE_CMD="sage"
else
    echo "    ✗ SageMath not available in apt, using Miniconda..."
    
    # Install Miniconda if not present
    if [ ! -d "$HOME/miniconda3" ]; then
        echo "    Installing Miniconda..."
        wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
        bash /tmp/miniconda.sh -b -p $HOME/miniconda3
        rm /tmp/miniconda.sh
        
        # Initialize conda
        eval "$($HOME/miniconda3/bin/conda shell.bash hook)"
        conda init bash
    else
        echo "    ✓ Miniconda already installed"
        eval "$($HOME/miniconda3/bin/conda shell.bash hook)"
    fi
    
    # Create sage environment
    echo "    Creating Sage environment (this takes 5-10 minutes)..."
    if ! conda env list | grep -q "sage"; then
        conda create -n sage -c conda-forge sage python=3.11 -y
    fi
    
    echo "    ✓ SageMath environment created"
    SAGE_CMD="conda run -n sage sage"
fi

echo ""
echo "[*] Step 4: Installing Python dependencies..."
pip3 install -r requirements.txt --quiet

echo ""
echo "[*] Step 5: Verifying installation..."
echo "    Checking Python packages..."
python3 -c "import py_ecc; print('  ✓ py_ecc')"
python3 -c "import pwn; print('  ✓ pwntools')"
python3 -c "from Crypto.PublicKey import ECC; print('  ✓ pycryptodome')"

echo ""
echo "    Checking SageMath..."
if command -v sage &> /dev/null; then
    sage -c "print('  ✓ SageMath')" 2>/dev/null || echo "  ⚠ SageMath installed but may need shell restart"
else
    echo "  ⚠ SageMath installed via conda (activate with: conda activate sage)"
fi

echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. If using conda Sage, activate it:"
echo "     source ~/miniconda3/bin/activate"
echo "     conda activate sage"
echo ""
echo "  2. Run the exploit:"
echo "     sage -python solver.py"
echo ""
echo "  3. Wait 1-2 minutes for the flag!"
echo ""
echo "If setup failed, try manually:"
echo "  sudo apt install sagemath"
echo "  OR use Docker:"
echo "  docker run -it -v \$(pwd):/work sagemath/sagemath"
echo "=========================================="
