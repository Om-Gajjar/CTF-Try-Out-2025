# HW Debug - CTF Challenge

## 📋 Challenge Information

**Category:** Hardware  
**Difficulty:** Easy  
**Points:** 950  
**Challenge Type:** Logic Analyzer / UART Serial Decoding  

## 📝 Challenge Description

Your team recovered a satellite dish used for transmitting relic locations, but it's malfunctioning due to interference. The debugging interface captured a serial signal during boot that needs to be decoded to find the interference source. Analyze the logic analyzer capture to decode the UART serial communication and retrieve the flag.

## 🎯 Solution Overview

The challenge involves:
1. Loading a Saleae Logic Analyzer capture file (.sal)
2. Adding a UART/Async Serial analyzer
3. Configuring the correct baud rate
4. Decoding the serial data to find the flag

### Key Insight
The flag is transmitted over UART serial communication during boot. You need to decode the digital signal to ASCII text.

## 🚀 Quick Start

### Prerequisites
- Saleae Logic 2 software (free)
- Windows/Linux/Mac supported

### Installation

**Linux:**
```bash
cd /tmp
wget https://downloads.saleae.com/logic2/Logic-2.4.14-linux-x64.AppImage
chmod +x Logic-2.4.14-linux-x64.AppImage
./Logic-2.4.14-linux-x64.AppImage
```

**Windows/Mac:**
- Download from: https://www.saleae.com/downloads/
- Install and run

### Running the Analysis

```bash
# Navigate to challenge directory
cd hardware/hw_debug

# Open Saleae Logic 2
# File -> Open Capture -> Select data/hw_debug.sal

# Add Async Serial Analyzer:
# 1. Click "Analyzers" in top right
# 2. Select "Async Serial"
# 3. Configure:
#    - Input Channel: Channel 0 (TX)
#    - Bit Rate (Baud): 115200
#    - Bits per Frame: 8
#    - Parity Bit: None
#    - Stop Bits: 1
# 4. Click "Save"

# View decoded data:
# - Terminal view shows ASCII output
# - Flag will be visible in the serial output
```

## 📁 Folder Structure

```
hw_debug/
├── README.md              # This file
├── data/                  # Challenge files
│   ├── hw_debug.sal      # Saleae Logic capture (42 KB)
│   ├── hw_debug.zip      # Archived capture
│   └── decoded_output.txt # Decoded serial data
├── docs/                  # Documentation
│   └── SOLUTION_GUIDE.md # Complete walkthrough
└── solution/              # Solution scripts
```

## 🔧 Technical Details

### Capture Information

- **File Format:** Saleae Logic Analyzer (.sal)
- **Channels:** 2 (Channel 0 = TX, Channel 1 = RX)
- **Sample Rate:** 25 MHz
- **Duration:** ~37 seconds
- **Protocol:** UART (Universal Asynchronous Receiver-Transmitter)

### UART Configuration

Standard UART settings for this capture:
```
Baud Rate: 115200 bps
Data Bits: 8
Parity: None
Stop Bits: 1
```

### Signal Analysis

**Channel 0 (TX):**
- Transmit line from device
- Contains boot messages and flag
- Active signal with data

**Channel 1 (RX):**
- Receive line to device
- May be idle or contain responses
- Less relevant for this challenge

### Decoding Process

1. **Digital Signal** → Raw voltage levels (0V/3.3V)
2. **UART Framing** → Start bit, 8 data bits, stop bit
3. **ASCII Decoding** → Binary to text characters
4. **Flag Extraction** → Find HTB{...} pattern

## 💡 Learning Points

1. **Logic Analyzers:** Understanding digital signal capture
2. **UART Protocol:** Serial communication basics
3. **Baud Rate:** Importance of matching transmission speed
4. **Signal Analysis:** Decoding digital protocols
5. **Hardware Debugging:** Using logic analyzers for troubleshooting

## 🐛 Troubleshooting

### Saleae Logic Won't Open File
```bash
# Check file integrity
file data/hw_debug.sal

# Try extracting from zip if needed
unzip data/hw_debug.zip
```

### Garbled Output / No Readable Text
- **Wrong Baud Rate:** Try common rates (9600, 19200, 38400, 57600, 115200)
- **Wrong Channel:** Ensure Channel 0 is selected
- **Inverted Signal:** Try "Inverted" option in analyzer settings

### Can't Find Flag
- Scroll through entire decoded output
- Use terminal view for easier reading
- Search for "HTB" or "flag" keywords
- Check decoded_output.txt if available

### Logic 2 Installation Issues (Linux)
```bash
# Make executable
chmod +x Logic-*.AppImage

# Install FUSE if needed
sudo apt install fuse libfuse2

# Run with --appimage-extract if needed
./Logic-*.AppImage --appimage-extract
./squashfs-root/AppRun
```

## 📖 Alternative Method: Command-Line Decoding

If you prefer not to use GUI:

```bash
# Using sigrok (open-source logic analyzer software)
sudo apt install sigrok-cli

# Convert and decode (if format supported)
sigrok-cli -i data/hw_debug.sal -P uart:baudrate=115200 -A uart
```

## 🔍 What to Look For

The decoded output will contain:
- Boot messages
- System initialization logs
- Debug information
- **The flag** in HTB{...} format
- Possibly error messages or warnings

## ✅ Success Criteria

- Successfully load .sal file in Saleae Logic 2
- Configure UART analyzer with correct baud rate
- Decode serial data to ASCII text
- Locate and extract the flag
- Flag format: `HTB{...}`

## 📖 Additional Resources

- See `docs/SOLUTION_GUIDE.md` for complete walkthrough with screenshots
- [Saleae Logic Documentation](https://support.saleae.com/user-guide)
- [UART Protocol Explained](https://www.analog.com/en/analog-dialogue/articles/uart-a-hardware-communication-protocol.html)
- [Logic Analyzer Basics](https://learn.sparkfun.com/tutorials/using-logic-analyzers)

---

**Challenge Type:** Hardware Debug / Serial Protocol Analysis  
**Key Skills:** Logic analyzer usage, UART decoding, signal analysis  
**Tools:** Saleae Logic 2, sigrok (alternative)  
**Difficulty:** Easy (straightforward signal decoding)
