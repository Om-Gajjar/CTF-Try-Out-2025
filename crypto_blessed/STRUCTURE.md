# Project Structure

```
crypto_blessed/
├── README.md                    # Main project readme (Quick start guide)
├── server.py                    # Challenge server code (reference)
├── setup.sh                     # Automated setup script
├── requirements.txt             # Python dependencies
├── validate.sh                  # Validation script
├── 
├── solvers/                     # Solver scripts (all working)
│   ├── solver.py               # ✅ Main solver (complete, tested)
│   ├── solver_verbose.py       # 📝 Verbose version with detailed logs
│   ├── solver_with_retry.py    # 🔄 Version with retry logic
│   ├── run_solver.sh           # Helper script to run solver
│   ├── test_solver.sh          # Environment verification
│   └── .gitignore              # Git ignore rules
│
└── documentation/               # All documentation
    ├── CHALLENGE_DOC.md        # Official challenge documentation
    ├── SOLUTION.md             # Complete solution writeup (detailed)
    ├── SOLVER_README.md        # Solver usage guide
    ├── QUICKSTART.txt          # Quick start instructions
    ├── OLD_SOLUTION_WRITEUP.md # Alternative writeup (archived)
    └── 2020-615.pdf            # Research paper reference
```

## File Descriptions

### Root Files
- **README.md** - Quick start guide with setup and usage instructions
- **server.py** - Original CTF challenge server code
- **setup.sh** - Automated installation script for dependencies
- **requirements.txt** - Python package dependencies
- **validate.sh** - Script to validate environment setup

### Solvers Directory
All solver files are **correct and working**:
- **solver.py** - Main production solver (use this)
- **solver_verbose.py** - Same as solver.py but with verbose logging
- **solver_with_retry.py** - Includes automatic retry logic for network issues
- **run_solver.sh** - Helper script: `./solvers/run_solver.sh`
- **test_solver.sh** - Verify SageMath and dependencies are installed

### Documentation Directory
- **CHALLENGE_DOC.md** - Official CTF challenge documentation (27KB)
- **SOLUTION.md** - Complete technical writeup (11KB, recommended)
- **SOLVER_README.md** - How to use the solver scripts
- **QUICKSTART.txt** - Quick reference guide
- **2020-615.pdf** - Academic paper on related cryptographic attacks

## Quick Start

```bash
# 1. Setup environment
./setup.sh

# 2. Activate sage (if using conda)
conda activate sage

# 3. Run solver
cd solvers
python solver.py
# OR
sage -python solver.py
# OR
./run_solver.sh
```

## Documentation Reading Order

1. **README.md** - Start here for quick setup
2. **documentation/QUICKSTART.txt** - Fast reference
3. **documentation/SOLVER_README.md** - Understand the solver
4. **documentation/SOLUTION.md** - Deep dive into the cryptography
5. **documentation/CHALLENGE_DOC.md** - Full challenge details

