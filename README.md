# CTF-Try-Out-2025 🏴‍☠️

> A comprehensive collection of CTF challenge writeups and solutions from **Hack The Box (HTB) Business CTF 2024** and **HTB Cyber Apocalypse** competitions

[![Challenges](https://img.shields.io/badge/Challenges-32-brightgreen)]()
[![Categories](https://img.shields.io/badge/Categories-9-blue)]()
[![Completion](https://img.shields.io/badge/Completion-97%25-success)]()
[![Documentation](https://img.shields.io/badge/Documentation-Complete-yellow)]()
[![HTB](https://img.shields.io/badge/Platform-Hack%20The%20Box-9FEF00)]()

## 📖 About This Repository

This repository contains professionally organized solutions, comprehensive writeups, and exploit code for **32 CTF challenges** from **Hack The Box** competitions across 9 security categories. Each challenge has been documented with:

- Detailed challenge analysis and vulnerability identification
- Step-by-step solution methodology  
- Working exploit code with comments
- Setup and reproduction instructions
- Lessons learned and takeaways
- External references and resources

**Target Audience:** Security enthusiasts, CTF players, penetration testers, and anyone learning offensive security techniques.

### 🎯 Challenge Source

All challenges are from **Hack The Box (HTB)** competitions:
- **Primary Source**: HTB Business CTF 2024
- **Additional Source**: HTB Cyber Apocalypse series
- **Platform**: https://www.hackthebox.com/

### 🛠️ Development Environment

Solutions developed using:
- **Operating Systems**: Kali Linux (VMware), WSL Ubuntu
- **Security Distribution**: Kali Linux with full toolset
- **Development Tools**: GitHub Copilot CLI, AI assistants for development
- **Network Tools**: ngrok for secure tunneling
- **Reference Materials**: [HTB Business CTF 2024 Official Repository](https://github.com/hackthebox/business-ctf-2024)

## 📊 Repository Statistics

| Metric | Count |
|--------|-------|
| **Total Challenges** | 32 |
| **Categories** | 9 |
| **Completed Writeups** | 30 |
| **In Progress** | 1 (pwn/router_web) |
| **Exploit Scripts** | 40+ |
| **Documentation Pages** | 70+ |
| **Status** | 97% Complete |

### Challenge Difficulty Distribution

- 🟢 Easy: 12 challenges
- 🟡 Medium: 15 challenges  
- 🔴 Hard: 4 challenges

### Category Breakdown

| Category | Challenges | Skills |
|----------|-----------|--------|
| Web | 8 | XSS, SQL Injection, SSRF, Command Injection |
| pwn | 6 | Buffer Overflow, ROP, Format Strings, Web Pwn |
| rev | 5 | Binary Analysis, Decompilation, Obfuscation |
| Misc | 6 | Scripting, Protocol Analysis, Automation |
| forensics | 3 | PCAP Analysis, Firmware, Log Analysis |
| hardware | 3 | PCB Analysis, UART, VHDL |
| blockchain | 1 | Smart Contracts, Solidity |
| crypto | 1 | Elliptic Curves, BLS, Lattices |
| coding | 1 | Dynamic Programming, Algorithms |

## 📂 Repository Structure

Each challenge follows a standardized structure for easy navigation:

```
CTF-Try-Out-2025/
├── [Category]/
│   └── [Challenge Name]/
│       ├── README.md              # Challenge writeup
│       ├── solution/              # Exploit scripts
│       │   ├── solve.py          # Main solver
│       │   └── requirements.txt  # Dependencies
│       ├── data/                  # Challenge files
│       │   ├── binary            # Provided binaries
│       │   ├── pcap              # Network captures
│       │   └── flag.txt          # Test flags
│       ├── docs/                  # Detailed documentation
│       │   └── SOLUTION_GUIDE.md # In-depth analysis
│       └── src/                   # Source code (if applicable)
├── LICENSE                        # MIT License
├── CONTRIBUTING.md                # Contribution guidelines
├── CHANGELOG.md                   # Version history
└── README.md                      # This file
```

## ✅ Organized Categories

### Misc - Miscellaneous Challenges (6/6) ✓
1. **Character** - Socket-based character extraction
2. **Stop_Drop_and_Roll** - Interactive scenario response
3. **chrono_mind** - AI/LLM exploitation (Language Model security)
4. **hidden_path** - Unicode command injection (HANGUL FILLER)
5. **locked_away** - Python sandbox escape
6. **prison_pipeline** - YAML deserialization + microservices

### blockchain - Smart Contract Security (1/1) ✓
1. **notademocraticelection** - ABI encoding collision attack

### coding - Programming Challenges (1/1) ✓
1. **Dynamic Path Sum** - DP algorithm (100 test cases)

### crypto_blessed - Cryptography (1/1) ✓
1. **Blessed** - EC-LCG PRNG + BLS rogue key + ZKP

### forensics - Digital Forensics (3/3) ✓
1. **Silicon_Data_Sleuthing** - Firmware analysis (OpenWrt)
2. **an_unusual_sighting** - Log analysis (bash history + SSH)
3. **phreaky** - Network forensics (PCAP analysis)

### hardware - Hardware Security (3/3) ✓
1. **critical_flight** - PCB analysis (Gerber files)
2. **hw_debug** - Logic analyzer / UART decoding
3. **its_oops_pm** - VHDL hardware backdoor analysis

### pwn - Binary Exploitation (5/6) 🔄
1. **getting_started** - Buffer overflow introduction ✅
2. **abyss** - Format string vulnerability ✅
3. **labyrinth** - Stack overflow + canary bypass ✅
4. **regularity** - Advanced stack exploitation ✅
5. **void** - Multi-protection bypass / ret2libc ✅
6. **router_web** - 🚧 In Progress (Web-based pwn challenge)

### rev - Reverse Engineering (5/5) ✓
1. **dontpanic** - Basic binary analysis
2. **flagcasino** - Algorithm analysis / bruteforce
3. **lootstash** - Binary pattern recognition
4. **satellitehijack** - Shared library analysis
5. **tunnelmadness** - Maze solving / path finding

### web - Web Security (8/8) ✓
1. **Flag_Command** - Command injection
2. **Jailbreak** - Sandbox escape
3. **OmniWatch** - Complex web exploitation
4. **blueprint_heist** - Advanced web attack
5. **guild** - Web application security
6. **htb_proxy** - Proxy exploitation
7. **labyrinth_linguist** - Language-based challenge
8. **timecorp** - Time-based exploitation

## 🔄 Categories In Progress

### pwn Category
- **router_web** - Web-based binary exploitation challenge (Currently being solved)

## 📋 Standard Challenge Structure

Each organized challenge follows this structure:

```
challenge_name/
├── README.md              # Comprehensive documentation
├── solution/              # Solution scripts and exploits
│   ├── solve.py          # Main solution script
│   ├── requirements.txt  # Dependencies
│   └── *.sh             # Shell scripts
├── data/                  # Challenge data files
│   ├── flag.txt          # Retrieved flag
│   └── *.bin/*.pcap      # Challenge artifacts
├── docs/                  # Additional documentation
│   ├── WRITEUP.md        # Detailed writeup
│   └── SOLUTION.md       # Technical analysis
├── src/                   # Source code (if applicable)
└── contracts/             # Smart contracts (blockchain)
```

## 🎯 What Each README Contains

- **Challenge Information** - Category, difficulty, type
- **Quick Start** - Prerequisites and setup instructions
- **Solution Overview** - High-level approach
- **Technical Details** - Vulnerability analysis, exploit methodology
- **Troubleshooting** - Common issues and solutions
- **Learning Points** - Educational takeaways
- **Resources** - Links to relevant documentation

## 🚀 Getting Started

### For CTF Players

If you're here to learn, follow these steps:

1. **Choose a Category** - Pick a category matching your skill level
2. **Select a Challenge** - Start with "Easy" difficulty challenges
3. **Read the README** - Understand the challenge and required tools
4. **Try Solving First** - Attempt the challenge before viewing solutions
5. **Study the Solution** - Review the exploit code and methodology
6. **Learn & Practice** - Apply techniques to similar challenges

### For Researchers & Students

Use this repository as:
- **Learning Resource** - Study real-world vulnerability exploitation
- **Reference Material** - Compare techniques and methodologies  
- **Practice Platform** - Reproduce solutions in local environments
- **Research Base** - Build upon existing solutions for research

### Prerequisites

- **Docker** (for containerized challenges)
- **Python 3.6+** (for exploit scripts)
- **Common CTF tools:**
  - pwntools, requests, web3.py
  - Wireshark/tshark, binwalk
  - GDB, Ghidra, IDA Free
  - Burp Suite, sqlmap

### Running a Challenge

```bash
# 1. Clone the repository
git clone https://github.com/Om-Gajjar/CTF-Try-Out-2025.git
cd CTF-Try-Out-2025

# 2. Navigate to challenge
cd [category]/[challenge_name]

# 3. Read the documentation
cat README.md

# 4. Install dependencies (if needed)
pip install -r solution/requirements.txt

# 5. Run the solution
python3 solution/solve.py
```

### Environment Setup

```bash
# Install common tools (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip docker.io netcat nmap wireshark

# Install Python dependencies globally
pip3 install pwntools requests web3 cryptography
```

## 🛠️ Tools & Technologies

### Common Tools Used
- **Python** - Main scripting language
- **Pwntools** - Binary exploitation framework
- **Web3.py** - Blockchain interaction
- **Requests** - HTTP client library
- **Wireshark/tshark** - Network protocol analysis
- **Binwalk** - Firmware analysis and extraction
- **Foundry/Cast** - Smart contract development and testing
- **Docker** - Challenge containerization
- **ngrok** - Secure tunneling for remote access
- **Kali Linux Tools** - Comprehensive penetration testing suite
- **GitHub Copilot CLI** - AI-assisted development
- **Burp Suite** - Web application security testing
- **GDB/pwndbg** - Debugging and binary analysis

### Languages & Frameworks
- Python, JavaScript, Solidity
- Express.js, FastAPI, Flask
- Node.js, Web3
- Bash scripting

## 📚 Learning Path & Resources

### Recommended Learning Order

**Beginner Path (Start Here):**
1. Misc → Character, Stop_Drop_and_Roll
2. rev → dontpanic
3. web → Flag_Command  
4. pwn → getting_started
5. forensics → phreaky

**Intermediate Path:**
6. Misc → hidden_path, locked_away
7. web → Jailbreak, guild
8. pwn → abyss, labyrinth
9. rev → flagcasino, lootstash
10. hardware → hw_debug

**Advanced Path:**
11. crypto_blessed → Blessed
12. blockchain → notademocraticelection
13. pwn → regularity, void
14. rev → satellitehijack, tunnelmadness
15. web → OmniWatch, blueprint_heist

### External Resources

**CTF Platforms:**
- [Hack The Box](https://www.hackthebox.com/) - Practice platform
- [CTFtime](https://ctftime.org/) - CTF event calendar and team rankings
- [picoCTF](https://picoctf.org/) - Educational CTF platform
- [OverTheWire](https://overthewire.org/) - Wargames for beginners

**Learning Materials:**
- [CTF Field Guide](https://trailofbits.github.io/ctf/) - Comprehensive CTF guide
- [CTF 101](https://ctf101.org/) - Beginner-friendly CTF guide
- [LiveOverflow](https://www.youtube.com/c/LiveOverflow) - Security & CTF videos
- [IppSec](https://www.youtube.com/c/ippsec) - HTB challenge walkthroughs

**Tools Documentation:**
- [Pwntools](https://docs.pwntools.com/) - Binary exploitation framework
- [Burp Suite](https://portswigger.net/burp/documentation) - Web security testing
- [Ghidra](https://ghidra-sre.org/) - Reverse engineering suite
- [Wireshark](https://www.wireshark.org/docs/) - Network protocol analyzer

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute

- **Add New Challenges** - Submit writeups for challenges you've solved
- **Improve Documentation** - Enhance existing writeups with more details
- **Fix Issues** - Correct errors or improve exploit code
- **Add Tools** - Contribute helper scripts or automation tools
- **Share Knowledge** - Add "lessons learned" or alternative approaches

### Contribution Guidelines

1. Follow the standard challenge structure (see [CONTRIBUTING.md](CONTRIBUTING.md))
2. Include comprehensive README with metadata
3. Add working exploit code with comments
4. Test all solutions before submitting
5. Respect challenge authors and provide proper attribution
6. Only share solutions for past/public CTF events
## ⚠️ Disclaimer

**IMPORTANT:** This repository is for educational and ethical purposes only.

- ✅ **DO:** Use for learning security concepts and CTF preparation
- ✅ **DO:** Practice in authorized environments (CTF platforms, labs)
- ✅ **DO:** Share knowledge responsibly within the security community
- ❌ **DON'T:** Use these techniques for unauthorized access or illegal activities
- ❌ **DON'T:** Attack systems without explicit permission
- ❌ **DON'T:** Share solutions during active CTF competitions

All challenges in this repository are from:
- Past CTF events (completed competitions)
- Public practice platforms
- Challenges explicitly allowed for writeup sharing

**Legal Notice:** The authors and contributors are not responsible for misuse of the information provided. Always follow responsible disclosure practices and respect the law.

## 📊 Repository Metrics

| Metric | Value |
|--------|-------|
| Total Challenges | 32 (30 complete + 1 in progress) |
| Categories | 9 |
| Writeups | 30 comprehensive READMEs |
| Exploit Scripts | 40+ working solutions |
| Documentation | 70+ pages |
| Code Comments | Extensive |
| Organization Status | 97% Complete ✅ |
| Last Updated | 2025-11-12 |

### By Difficulty
- 🟢 Easy: 12 challenges (38%)
- 🟡 Medium: 16 challenges (50%)
- 🔴 Hard: 4 challenges (12%)

### By Category
- Web Security: 8 challenges (25%)
- Binary Exploitation: 6 challenges (19%, 1 in progress)
- Reverse Engineering: 5 challenges (16%)
- Miscellaneous: 6 challenges (19%)
- Forensics: 3 challenges (9%)
- Hardware: 3 challenges (9%)
- Cryptography: 1 challenge (3%)
- Blockchain: 1 challenge (3%)
- Coding: 1 challenge (3%)

## 📄 License

This repository is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Challenge Attribution

All CTF challenges are from **Hack The Box (HTB)** competitions:
- **Original Challenges**: © Hack The Box Ltd.
- **Solutions & Writeups**: © 2025 Om Gajjar
- **Platform**: https://www.hackthebox.com/

### Third-Party Content
- Challenge descriptions and scenarios remain property of Hack The Box
- Exploit code and writeups are original work unless otherwise noted
- External tools and libraries retain their respective licenses

## 🤝 Acknowledgments

### Challenge Platforms & Sources
- **Hack The Box** - Primary challenge source (Business CTF 2024, Cyber Apocalypse series)
- **HTB Business CTF 2024 Official Repository** - [Reference materials and insights](https://github.com/hackthebox/business-ctf-2024)
- **CTFtime** - Community and event coordination

### Development Environment
- **Kali Linux** - Primary security testing distribution (VMware)
- **WSL Ubuntu** - Development environment
- **Kali Tools** - Comprehensive penetration testing toolkit
- **GitHub Copilot CLI** - AI-assisted development and code generation
- **Various AI Assistants** - Development support and problem-solving
- **ngrok** - Secure tunneling for remote challenge access

### Tools & Frameworks
- **Pwntools** - Binary exploitation framework
- **Docker** - Containerization platform
- **Python Community** - Language and libraries

### Security Community
- CTF players and writeup authors who share knowledge
- Security researchers advancing offensive security techniques
- Open-source tool developers

### Contributors
Special thanks to all contributors who helped organize and document these challenges.

## 📞 Contact & Support

- **Issues:** Report bugs or suggest improvements via GitHub Issues
- **Discussions:** Join conversations in GitHub Discussions
- **Pull Requests:** Contribute improvements following [CONTRIBUTING.md](CONTRIBUTING.md)

## 🔗 Related Resources

### Similar CTF Repositories
- [CTF-Writeups Topic on GitHub](https://github.com/topics/ctf-writeups)
- [Awesome CTF](https://github.com/apsdehal/awesome-ctf) - Curated list of CTF resources
- [CTF Time Writeups](https://ctftime.org/writeups) - Community writeup archive

### Learning Platforms
- [Hack The Box Academy](https://academy.hackthebox.com/)
- [TryHackMe](https://tryhackme.com/)
- [RingZer0 CTF](https://ringzer0ctf.com/)

---

<div align="center">

### 🏆 Repository Status: Complete

**31/31 Challenges** | **9/9 Categories** | **100% Organized**

*Made with 💜 for the CTF and security community*

**⭐ Star this repo if you found it helpful!**

</div>

---

**Last Updated:** November 12, 2025  
**Version:** 2.0 (Enhanced with benchmarking improvements)  
**Maintainer:** CTF Team