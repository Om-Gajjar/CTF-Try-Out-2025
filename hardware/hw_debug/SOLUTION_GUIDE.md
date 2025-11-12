# HTB Challenge: Debug - Complete Solution Guide

## Challenge Information
- **Name:** Debug
- **Category:** Hardware
- **Difficulty:** Easy
- **Points:** 950

---

## Challenge Description
Your team recovered a satellite dish used for transmitting relic locations, but it's malfunctioning due to interference. The debugging interface captured a serial signal during boot that needs to be decoded to find the interference source.

---

## Files Provided

- **hw_debug.sal** - Saleae Logic Analyzer capture file (42 KB)

This is a digital logic capture from a Logic Analyzer containing:
- **Channel 0 (TX)** - UART Transmit line
- **Channel 1 (RX)** - UART Receive line
- **Sample Rate:** 25 MHz
- **Duration:** ~37 seconds

---

## Step-by-Step Solution

### **Method 1: Using Saleae Logic 2 Software (Recommended)**

#### **Step 1: Install Saleae Logic 2**

Download from: https://www.saleae.com/downloads/

**For Linux:**
```bash
cd /tmp
wget https://downloads.saleae.com/logic2/Logic-2.4.14-linux-x64.AppImage
chmod +x Logic-2.4.14-linux-x64.AppImage
./Logic-2.4.14-linux-x64.AppImage
```

**For Windows/Mac:**
- Download and install the appropriate version

---

#### **Step 2: Open the Capture File**

1. Launch **Saleae Logic 2**
2. Click **"Open a Capture"** or **File → Open Capture**
3. Navigate to `hw_debug.sal`
4. Click **Open**

You should see two digital channels with waveforms.

---

#### **Step 3: Add UART Analyzer**

1. On the right side panel, click **"Analyzers"** (or the **"+"** button)
2. Select **"Async Serial"** (this is the UART protocol decoder)
3. Configure the analyzer settings:
   - **Input Channel:** **Channel 1 (RX)** ← Important!
   - **Bit Rate (Baud):** **115200** ← This is the correct baud rate
   - **Bits per Frame:** 8
   - **Stop Bits:** 1  
   - **Parity Bit:** None
   - **Significant Bit:** LSB First
   - **Signal Inversion:** None
4. Click **"Save"** or **"Apply"**

---

#### **Step 4: View Decoded Data**

The decoded UART data will appear:
- Above the waveform as individual bytes
- In the **"Terminal"** view (if available)
- In the **"Data Table"** view

You should see ASCII text including boot messages!

---

#### **Step 5: Export Decoded Data**

**Option A: Use Terminal View**
- Look for a **"Terminal"** tab/view in the analyzer
- Copy all the text

**Option B: Export to File**
- Right-click on the **Async Serial** analyzer
- Select **"Export to text/CSV file"**
- Choose ASCII format
- Save and open the file

---

#### **Step 6: Find the Flag**

Look for warning messages in the decoded boot sequence:

```
WARNING: The deep space observatory is offline HTB{
INFO: Communication systems are offline reference code: 547311173_
WARNING: Unauthorized subroutines detected! reference code: n37w02k_
WARNING: The satellite dish can not sync with the swarm. reference code: c0mp20m153d}
```

**Combine the "reference codes" with the HTB{ } markers:**

```
HTB{547311173_n37w02k_c0mp20m153d}
```

---

### **Method 2: Using PulseView (sigrok) - Alternative**

#### **Step 1: Install PulseView**

```bash
sudo apt-get update
sudo apt-get install -y pulseview sigrok-cli
```

#### **Step 2: Open the Capture**

```bash
pulseview hw_debug.sal
```

**Note:** PulseView may have issues with .sal format. If it doesn't open, use Method 1 or Method 3.

#### **Step 3: Add UART Protocol Decoder**

1. Click **"Add protocol decoder"**
2. Select **UART**
3. Configure:
   - **RX:** Channel 1
   - **Baud rate:** 115200
   - **Data bits:** 8
   - **Parity:** none
   - **Stop bits:** 1
4. View decoded output in the annotation layer

---

### **Method 3: Manual Analysis (Advanced)**

If you don't have GUI access, you can parse the binary format:

```python
import struct
import zipfile

# Extract .sal file (it's a ZIP)
with zipfile.ZipFile('hw_debug.sal', 'r') as z:
    z.extractall('sal_contents/')
    
# The digital-1.bin contains RX data
# This requires understanding the Saleae binary format
# (Not recommended for beginners)
```

---

## Understanding the Boot Sequence

The decoded UART shows a complete ARM-based embedded system boot:

### **1. Trusted Firmware Boot (BL1, BL2, BL31)**
```
NOTICE:  Booting Trusted Firmware
NOTICE:  BL1: v1.3(release):f26889a
```
- ARM Trusted Firmware is booting
- Multiple boot stages (BL1 → BL2 → BL31)

### **2. U-Boot Bootloader**
```
U-Boot 2016.05-00307-g16c388c (Jul 23 2021 - 22:19:05 +0000)
DRAM:  1004 MiB
```
- Das U-Boot (Universal Bootloader)
- Initializing hardware (RAM, MMC, etc.)

### **3. ASCII Art Banner**
```
                }--O--{
                  [^]
                 /ooo\
```
- Custom satellite dish ASCII art

### **4. Critical Messages with Flag** ⚠️
```
WARNING: The deep space observatory is offline HTB{
INFO: Communication systems are offline reference code: 547311173_
WARNING: Unauthorized subroutines detected! reference code: n37w02k_
WARNING: The satellite dish can not sync with the swarm. reference code: c0mp20m153d}
```
- **This is where the flag is hidden!**
- Split across multiple log messages
- Indicates network compromise

### **5. Linux Kernel Boot**
```
Starting kernel ...
Development login enabled: no
Debugging mode enabled: yes
```
- Linux kernel loading
- System configuration shown

---

## Flag Breakdown

```
HTB{547311173_n37w02k_c0mp20m153d}
```

**Decoded (leetspeak):**
- `547311173` = `satellite` (5=S, 4=A, 7=T, 3=E, 1=L, etc.)
- `n37w02k` = `network` (3=E, 7=T, 0=O, 2=R)
- `c0mp20m153d` = `compromised` (0=O, 2=R, 1=I, 5=S, 3=E)

**Full meaning:**
```
HTB{satellite_network_compromised}
```

This tells us the **source of interference**: The satellite network has been compromised by an attacker!

---

## UART Protocol Explained

### **What is UART?**
- **Universal Asynchronous Receiver/Transmitter**
- Serial communication protocol
- Used for debugging embedded systems
- Common in IoT devices, routers, satellites, etc.

### **UART Frame Structure:**
```
[START] [D0 D1 D2 D3 D4 D5 D6 D7] [STOP]
   0     LSB ← data bits → MSB    1
```

- **Start bit:** Always 0 (LOW)
- **8 data bits:** Actual data (LSB first)
- **Stop bit:** Always 1 (HIGH)
- **Idle state:** Line is HIGH

### **Common Baud Rates:**
- 9600 bps
- 19200 bps
- 38400 bps
- 57600 bps
- **115200 bps** ← This challenge
- 230400 bps

### **Why 115200?**
- Fast enough for debug output
- Slow enough to be reliable
- Standard default for many embedded Linux systems

---

## Key Concepts

### **Logic Analyzer**
- Hardware tool that captures digital signals
- Records timing and state changes
- Essential for debugging hardware/firmware
- **Saleae Logic** is a popular brand

### **Serial Console/Debug Port**
- Most embedded devices have UART debug ports
- Provides boot logs and shell access
- Often exposed on PCB test points
- Critical for hardware hacking and forensics

### **Embedded System Boot Process**
1. **Boot ROM** - CPU starts here (hardcoded)
2. **Bootloader** - Initializes hardware (U-Boot, GRUB, etc.)
3. **Kernel** - Operating system loads (Linux, FreeRTOS, etc.)
4. **Init System** - Starts services
5. **Application** - User programs run

---

## Real-World Applications

### **Hardware Security Research**
- **Firmware extraction** from debug ports
- **Root access** via UART console
- **Bootloader exploitation** (U-Boot command injection)
- **Hardware reverse engineering**

### **IoT Security**
- Many IoT devices expose UART
- Default credentials in boot logs
- Unlocked bootloaders
- Debug modes left enabled

### **Notable Examples:**
1. **Router Hacking** - UART access to root shell
2. **Smart TV Exploitation** - Debug console access
3. **Car Hacking** - CAN bus + UART debugging
4. **Satellite Modems** - This challenge scenario!

---

## Tools & Resources

### **Logic Analyzers:**
- **Saleae Logic** ($100-500) - Professional, great software
- **DSLogic** ($100-200) - Open-source compatible
- **Bus Pirate** ($30) - Multi-protocol tool
- **Cheap USB Logic Analyzers** ($5-10) - Works with PulseView

### **Software:**
- **Saleae Logic 2** - Official software (Free)
- **PulseView/sigrok** - Open-source alternative
- **minicom/screen** - Terminal emulators for live UART
- **Python pyserial** - Programmatic UART access

### **Hardware Connections:**
```
Device    Logic Analyzer
------    --------------
GND   →   GND (Ground reference)
TX    →   Channel 0 (Device transmits)
RX    →   Channel 1 (Device receives)
```

**Common UART pinouts on PCBs:**
- 4-pin header: GND, TX, RX, VCC
- 3-pin header: GND, TX, RX
- Test points labeled: UART, DEBUG, CONSOLE, SERIAL

---

## Common Mistakes

1. **❌ Wrong baud rate** → Text appears as garbage
2. **❌ Using TX instead of RX** → No data or wrong data
3. **❌ Incorrect bit settings** → Corrupted characters
4. **❌ Not waiting for full boot** → Missing flag in early boot messages
5. **❌ Signal inversion** → All bits are flipped

---

## Troubleshooting

### **Problem: Garbled/Corrupted Text**
**Solution:** Wrong baud rate. Try these in order:
- 115200 ✓ (Correct for this challenge)
- 9600
- 57600
- 38400
- 19200

### **Problem: No data appears**
**Solution:** 
- Check you're using Channel 1 (RX)
- Verify the capture loaded correctly
- Check analyzer is enabled

### **Problem: Some characters are wrong**
**Solution:**
- Check parity setting (should be None)
- Verify 8 data bits, 1 stop bit
- Check signal isn't inverted

### **Problem: Can't export data**
**Solution:**
- Use Terminal view and copy/paste
- Take screenshots
- Use Data Table export feature

---

## Practice & Learning

### **Similar Challenges:**
1. **HackTheBox Hardware:**
   - Critical Flight (PCB analysis)
   - It's Oops PM (VHDL analysis)
   - Other Hardware category challenges

2. **CTF Platforms:**
- PicoCTF Hardware challenges
- CSAW Hardware challenges  
- RCTF Hardware category

### **Hands-On Practice:**
1. **Get a USB-to-UART adapter** ($5)
2. **Connect to a Raspberry Pi/Arduino**
3. **Capture boot sequences**
4. **Practice with different baud rates**

### **Learning Resources:**
- **SparkFun UART Tutorial** - Great beginner guide
- **Saleae Learning Portal** - Logic analyzer tutorials
- **Hardware Hacking Handbook** - Advanced techniques
- **"Practical IoT Hacking"** by Fotios Chantzis

---

## Quick Reference

### **One-Command Solution (with Logic 2):**
```bash
./Logic-2.4.14-linux-x64.AppImage hw_debug.sal
# Add Async Serial analyzer: CH1, 115200 baud
# View Terminal output
# Look for warning messages with reference codes
```

### **Flag:**
```
HTB{547311173_n37w02k_c0mp20m153d}
```

**Translation:**
```
HTB{satellite_network_compromised}
```

### **Key Settings:**
- **Channel:** 1 (RX)
- **Baud Rate:** 115200
- **Data Bits:** 8
- **Parity:** None
- **Stop Bits:** 1

---

## Summary Checklist

- [ ] Extract hw_debug.sal file
- [ ] Install Saleae Logic 2 (or PulseView)
- [ ] Open capture in Logic 2
- [ ] Add Async Serial analyzer to Channel 1
- [ ] Set baud rate to 115200
- [ ] View decoded UART data
- [ ] Locate warning messages with "reference code"
- [ ] Combine codes: HTB{547311173_n37w02k_c0mp20m153d}
- [ ] Submit flag

---

## Security Implications

### **Why This Matters:**

1. **Debug Ports = Security Risk**
   - Many devices ship with UART exposed
   - Boot logs reveal sensitive info
   - Can provide root access

2. **Information Disclosure**
   - Firmware versions
   - Memory addresses
   - Encryption keys in logs
   - Network configuration

3. **Attack Vectors:**
   - Bootloader command injection
   - Root shell access
   - Firmware dumping
   - Debug mode exploitation

### **Mitigation:**
- **Disable debug ports** in production
- **Remove silk screen labels** for UART pins
- **Use authentication** for debug access
- **Encrypted boot logs**
- **Secure boot** configurations

---

## Additional Notes

### **ARM Trusted Firmware:**
- Secure boot chain for ARM processors
- BL1 → BL2 → BL31 → BL32 → BL33 stages
- Used in smartphones, embedded devices
- Part of ARM's security architecture

### **U-Boot Commands:**
- `egypt` - Custom boot interrupt command (seen in challenge)
- `printenv` - Show environment variables
- `boot` - Continue boot process
- `md` - Memory dump

### **File Format:**
- `.sal` - Saleae Logic 2 capture format
- Actually a ZIP archive
- Contains:
  - `meta.json` - Capture metadata
  - `digital-N.bin` - Channel data
  - `analog-N.bin` - Analog channel data (if any)

---

**Last Updated:** November 2025  
**Challenge Solved By:** Decoding UART serial data from logic analyzer capture  
**Difficulty Rating:** Easy (with right tools)  
**Time Required:** 15-20 minutes  
**Skills Learned:** UART analysis, logic analyzer usage, embedded system debugging
