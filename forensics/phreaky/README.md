# Phreaky - CTF Challenge

## 📋 Challenge Information

**Category:** Forensics  
**Difficulty:** Medium  
**Points:** 975  
**Challenge Type:** Network Forensics / PCAP Analysis  

## 📝 Challenge Description

A network forensics challenge involving packet capture analysis. A mole within "The Phreaks" organization is leaking sensitive information to their rival faction "The Talents." Analyze the PCAP file to identify the traitor, reconstruct fragmented and encrypted data, and retrieve the flag.

## 🎯 Solution Overview

The challenge involves:
1. Analyzing network traffic in PCAP file
2. Identifying encrypted or obfuscated communications
3. Extracting and reconstructing fragmented data
4. Decrypting transmitted information
5. Identifying the mole and retrieving the flag

## 🚀 Quick Start

### Prerequisites
- Wireshark / tshark - Network protocol analyzer
- tcpdump - Packet capture tool
- openssl - Cryptography toolkit
- strings, grep, file utilities

### Installation
```bash
# All tools typically pre-installed on Kali Linux
sudo apt install wireshark tshark tcpdump openssl
```

### Running the Analysis
```bash
# Navigate to challenge directory
cd forensics/phreaky

# Extract the PCAP if zipped
unzip data/forensics_phreaky.zip -d data/

# Analyze with Wireshark (GUI)
wireshark data/phreaky.pcap

# Or use command-line tools
tshark -r data/phreaky.pcap
tcpdump -r data/phreaky.pcap -nn

# Look for specific protocols
tshark -r data/phreaky.pcap -Y "http or ftp or smtp"

# Extract files
tshark -r data/phreaky.pcap --export-objects http,exported/
```

## 📁 Folder Structure

```
phreaky/
├── README.md                  # This file
├── data/                      # Challenge files
│   ├── forensics_phreaky.zip # Original challenge archive
│   └── phreaky.pcap          # Network capture file
├── docs/                      # Documentation
│   └── SOLUTION_WRITEUP.md   # Detailed solution writeup
└── solution/                  # Solution scripts
```

## 🔧 Technical Details

### PCAP Analysis Steps

1. **Initial Reconnaissance**
   ```bash
   # Get capture statistics
   capinfos phreaky.pcap
   
   # List conversations
   tshark -r phreaky.pcap -q -z conv,ip
   tshark -r phreaky.pcap -q -z conv,tcp
   ```

2. **Protocol Analysis**
   ```bash
   # HTTP traffic
   tshark -r phreaky.pcap -Y "http" -T fields -e http.request.uri
   
   # DNS queries
   tshark -r phreaky.pcap -Y "dns" -T fields -e dns.qry.name
   
   # FTP commands
   tshark -r phreaky.pcap -Y "ftp"
   ```

3. **File Extraction**
   ```bash
   # Export HTTP objects
   tshark -r phreaky.pcap --export-objects http,output/
   
   # Extract FTP data
   tshark -r phreaky.pcap -Y "ftp-data" -T fields -e data
   ```

4. **Encrypted Data**
   - Look for SSL/TLS traffic
   - Check for custom encryption schemes
   - Search for keys in plaintext protocols
   - Use openssl to decrypt if keys are found

5. **Flag Extraction**
   ```bash
   # Search for flag pattern
   strings phreaky.pcap | grep -i "htb{"
   tshark -r phreaky.pcap -Y "frame contains HTB"
   ```

### Common Analysis Patterns

- **Follow TCP Streams:** Reconstruct full conversations
- **Export Objects:** Extract transmitted files
- **Protocol Hierarchy:** Identify unusual protocols
- **Timing Analysis:** Look for patterns in transmission times
- **Payload Inspection:** Search for encoded/encrypted data

## 💡 Learning Points

1. **Network Forensics:** Analyzing packet captures
2. **Protocol Analysis:** Understanding network protocols
3. **Data Reconstruction:** Reassembling fragmented data
4. **Cryptography:** Identifying and breaking encryption
5. **Wireshark Skills:** Effective use of filters and tools

## 🐛 Troubleshooting

### Large PCAP File
- Use display filters to reduce data
- Focus on specific protocols or IPs
- Export only relevant streams

### Encrypted Traffic
- Look for keys in earlier packets
- Check for weak encryption schemes
- Search for authentication credentials

### Missing Data
- Ensure all packets are captured
- Check for packet loss indicators
- Verify PCAP file integrity

## 📖 Additional Resources

- See `docs/SOLUTION_WRITEUP.md` for complete solution
- [Wireshark User Guide](https://www.wireshark.org/docs/wsug_html_chunked/)
- [tshark Documentation](https://www.wireshark.org/docs/man-pages/tshark.html)
- [PCAP Analysis Techniques](https://www.sans.org/white-papers/)

## ✅ Success Criteria

- Successfully analyze network traffic
- Identify the mole's communications
- Extract and decrypt transmitted data
- Reconstruct fragmented information
- Retrieve the flag
- Flag format: `HTB{...}`

---

**Challenge Type:** Network Forensics  
**Key Skills:** PCAP analysis, protocol inspection, data reconstruction  
**Tools:** Wireshark, tshark, tcpdump, openssl  
**Difficulty:** Medium (requires network analysis experience)
