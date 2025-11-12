# Silicon Data Sleuthing - CTF Challenge

## 📋 Challenge Information

**Category:** Forensics  
**Difficulty:** Easy  
**Points:** 975  
**Challenge Type:** Firmware Analysis / OpenWrt Forensics  

## 📝 Challenge Description

Analyze a router firmware dump (OpenWrt) extracted from a rusty router PCB found near a vault. Extract embedded filesystems, find configuration files and credentials, and answer questions via a remote service to obtain the flag.

## 🎯 Solution Overview

The challenge involves:
1. Analyzing router firmware binary (chal_router_dump.bin)
2. Using binwalk to identify embedded filesystems
3. Extracting JFFS2 filesystem with jefferson
4. Finding configuration files with credentials
5. Connecting to remote service to answer security questions
6. Obtaining the flag

## 🚀 Quick Start

### Prerequisites
- binwalk - Firmware analysis tool
- jefferson - JFFS2 extraction (python3-jefferson)
- strings, grep, file, hexdump
- netcat for server connection

### Installation
```bash
sudo apt install binwalk python3-jefferson
```

### Running the Analysis
```bash
# Navigate to challenge directory
cd forensics/Silicon_Data_Sleuthing

# Analyze the firmware dump
binwalk data/chal_router_dump.bin

# Extract filesystems
binwalk -e data/chal_router_dump.bin

# Extract JFFS2
jefferson -d output/ data/jffs2_filesystem.bin

# Search for credentials
grep -r "password" output/
grep -r "admin" output/
strings data/chal_router_dump.bin | grep -i pass
```

## 📁 Folder Structure

```
Silicon_Data_Sleuthing/
├── README.md              # This file
├── data/                  # Challenge files
│   └── chal_router_dump.bin  # Router firmware dump
├── docs/                  # Documentation
│   └── WRITEUP.md        # Detailed solution writeup
└── solution/              # Solution scripts (if any)
```

## 🔧 Technical Details

### Firmware Analysis Steps

1. **Identify File Type**
   ```bash
   file chal_router_dump.bin
   hexdump -C chal_router_dump.bin | head
   ```

2. **Scan for Embedded Files**
   ```bash
   binwalk chal_router_dump.bin
   ```

3. **Extract Filesystems**
   - Look for SquashFS, JFFS2, or other embedded FS
   - Use binwalk -e or jefferson for extraction

4. **Analyze Configuration Files**
   - Check `/etc/` for config files
   - Look for `/etc/shadow`, `/etc/config/`
   - Search for wireless configurations
   - Find SSH keys, passwords, credentials

5. **Connect to Challenge Server**
   - Answer questions about extracted data
   - Provide credentials or configuration values
   - Receive flag upon correct answers

## 💡 Learning Points

1. **Firmware Analysis:** Understanding router firmware structure
2. **Filesystem Extraction:** Working with embedded Linux filesystems
3. **OpenWrt:** Familiarity with OpenWrt configuration layout
4. **Forensics Tools:** binwalk, jefferson, strings
5. **Data Recovery:** Extracting sensitive information from binary dumps

## 📖 Additional Resources

- See `docs/WRITEUP.md` for complete step-by-step solution
- [binwalk Documentation](https://github.com/ReFirmLabs/binwalk)
- [jefferson - JFFS2 Extraction](https://github.com/sviehb/jefferson)
- [OpenWrt Documentation](https://openwrt.org/docs/start)

## ✅ Success Criteria

- Successfully extract firmware filesystems
- Locate configuration files and credentials
- Answer all remote service questions correctly
- Retrieve the flag
- Flag format: `HTB{...}`

---

**Challenge Type:** Firmware Forensics  
**Key Skills:** Binary analysis, filesystem extraction, credential recovery  
**Flag:** `HTB{Y0u'v3_m4st3r3d_0p3nWRT_d4t4_3xtr4ct10n!!_...}`
