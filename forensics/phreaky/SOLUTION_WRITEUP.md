# CTF Challenge: "Phreaky" - Solution Writeup

**Challenge**: Phreaky  
**Category**: Forensics  
**Points**: 975  
**Difficulty**: Medium  

---

## Introduction

The "Phreaky" challenge presents a network forensics scenario where a mole within "The Phreaks" organization is leaking sensitive information to their rival faction, "The Talents." The challenge involves analyzing a packet capture (PCAP) file to identify the traitor, reconstruct fragmented and encrypted data, and retrieve the flag that proves successful mission completion.

The scenario description hints at:
- Network traffic analysis (PCAP file)
- Encrypted or obfuscated communications
- A mole sending "keys" to The Talents
- Need to identify the traitor and extract the flag

---

## Tools & Environment Check

### Available Tools
All necessary tools were pre-installed in the Kali Linux environment:

```bash
✓ tshark (Wireshark) 4.4.9 - Network protocol analyzer
✓ tcpdump version 4.99.5 - Packet capture tool
✓ wireshark - GUI packet analyzer
✓ strings - Extract printable strings from files
✓ grep - Text search utility
✓ openssl - Cryptography toolkit
✓ file - File type identification
✓ unzip - ZIP archive extraction
✓ pdftotext - PDF text extraction
```

No additional installations were required for this challenge.

---

## Packet Capture & File Reconnaissance

### Step 1: Initial File Extraction

The challenge provided a password-protected ZIP file:
```bash
# Extract with password "hackthebox"
unzip -P hackthebox forensics_phreaky.zip
```

This extracted: `phreaky.pcap` (7.0 MB)

### Step 2: Protocol Hierarchy Analysis

First, I examined the PCAP to understand what protocols were present:

```bash
tshark -r phreaky.pcap -q -z io,phs
```

**Key Findings**:
- **SMTP traffic** (337 frames, 54KB) - Email communications
- **TLS traffic** (278 frames) - Encrypted connections  
- **HTTP traffic** (18 frames) - Web traffic
- **DNS, DHCP, NTP** - Standard network services

The SMTP traffic was immediately suspicious given the scenario mentions "sending keys."

### Step 3: SMTP Stream Identification

I identified all TCP streams containing SMTP traffic:

```bash
tshark -r phreaky.pcap -Y "smtp" -T fields -e tcp.stream | sort -u
```

Found 30+ SMTP streams (streams 1-31).

### Step 4: Examining SMTP Communications

I analyzed the first SMTP stream:

```bash
tshark -r phreaky.pcap -q -z follow,tcp,ascii,1
```

**Critical Discovery**:
- **From**: caleb@thephreaks.com (Caleb)
- **To**: resources@thetalents.com
- **Subject**: Secure File Transfer
- **Content**: Base64-encoded ZIP attachment with password
- **Message**: "Attached is a part of the file. Password: S3W8yzixNoL8"

This immediately identified **Caleb** as the mole!

---

## Findings & Exploitation

### Step 5: Email Object Extraction

I extracted all email messages from the PCAP:

```bash
tshark -r phreaky.pcap --export-objects imf,smtp_analysis/
```

Result: **15 email messages**, each titled "Secure File Transfer"

### Step 6: Password and Attachment Inventory

Each email contained:
1. A password-protected ZIP file (base64-encoded)
2. A unique password
3. Part of a filename ending in `.zip`

| Email # | Password | Filename Hash (partial) |
|---------|----------|------------------------|
| 1 | S3W8yzixNoL8 | caf33472c6e0b2de... |
| 2 | r5Q6YQEcGWEF | 2c586ccfbbc90a11... |
| 3 | TVm9aC1UycxF | 9026fbe65473f451... |
| ... | ... | ... |
| 15 | gdOvbPtB0xCK | d0034e52b6d86170... |

### Step 7: Base64 Decoding and ZIP Extraction

I wrote a Python script to:
1. Parse each email file
2. Extract the base64-encoded attachment
3. Decode and save as ZIP file
4. Map each ZIP to its password

```python
import re, base64

for email_file in email_files:
    # Extract password
    password = re.search(r'Password:\s*(\S+)', content).group(1)
    
    # Extract and decode base64 attachment
    b64_match = re.search(r'Content-Transfer-Encoding: base64.*?\n\n(.*?)\n\n--=-=', 
                         content, re.DOTALL)
    decoded = base64.b64decode(b64_match.group(1).replace('\n', ''))
    
    # Save to file
    with open(zip_filename, 'wb') as f:
        f.write(decoded)
```

**Result**: 15 encrypted ZIP files extracted successfully

### Step 8: Decrypting ZIP Archives

Each ZIP was decrypted using its corresponding password:

```bash
unzip -P <password> <zipfile> -d parts/
```

**Contents discovered**:
- `phreaks_plan.pdf.part1` through `phreaks_plan.pdf.part15`
- File types varied: PDF header, OpenPGP data, ASCII text, binary data

### Step 9: File Reconstruction

The 15 parts formed a split PDF file. I concatenated them in order:

```bash
cat phreaks_plan.pdf.part{1..15} > phreaks_plan.pdf
file phreaks_plan.pdf
# Output: PDF document, version 1.3, 2 page(s)
```

### Step 10: PDF Analysis and Flag Extraction

The reconstructed PDF contained:

**Document Title**: "Operation Spotlight: The Phreaks' Grand Scheme Against The Talents"

**Content Summary**:
- Strategic plan for The Phreaks to attack The Talents
- Multi-phase cyber infiltration operation
- Details on malware deployment, DDoS attacks, and psychological operations
- Communication protocols for operatives

**Key Section - Appendix**:
```
Appendix: Communication Protocols

For secure communication, all operatives are required to use encrypted 
channels only. Coordination of the attack will follow predefined code 
phrases to maintain operational security. 

Key for secure communication: HTB{Th3Phr3aksReadyT0Att4ck}.
```

Extracted the flag:
```bash
pdftotext phreaks_plan.pdf - | grep -o "HTB{[^}]*}"
```

---

## Flag Retrieval

**FLAG**: `HTB{Th3Phr3aksReadyT0Att4ck}`

**Traitor Identified**: Caleb (caleb@thephreaks.com)

**Evidence**:
1. Caleb sent 15 emails to resources@thetalents.com (enemy organization)
2. Emails contained password-protected parts of The Phreaks' operational plan
3. The plan detailed a secret attack strategy against The Talents
4. The flag was embedded in the communication protocol key within the leaked document

---

## Solution Summary

### Attack Chain
1. **PCAP Analysis** → Identified SMTP traffic containing email communications
2. **Email Extraction** → Exported 15 email messages from packet capture
3. **Credential Harvesting** → Extracted 15 passwords from email bodies
4. **Attachment Decoding** → Decoded base64-encoded ZIP attachments
5. **Archive Decryption** → Decrypted ZIPs using extracted passwords
6. **File Reconstruction** → Concatenated 15 PDF parts into complete document
7. **Document Analysis** → Extracted text and located flag in appendix

### Key Techniques Used
- Protocol hierarchy analysis
- TCP stream following
- Email object export (IMF - Internet Message Format)
- Base64 encoding/decoding
- Password-protected archive extraction
- Split-file reconstruction
- PDF text extraction

### Learning Outcomes
This challenge demonstrated:
- Network forensics fundamentals
- SMTP protocol analysis
- Multi-stage data exfiltration detection
- File reconstruction from fragments
- MIME/email parsing
- Basic cryptanalysis (password-protected archives)

---

## Clean-Up Note

### Files Created During Analysis
```
/home/kali/Downloads/HTB CTF/forensics/phreaky/
├── phreaky.pcap (original capture)
├── smtp_analysis/
│   ├── *.eml (15 email files)
│   ├── *.zip (15 encrypted archives)
│   └── parts/
│       ├── phreaks_plan.pdf.part* (15 parts)
│       └── phreaks_plan.pdf (reconstructed)
└── SOLUTION_WRITEUP.md (this document)
```

### Session Status
- All analysis files remain intact for reference
- No system modifications were made
- No temporary files require deletion
- Session remains open for follow-up questions

### Recommendations for Second-Year IT Students
1. **Practice PCAP analysis** with Wireshark filtering and stream following
2. **Learn Python scripting** for automating data extraction tasks
3. **Understand email protocols** (SMTP, MIME, base64 encoding)
4. **Study file formats** (ZIP, PDF, split archives)
5. **Develop pattern recognition** for identifying anomalous network behavior

---

**Challenge Completed Successfully** ✓

Date: November 10, 2024  
Analyst: AI Assistant (GitHub Copilot CLI)  
Tools Used: tshark, Python 3, unzip, pdftotext, grep, bash scripting
