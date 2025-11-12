# PWN Tools Installation Guide for HTB Abyss Challenge

## Tools Status Summary

### ✅ Already Installed (11 tools)
- gdb - GNU Debugger
- python3 - Python 3 interpreter
- gcc - GNU Compiler Collection
- objdump - Binary disassembler
- readelf - ELF file analyzer
- radare2 - Reverse engineering framework
- file - File type identifier
- strings - Extract printable strings
- hexdump - Hex dump utility
- nc - Netcat (network utility)
- socat - Socket relay tool

### ❌ Missing Tools (8 tools)
- checksec - Binary security checker
- ROPgadget - ROP gadget finder
- ghidra - NSA reverse engineering tool
- strace - System call tracer
- ltrace - Library call tracer
- one_gadget - One-gadget RCE finder
- seccomp-tools - Seccomp filter analyzer
- pwntools - Exploit development framework
- GDB extensions (pwndbg/gef/peda)

---

## Installation Commands

### 1. Essential Tools (High Priority)

#### Install pwntools (MOST IMPORTANT)
```bash
# Method 1: Using pip3 (recommended)
pip3 install pwntools --user

# Method 2: System-wide (requires sudo)
sudo apt update
sudo apt install python3-pwntools

# Verify installation
python3 -c "import pwn; print(pwn.__version__)"
```

#### Install ROPgadget
```bash
# Via pip3
pip3 install ropgadget --user

# Or via apt
sudo apt install python3-ropgadget

# Verify
ROPgadget --version
```

#### Install pwndbg (GDB Enhancement - HIGHLY RECOMMENDED)
```bash
# Clone and install pwndbg
cd ~
git clone https://github.com/pwndbg/pwndbg
cd pwndbg
./setup.sh

# Verify - should show pwndbg prompt
gdb -q
```

#### Alternative: Install GEF (Another GDB Enhancement)
```bash
# One-liner installation
bash -c "$(curl -fsSL https://gef.blah.cat/sh)"

# Or manual
wget -O ~/.gdbinit-gef.py -q https://gef.blah.cat/py
echo source ~/.gdbinit-gef.py >> ~/.gdbinit

# Verify
gdb -q
```

#### Install checksec
```bash
# Part of pwntools, but standalone version:
sudo apt install checksec

# Or use pwntools version
python3 -c "from pwn import *; print(checksec('/bin/ls'))"
```

#### Install strace and ltrace
```bash
sudo apt update
sudo apt install strace ltrace

# Verify
strace --version
ltrace --version
```

---

### 2. Advanced Tools (Medium Priority)

#### Install one_gadget (for libc exploits)
```bash
# Requires Ruby
sudo apt install ruby ruby-dev
sudo gem install one_gadget

# Verify
one_gadget --version
```

#### Install seccomp-tools (for seccomp analysis)
```bash
sudo gem install seccomp-tools

# Or via apt (if available)
sudo apt install seccomp-tools

# Verify
seccomp-tools --version
```

---

### 3. Optional Tools (Nice to Have)

#### Install Ghidra
```bash
# Download from NSA GitHub
cd ~/Downloads
wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_10.4_build/ghidra_10.4_PUBLIC_20230928.zip

# Extract
unzip ghidra_10.4_PUBLIC_20230928.zip
sudo mv ghidra_10.4_PUBLIC /opt/ghidra

# Create launcher
sudo ln -s /opt/ghidra/ghidraRun /usr/local/bin/ghidra

# Requires Java JDK
sudo apt install default-jdk

# Launch
ghidra
```

#### Install Binary Ninja (Commercial Alternative)
```bash
# Download from https://binary.ninja/
# Free version available for students/education
```

---

## Quick Installation Script (All Essential Tools)

```bash
#!/bin/bash

echo "Installing essential PWN tools..."

# Update package list
sudo apt update

# Install system packages
sudo apt install -y strace ltrace ruby ruby-dev

# Install Python tools
pip3 install --user pwntools ropgadget

# Install pwndbg (GDB enhancement)
cd ~
if [ ! -d "pwndbg" ]; then
    git clone https://github.com/pwndbg/pwndbg
    cd pwndbg
    ./setup.sh
fi

# Install Ruby gems
sudo gem install one_gadget seccomp-tools

echo "Installation complete!"
echo ""
echo "Verify installations:"
echo "  python3 -c 'import pwn; print(pwn.__version__)'"
echo "  ROPgadget --version"
echo "  gdb -q"
echo "  strace --version"
echo "  one_gadget --version"
```

---

## Verification Commands

After installation, verify each tool:

```bash
# Python modules
python3 -c "import pwn; print('pwntools:', pwn.__version__)"
python3 -c "import ropgadget; print('ROPgadget: OK')"

# System tools
gdb --version | head -1
ROPgadget --version
strace --version | head -1
ltrace --version | head -1

# Ruby gems
one_gadget --version
seccomp-tools --version

# GDB enhancement (should see colored prompt)
gdb -q
```

---

## Recommended Tool Priority for Abyss Challenge

### Tier 1 (MUST HAVE)
1. **pwntools** - Core exploit development
2. **pwndbg/gef** - GDB enhancement for debugging
3. **ROPgadget** - Find ROP chains
4. **strace** - Track system calls

### Tier 2 (VERY USEFUL)
5. **checksec** - Check binary protections
6. **ltrace** - Library call tracking
7. **one_gadget** - Quick RCE gadgets

### Tier 3 (NICE TO HAVE)
8. **ghidra** - Static analysis GUI
9. **seccomp-tools** - Seccomp analysis

---

## Usage Examples for Abyss

### Using pwntools
```python
from pwn import *

# Connect to challenge
io = remote('83.136.255.106', 53373)

# Send commands
io.send(p32(0))  # LOGIN command

# Interactive shell
io.interactive()
```

### Using ROPgadget
```bash
# Find all gadgets
ROPgadget --binary abyss

# Find specific gadgets
ROPgadget --binary abyss --only "pop|ret"

# Find gadgets with specific instructions
ROPgadget --binary abyss --string "/bin/sh"
```

### Using pwndbg
```bash
# Start GDB with pwndbg
gdb ./abyss

# Set breakpoint
b *cmd_login

# Run with input
r < payload.bin

# Examine stack
telescope $rsp 20

# Find patterns
cyclic 500
cyclic -l 0x61616171
```

### Using strace
```bash
# Trace system calls
strace ./abyss

# Trace specific syscalls
strace -e trace=read,write,open ./abyss

# Save to file
strace -o trace.log ./abyss
```

---

## Troubleshooting

### pwntools installation fails
```bash
# Install dependencies
sudo apt install python3-dev python3-pip libssl-dev libffi-dev build-essential

# Try again
pip3 install pwntools --user
```

### pwndbg not loading
```bash
# Check .gdbinit
cat ~/.gdbinit

# Manually source
echo "source ~/pwndbg/gdbinit.py" >> ~/.gdbinit
```

### Permission denied for gems
```bash
# Install without sudo
gem install --user-install one_gadget seccomp-tools

# Add to PATH
echo 'export PATH="$HOME/.gem/ruby/2.7.0/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## Additional Resources

- **Pwntools Documentation**: https://docs.pwntools.com/
- **Pwndbg GitHub**: https://github.com/pwndbg/pwndbg
- **ROPgadget GitHub**: https://github.com/JonathanSalwan/ROPgadget
- **Ghidra Documentation**: https://ghidra-sre.org/
- **CTF Binary Exploitation Guide**: https://ir0nstone.gitbook.io/notes/

---

**Save this file as**: `TOOLS_INSTALLATION.md`

**Quick install all essential tools**:
```bash
sudo apt update && sudo apt install -y strace ltrace ruby ruby-dev && pip3 install --user pwntools ropgadget && cd ~ && git clone https://github.com/pwndbg/pwndbg && cd pwndbg && ./setup.sh && sudo gem install one_gadget seccomp-tools
```
