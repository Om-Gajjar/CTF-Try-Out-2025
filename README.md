# CTF-Try-Out-2025

## 🏆 CTF Challenge Solutions Repository

This repository contains organized solutions and comprehensive documentation for CTF challenges from various categories. Each challenge has been carefully documented with setup instructions, solution methodologies, and learning resources.

## 📂 Repository Structure

```
CTF-Try-Out-2025/
├── Misc/                  # Miscellaneous challenges (6 challenges) ✓
├── blockchain/            # Smart contract challenges (1 challenge) ✓
├── coding/                # Programming challenges (1 challenge) ✓
├── crypto_blessed/        # Cryptography challenges (1 challenge) ✓
├── forensics/             # Digital forensics (3 challenges) ✓
├── hardware/              # Hardware security (3 challenges)
├── pwn/                   # Binary exploitation (5 challenges)
├── rev/                   # Reverse engineering (5 challenges)
├── web/                   # Web security (8 challenges)
├── LICENSE                # Repository license
└── README.md              # This file
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

### pwn - Binary Exploitation (5/5) ✓
1. **getting_started** - Buffer overflow introduction
2. **abyss** - Format string vulnerability
3. **labyrinth** - Stack overflow + canary bypass
4. **regularity** - Advanced stack exploitation
5. **void** - Multi-protection bypass / ret2libc

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

**All categories complete!** 🎉

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

### Prerequisites
- Docker (for containerized challenges)
- Python 3.6+ (for exploit scripts)
- Common CTF tools (pwntools, web3, requests, etc.)

### Running a Challenge

```bash
# Navigate to the challenge directory
cd category/challenge_name

# Read the documentation
cat README.md

# Install dependencies (if needed)
pip install -r solution/requirements.txt

# Run the solution
python3 solution/solve.py
```

## 🛠️ Tools & Technologies

### Common Tools Used
- **Python** - Main scripting language
- **Pwntools** - Binary exploitation
- **Web3.py** - Blockchain interaction
- **Requests** - HTTP client
- **Wireshark/tshark** - Network analysis
- **Binwalk** - Firmware analysis
- **Foundry/Cast** - Smart contract tools
- **Docker** - Challenge containerization

### Languages & Frameworks
- Python, JavaScript, Solidity
- Express.js, FastAPI, Flask
- Node.js, Web3
- Bash scripting

## 📚 Learning Resources

Each challenge includes learning points and links to:
- Official documentation
- Security best practices
- OWASP guidelines
- Tool documentation
- CTF technique guides

## 🏅 Challenge Statistics

- **Total Challenges:** 31
- **Organized:** 31 (100%) ✅
- **Categories Complete:** 9/9 (100%) ✅
- **Documentation:** 31 comprehensive READMEs
- **Solution Scripts:** 31+ working exploits

## 📝 Contributing

This repository follows best practices for CTF solution documentation:
- Clear, comprehensive READMEs
- Well-commented code
- Proper folder organization
- No sensitive data in commits
- Educational focus

**Status:** ✅ Fully Organized  
**All 31 challenges across 9 categories complete!**

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🤝 Acknowledgments

- HackTheBox for the challenges
- CTF community for methodologies
- Security researchers for techniques

---

**Status:** ✅ 100% Complete  
**Last Updated:** 2025-11-12  
**Completion:** All 31 challenges organized across 9 categories