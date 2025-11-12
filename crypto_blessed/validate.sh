#!/bin/bash
# Quick validation script to check if everything is ready

echo "Blessed CTF - Environment Validation"
echo "====================================="
echo ""

ERRORS=0

# Check 1: SageMath
echo -n "[1/5] Checking SageMath... "
if command -v sage &> /dev/null; then
    VERSION=$(sage --version 2>&1 | head -1)
    echo "✓ Found: $VERSION"
elif conda env list 2>/dev/null | grep -q sage; then
    echo "✓ Found in conda (activate with: conda activate sage)"
else
    echo "✗ NOT FOUND"
    echo "      Install with: sudo apt install sagemath"
    echo "      OR run: ./setup.sh"
    ERRORS=$((ERRORS + 1))
fi

# Check 2: Python packages
echo -n "[2/5] Checking py_ecc... "
if python3 -c "import py_ecc" 2>/dev/null; then
    echo "✓"
else
    echo "✗ NOT FOUND"
    echo "      Install with: pip install -r requirements.txt"
    ERRORS=$((ERRORS + 1))
fi

echo -n "[3/5] Checking pwntools... "
if python3 -c "import pwn" 2>/dev/null; then
    echo "✓"
else
    echo "✗ NOT FOUND"
    echo "      Install with: pip install -r requirements.txt"
    ERRORS=$((ERRORS + 1))
fi

echo -n "[4/5] Checking pycryptodome... "
if python3 -c "from Crypto.PublicKey import ECC" 2>/dev/null; then
    echo "✓"
else
    echo "✗ NOT FOUND"
    echo "      Install with: pip install -r requirements.txt"
    ERRORS=$((ERRORS + 1))
fi

# Check 3: Server connectivity
echo -n "[5/5] Checking server connectivity... "
if timeout 3 bash -c "echo > /dev/tcp/83.136.254.84/54006" 2>/dev/null; then
    echo "✓ Server is reachable"
else
    echo "⚠ Cannot reach server (may be firewall/network issue)"
    echo "      This won't prevent local testing"
fi

echo ""
echo "====================================="
if [ $ERRORS -eq 0 ]; then
    echo "✓ ALL CHECKS PASSED!"
    echo ""
    echo "Ready to run exploit:"
    echo "  sage -python solver.py"
else
    echo "✗ $ERRORS ERROR(S) FOUND"
    echo ""
    echo "Fix the issues above, then run:"
    echo "  ./validate.sh"
    echo ""
    echo "Or run the setup script:"
    echo "  ./setup.sh"
fi
echo "====================================="
