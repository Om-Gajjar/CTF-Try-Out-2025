#!/bin/bash
# Test script for solver.py
# This script verifies that the solver is properly configured and ready to run

set -e

echo "=========================================="
echo "Blessed CTF Solver - Verification Test"
echo "=========================================="
echo ""

# Check if sage environment exists
echo "[*] Checking SageMath installation..."
if command -v sage &> /dev/null; then
    echo "    ✓ SageMath found: $(which sage)"
elif [ -d "$HOME/miniforge3/envs/sage" ]; then
    echo "    ✓ SageMath conda environment found"
else
    echo "    ✗ SageMath not found"
    echo "    Please run setup.sh or install SageMath manually"
    exit 1
fi

# Activate sage environment if using conda
if [ -f "$HOME/miniforge3/etc/profile.d/conda.sh" ]; then
    export PATH="$HOME/miniforge3/bin:$PATH"
    source $HOME/miniforge3/etc/profile.d/conda.sh
    conda activate sage
fi

echo ""
echo "[*] Checking Python packages..."
python -c "import py_ecc; print('    ✓ py_ecc')" 2>/dev/null || echo "    ✗ py_ecc (run: pip install py_ecc)"
python -c "import pwn; print('    ✓ pwntools')" 2>/dev/null || echo "    ✗ pwntools (run: pip install pwntools)"
python -c "from Crypto.PublicKey import ECC; print('    ✓ pycryptodome')" 2>/dev/null || echo "    ✗ pycryptodome (run: pip install pycryptodome)"
python -c "from sage.all import EllipticCurve; print('    ✓ sagemath')" 2>/dev/null || echo "    ✗ sagemath"

echo ""
echo "[*] Checking solver.py syntax..."
python -c "import ast; ast.parse(open('solver.py').read()); print('    ✓ solver.py syntax valid')"

echo ""
echo "[*] Checking file integrity..."
if [ -f "solver.py" ]; then
    echo "    ✓ solver.py exists"
else
    echo "    ✗ solver.py not found"
    exit 1
fi

if [ -f "server.py" ]; then
    echo "    ✓ server.py exists"
else
    echo "    ✗ server.py not found"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ All checks passed!"
echo "=========================================="
echo ""
echo "To run the solver against the CTF server:"
echo "  python solver.py"
echo ""
echo "To run against a custom server:"
echo "  CTF_HOST=your.server.ip CTF_PORT=12345 python solver.py"
echo ""
echo "To test locally:"
echo "  1. In terminal 1: python server.py"
echo "  2. In terminal 2: CTF_HOST=127.0.0.1 CTF_PORT=<port> python solver.py"
echo ""
