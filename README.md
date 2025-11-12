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

## 🔄 Categories In Progress

### hardware - Hardware Security (3 challenges)
- critical_flight
- hw_debug
- its_oops_pm

### pwn - Binary Exploitation (5 challenges)
- abyss
- getting_started
- labyrinth
- regularity
- void

### rev - Reverse Engineering (5 challenges)
- dontpanic
- flagcasino
- lootstash
- satellitehijack
- tunnelmadness

### web - Web Security (8 challenges)
- Flag_Command
- Jailbreak
- OmniWatch
- blueprint_heist
- guild
- htb_proxy
- labyrinth_linguist
- timecorp

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

- **Total Challenges:** 31+
- **Organized:** 15 (48%)
- **Categories Complete:** 4/9 (44%)
- **Documentation:** 15 comprehensive READMEs
- **Solution Scripts:** 15+ working exploits

## 📝 Contributing

This repository follows best practices for CTF solution documentation:
- Clear, comprehensive READMEs
- Well-commented code
- Proper folder organization
- No sensitive data in commits
- Educational focus

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🤝 Acknowledgments

- HackTheBox for the challenges
- CTF community for methodologies
- Security researchers for techniques

---

**Status:** Active Development  
**Last Updated:** 2025-11  
**Completion:** 48% organized