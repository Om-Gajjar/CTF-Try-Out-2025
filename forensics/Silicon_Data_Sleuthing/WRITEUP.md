# Silicon Data Sleuthing - CTF Challenge Write-up

**Challenge:** Silicon Data Sleuthing  
**Category:** Forensics  
**Difficulty:** Easy  
**Points:** 975  
**Flag:** `HTB{Y0u'v3_m4st3r3d_0p3nWRT_d4t4_3xtr4ct10n!!_c21a6678c8f306f552d88c2748c603b9}`

---

## Introduction

In this challenge, we are presented with a scenario where we've discovered a rusty router PCB in the sand near a vault. The hardware team successfully extracted a firmware image from the router's ROM chip. Our task is to analyze this firmware image to recover sensitive information that could help bypass the vault's security countermeasures.

The challenge involves:
- Analyzing a router firmware dump (OpenWrt)
- Extracting embedded filesystems
- Finding configuration files and credentials
- Answering questions via a remote service to obtain the flag

---

## Tools & Environment Check

Before starting the analysis, we verified that the necessary tools were available:

```bash
# Check for firmware analysis tools
which binwalk    # ✓ Available
which strings    # ✓ Available
which grep       # ✓ Available
which file       # ✓ Available
which dd         # ✓ Available
which hexdump    # ✓ Available
```

**Additional tool required:** `jefferson` (for JFFS2 extraction)
- Initially not installed, installed via: `sudo apt install python3-jefferson`

---

## Firmware Extraction & Reconnaissance

### Step 1: Initial File Analysis

First, we examined the firmware file to understand its type:

```bash
file chal_router_dump.bin
# Output: chal_router_dump.bin: data
```

The file is identified as generic data, which is typical for raw firmware dumps.

### Step 2: Firmware Scanning with Binwalk

We used `binwalk` to scan for embedded filesystems and files within the firmware:

```bash
binwalk chal_router_dump.bin
```

**Key findings:**
- U-Boot bootloader (offset 0x17DA0)
- uImage header at 0x180000 containing:
  - **OpenWrt version:** Linux-5.15.134
  - Image created: 2023-10-09
- **Squashfs filesystem** at offset 0x42C2C8 (main root filesystem)
- **JFFS2 filesystem** at offset 0x7C0000 (overlay filesystem for persistent data)

**Why this matters:** Router firmware typically uses a read-only Squashfs for the base system and a writable JFFS2 overlay for user configurations. The JFFS2 is where we'll find customized settings.

### Step 3: Extracting Filesystems

```bash
binwalk -e chal_router_dump.bin
```

This command extracted:
1. **squashfs-root/** - Base OpenWrt filesystem
2. **7C0000.jffs2** - Overlay filesystem (not automatically extracted, needs jefferson)

---

## Findings & Exploitation

### Step 4: Exploring the Base Filesystem

We explored the extracted Squashfs filesystem:

```bash
cd _chal_router_dump.bin.extracted/squashfs-root/
ls -la
```

Found standard OpenWrt directory structure:
- `/etc/` - Configuration files
- `/www/` - Web interface
- `/root/` - Root home directory (empty)
- `/bin/`, `/sbin/`, `/usr/` - System binaries

### Step 5: Checking Initial Credentials

```bash
cat etc/passwd
cat etc/shadow
```

**Finding:** The base filesystem showed `root:::0:99999:7:::` (no password hash) - this is the default OpenWrt state. However, the challenge asked for a password hash, indicating modifications were made.

### Step 6: Extracting the JFFS2 Overlay

The JFFS2 filesystem contains user modifications. We extracted it using jefferson:

```bash
jefferson -d jffs2-root 7C0000.jffs2
```

**Why JFFS2 is important:** In OpenWrt, the overlay filesystem uses JFFS2 to store changes made after installation. Any passwords set, WiFi configurations, or firewall rules would be here.

### Step 7: Analyzing JFFS2 Contents

The JFFS2 extracted into an unusual structure with numbered files:

```bash
cd jffs2-root/work/work/
ls -la
```

These numbered files (#2c, #30, #32, etc.) represent the overlay modifications. We systematically examined them:

**File #2c** - Modified passwd file (same as base)
**File #32** - **CRITICAL FINDING:** Modified shadow file with password hash!

```bash
cat "jffs2-root/work/work/#32"
```

Output:
```
root:$1$YfuRJudo$cXCiIJXn9fWLIt8WY2Okp1:19804:0:99999:7:::
```

**What this means:** 
- Hash type: MD5-based crypt ($1$)
- Salt: YfuRJudo
- This is the actual root password hash set by the administrator

### Step 8: Finding Network Configuration

**File #4/network** - WAN/LAN configuration

```bash
cat "jffs2-root/work/work/#4/network"
```

**Key findings:**
```
config interface 'wan'
    option proto 'pppoe'
    option username 'yohZ5ah'
    option password 'ae-h+i$i^Ngohroorie!bieng6kee7oh'
```

**Why PPPoE credentials matter:** PPPoE is used for DSL internet connections. These credentials authenticate the router to the ISP and could be used to access the network.

### Step 9: WiFi Configuration

**File #4/wireless** - Wireless settings

```bash
cat "jffs2-root/work/work/#4/wireless"
```

**Key findings:**
```
config wifi-iface 'default_radio0'
    option ssid 'VLT-AP01'
    option encryption 'sae-mixed'
    option key 'french-halves-vehicular-favorable'
```

**Security note:** The WiFi uses WPA3-SAE (Simultaneous Authentication of Equals), which is more secure than WPA2, but the passphrase was still extracted.

### Step 10: Firewall Port Forwarding Rules

**File #b** - Firewall configuration

```bash
cat "jffs2-root/work/work/#b"
```

**Key findings - Port redirects (DNAT rules):**
```
config redirect
    option name 'DB'
    option src_dport '1778'
    option dest_ip '192.168.1.184'
    option dest_port '5881'

config redirect
    option name 'WEB'
    option src_dport '2289'
    option dest_ip '192.168.1.119'
    option dest_port '9889'

config redirect
    option name 'NAS'
    option src_dport '8088'
    option dest_ip '192.168.1.166'
    option dest_port '4431'
```

**What this reveals:**
- Three internal services exposed to WAN
- WAN ports: **1778, 2289, 8088**
- Internal hosts: DB server, Web server, NAS device
- These are potential attack vectors into the internal network

---

## Flag Retrieval

### Step 11: Connecting to the Challenge Service

We connected to the remote service which presented a series of questions:

```bash
nc 94.237.48.51 32551
```

### Step 12: Answering the Questions

Using the information extracted from the firmware:

1. **OpenWrt version:** Found in `/etc/openwrt_release`
   - Answer: `23.05.0`

2. **Linux kernel version:** From binwalk output (uImage header)
   - Answer: `5.15.134`

3. **Root password hash:** From JFFS2 overlay file #32
   - Answer: `root:$1$YfuRJudo$cXCiIJXn9fWLIt8WY2Okp1:19804:0:99999:7:::`

4. **PPPoE username:** From network config (file #4/network)
   - Answer: `yohZ5ah`

5. **PPPoE password:** From network config
   - Answer: `ae-h+i$i^Ngohroorie!bieng6kee7oh`

6. **WiFi SSID:** From wireless config (file #4/wireless)
   - Answer: `VLT-AP01`

7. **WiFi password:** From wireless config
   - Answer: `french-halves-vehicular-favorable`

8. **WAN port redirects:** From firewall config (file #b)
   - Answer: `1778,2289,8088`

### Step 13: Flag Obtained!

After correctly answering all questions, the service provided the flag:

```
HTB{Y0u'v3_m4st3r3d_0p3nWRT_d4t4_3xtr4ct10n!!_c21a6678c8f306f552d88c2748c603b9}
```

---

## Key Takeaways & Learning Points

### For a 2nd-year BSc IT Student:

1. **Firmware Structure Understanding:**
   - Firmware is like a computer's operating system stored in read-only memory
   - It contains both the OS and configuration data
   - OpenWrt uses layered filesystems (Squashfs + JFFS2 overlay)

2. **Why Two Filesystems?**
   - **Squashfs (read-only):** Base system, takes less space, faster to read
   - **JFFS2 (read-write):** Stores changes, allows persistence across reboots
   - Think of it like: Base Windows installation + Your personal files/settings

3. **Security Implications:**
   - Firmware dumps can reveal ALL configuration data
   - Passwords, network topology, exposed services
   - In real-world: Never expose physical devices with sensitive configs

4. **Tools Chain:**
   - `binwalk`: Scans for embedded files (like an X-ray for firmware)
   - `jefferson`: Extracts JFFS2 filesystems
   - `strings`, `grep`: Search for text patterns
   - `file`, `hexdump`: Examine file types and raw data

5. **Attack Surface Analysis:**
   - The port forwards (1778, 2289, 8088) expose internal services to the internet
   - Each is a potential entry point for attackers
   - Defense: Minimize exposed services, use VPN instead of direct forwards

---

## Clean-Up Note

All extracted temporary files were removed after completing the challenge:

```bash
rm -rf _chal_router_dump.bin.extracted/
```

**Session Status:** ✓ Kept alive as requested - ready for follow-up questions!

---

## Summary

This challenge demonstrated practical firmware analysis skills applicable to:
- IoT security assessment
- Router/device forensics
- Configuration recovery
- Penetration testing reconnaissance

The methodical approach of:
1. Identifying file structure (binwalk)
2. Extracting filesystems
3. Analyzing configuration files
4. Understanding how routers store persistent data

...is applicable to real-world security audits and incident response scenarios.

---

**Completion Time:** ~15 minutes  
**Difficulty Assessment:** Easy (with proper tools and methodology)  
**Skills Practiced:** Firmware analysis, filesystem extraction, configuration parsing, Linux basics
