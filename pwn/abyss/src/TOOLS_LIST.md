# Essential PWN Tools List for HTB Abyss Challenge

## Quick Reference

| Tool | Status | Purpose | Priority | Install Command |
|------|--------|---------|----------|-----------------|
| **pwntools** | ❌ Missing | Exploit development framework | 🔴 CRITICAL | `pip3 install --user pwntools` |
| **pwndbg** | ❌ Missing | GDB enhancement | 🔴 CRITICAL | `git clone https://github.com/pwndbg/pwndbg && cd pwndbg && ./setup.sh` |
| **ROPgadget** | ❌ Missing | ROP chain builder | 🔴 CRITICAL | `pip3 install --user ropgadget` |
| **strace** | ❌ Missing | System call tracer | 🟡 HIGH | `sudo apt install strace` |
| **ltrace** | ❌ Missing | Library call tracer | 🟡 HIGH | `sudo apt install ltrace` |
| **checksec** | ❌ Missing | Binary protections checker | 🟡 HIGH | Included in pwntools |
| **one_gadget** | ❌ Missing | One-gadget RCE finder | 🟢 MEDIUM | `sudo gem install one_gadget` |
| **seccomp-tools** | ❌ Missing | Seccomp analyzer | 🟢 MEDIUM | `sudo gem install seccomp-tools` |
| **ghidra** | ❌ Missing | Reverse engineering GUI | 🟢 MEDIUM | Download from GitHub |
| **gdb** | ✅ Installed | Core debugger | - | Already present |
| **python3** | ✅ Installed | Python interpreter | - | Already present |
| **gcc** | ✅ Installed | C compiler | - | Already present |
| **objdump** | ✅ Installed | Disassembler | - | Already present |
| **readelf** | ✅ Installed | ELF analyzer | - | Already present |
| **radare2** | ✅ Installed | Alternative RE tool | - | Already present |

---

## Category 1: CRITICAL Tools (Install First)

### 1. pwntools
**Purpose**: Python framework for exploit development
**Why Critical**: 
- Automated payload generation
- Socket handling for remote exploits
- Built-in utilities (cyclic patterns, packing, etc.)
- Industry standard for CTF pwn challenges

**Installation**:
```bash
pip3 install --user pwntools
```

**Verification**:
```bash
python3 -c "from pwn import *; print(context)"
```

**Usage Example for Abyss**:
```python
from pwn import *

# Connect
io = remote('83.136.255.106', 53373)

# Send LOGIN command
io.send(p32(0))

# Send payload
payload = b'USER ' + b'A' * 507 + p32(541)
io.send(payload)

# Interactive
io.interactive()
```

---

### 2. pwndbg (GDB Extension)
**Purpose**: Enhanced GDB for binary exploitation
**Why Critical**:
- Visual stack/heap/register display
- Automatic exploit detection
- Better disassembly view
- Built-in pattern generation

**Installation**:
```bash
cd ~
git clone https://github.com/pwndbg/pwndbg
cd pwndbg
./setup.sh
```

**Alternative: GEF**:
```bash
bash -c "$(curl -fsSL https://gef.blah.cat/sh)"
```

**Verification**:
```bash
gdb -q
# Should show pwndbg or gef banner
```

**Usage for Abyss**:
```bash
gdb ./abyss

# Set breakpoint at cmd_login
b *cmd_login

# Run with input file
r < payload.bin

# View stack
telescope $rsp 20

# View registers
registers

# Find cyclic pattern offset
cyclic 500
cyclic -l 0x61616171
```

---

### 3. ROPgadget
**Purpose**: Find ROP gadgets in binaries
**Why Critical**:
- Essential for ROP chain construction
- Bypass NX/DEP protections
- Find useful instruction sequences

**Installation**:
```bash
pip3 install --user ropgadget
```

**Verification**:
```bash
ROPgadget --version
```

**Usage for Abyss**:
```bash
# Find all gadgets
ROPgadget --binary abyss

# Find pop/ret gadgets
ROPgadget --binary abyss --only "pop|ret"

# Find specific register gadgets
ROPgadget --binary abyss --only "pop rdi|pop rsi|pop rdx"

# Search for strings
ROPgadget --binary abyss --string "/bin/sh"

# Generate ROP chain
ROPgadget --binary abyss --ropchain
```

---

## Category 2: HIGH Priority Tools

### 4. strace
**Purpose**: Trace system calls
**Why Important**: 
- See what syscalls the program makes
- Understand program behavior
- Debug file operations

**Installation**:
```bash
sudo apt install strace
```

**Usage for Abyss**:
```bash
# Basic trace
strace ./abyss

# Trace specific syscalls
strace -e trace=read,write,open ./abyss

# Follow forks
strace -f ./abyss

# Save to file
strace -o trace.log ./abyss
```

---

### 5. ltrace
**Purpose**: Trace library calls
**Why Important**:
- See library function calls (strcmp, strcpy, etc.)
- Understand program logic
- Find vulnerabilities

**Installation**:
```bash
sudo apt install ltrace
```

**Usage for Abyss**:
```bash
# Basic trace
ltrace ./abyss

# Trace specific functions
ltrace -e strcmp,strcpy ./abyss

# Show timestamps
ltrace -t ./abyss
```

---

### 6. checksec (part of pwntools)
**Purpose**: Check binary security features
**Why Important**:
- Know what protections to bypass
- Plan exploit strategy

**Usage**:
```bash
# Using pwntools
python3 -c "from pwn import *; print(checksec('./abyss'))"

# Or use checksec script
checksec --file=abyss
```

**Expected output for Abyss**:
```
Arch:     amd64-64-little
RELRO:    Partial RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      No PIE (0x400000)
```

---

## Category 3: MEDIUM Priority Tools

### 7. one_gadget
**Purpose**: Find one-shot RCE gadgets in libc
**Installation**:
```bash
sudo apt install ruby ruby-dev
sudo gem install one_gadget
```

**Usage**:
```bash
one_gadget /lib/x86_64-linux-gnu/libc.so.6
```

---

### 8. seccomp-tools
**Purpose**: Analyze seccomp filters
**Installation**:
```bash
sudo gem install seccomp-tools
```

**Usage**:
```bash
seccomp-tools dump ./abyss
```

---

### 9. Ghidra
**Purpose**: Advanced static analysis
**Installation**: Download from GitHub releases
**Alternative**: Use radare2 (already installed)

---

## Complete Installation Script

Save as `install_pwn_tools.sh`:

```bash
#!/bin/bash

echo "Installing PWN tools..."

# System tools
sudo apt update
sudo apt install -y strace ltrace ruby ruby-dev

# Python tools
pip3 install --user pwntools ropgadget

# GDB enhancement
cd ~
git clone https://github.com/pwndbg/pwndbg
cd pwndbg
./setup.sh

# Ruby gems
sudo gem install one_gadget seccomp-tools

echo "Installation complete!"
echo "Restart terminal and verify with: python3 -c 'import pwn'"
```

Run with:
```bash
chmod +x install_pwn_tools.sh
./install_pwn_tools.sh
```

---

## One-Line Install Command

```bash
sudo apt update && sudo apt install -y strace ltrace ruby ruby-dev && pip3 install --user pwntools ropgadget && cd ~ && git clone https://github.com/pwndbg/pwndbg && cd pwndbg && ./setup.sh && sudo gem install one_gadget seccomp-tools
```

---

## Verification Checklist

After installation, run these commands:

```bash
# Python modules
python3 -c "from pwn import *; print('✅ pwntools:', __version__)"
ROPgadget --version

# System tools  
strace --version | head -1
ltrace --version | head -1

# GDB
gdb -q  # Should show pwndbg banner

# Ruby gems
one_gadget --version
seccomp-tools --version
```

---

## Tool Usage Workflow for Abyss

```
1. checksec ./abyss          → Check protections
2. objdump -d abyss          → Quick disassembly
3. gdb ./abyss               → Debug with pwndbg
4. strace ./abyss            → Watch syscalls
5. ltrace ./abyss            → Watch library calls
6. ROPgadget --binary abyss  → Find gadgets
7. python3 exploit.py        → Run pwntools exploit
```

---

## Quick Reference Card

### Most Used Commands

**pwntools**:
```python
p32(0x12345678)      # Pack 32-bit little endian
p64(0x12345678)      # Pack 64-bit little endian
cyclic(100)          # Generate pattern
cyclic_find(0x6161)  # Find pattern offset
remote('ip', port)   # Connect to remote
io.sendline(data)    # Send line
io.recvuntil('>')    # Receive until marker
io.interactive()     # Interactive shell
```

**pwndbg**:
```
b *0x401234          # Breakpoint at address
r                    # Run
c                    # Continue
ni                   # Next instruction
si                   # Step into
telescope $rsp 20    # View stack
vmmap                # View memory map
search "string"      # Search memory
ropgadget            # Find gadgets
```

**ROPgadget**:
```bash
ROPgadget --binary file                    # All gadgets
ROPgadget --binary file --only "pop|ret"   # Filter gadgets
ROPgadget --binary file --string "/bin/sh" # Find strings
```

---

## Troubleshooting

### pwntools won't install
```bash
sudo apt install python3-dev python3-pip libssl-dev libffi-dev build-essential
pip3 install --user --upgrade pip
pip3 install --user pwntools
```

### pwndbg not loading in GDB
```bash
cat ~/.gdbinit  # Check if pwndbg is sourced
echo "source ~/pwndbg/gdbinit.py" >> ~/.gdbinit
```

### ROPgadget command not found
```bash
# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Ruby gem permission errors
```bash
# Install without sudo
gem install --user-install one_gadget
echo 'export PATH="$HOME/.gem/ruby/2.7.0/bin:$PATH"' >> ~/.bashrc
```

---

## Additional Learning Resources

- **pwntools docs**: https://docs.pwntools.com/
- **pwndbg GitHub**: https://github.com/pwndbg/pwndbg
- **ROPgadget**: https://github.com/JonathanSalwan/ROPgadget
- **Pwn tutorials**: https://ir0nstone.gitbook.io/
- **CTF challenges**: https://pwnable.kr/, https://exploit.education/

---

**Last Updated**: 2024-11-10
**For Challenge**: HTB Abyss
**Difficulty**: Easy (1000 points)
