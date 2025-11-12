# Contributing to CTF-Try-Out-2025

Thank you for your interest in contributing to this CTF challenge solutions repository! This document provides guidelines for maintaining consistency and quality across all contributions.

## 📋 Table of Contents

- [Repository Organization Standards](#repository-organization-standards)
- [Challenge Structure](#challenge-structure)
- [Documentation Guidelines](#documentation-guidelines)
- [Code Standards](#code-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## 📂 Repository Organization Standards

### Standard Folder Structure

Every challenge MUST follow this structure:

```
challenge_name/
├── README.md              # Comprehensive documentation (REQUIRED)
├── solution/              # Solution scripts and exploits
│   ├── solve.py          # Main solution script
│   ├── requirements.txt  # Python dependencies (if needed)
│   └── *.sh             # Shell scripts (if applicable)
├── data/                  # Challenge data and artifacts
│   ├── flag.txt          # Retrieved flag (if applicable)
│   └── *.bin/*.pcap      # Challenge files
├── docs/                  # Additional documentation
│   ├── WRITEUP.md        # Detailed technical writeup
│   └── SOLUTION.md       # Alternative solution methods
├── src/                   # Source code (for challenges providing source)
│   └── challenge files
└── contracts/             # Smart contracts (blockchain challenges only)
```

### File Naming Conventions

- Use lowercase with underscores: `solve_script.py`
- Use hyphens for challenge folders: `challenge-name/`
- Be descriptive: `exploit_buffer_overflow.py` not `exploit.py`
- README files: Always `README.md` (uppercase)

## 📄 README.md Template

Every challenge README.md MUST include these sections:

```markdown
# Challenge Name - CTF Challenge

## 📋 Challenge Information
**Category:** [Misc/Web/Pwn/Rev/Crypto/Forensics/etc]
**Difficulty:** [Easy/Medium/Hard]
**Points:** [If known]
**Challenge Type:** [Brief type description]

## 📝 Challenge Description
[Clear description of the challenge]

## 🎯 Solution Overview
[High-level approach to solving]

## 🚀 Quick Start
### Prerequisites
### Installation
### Running the Solution

## 📁 Folder Structure
[Tree showing the challenge structure]

## 🔧 Technical Details
[Detailed vulnerability/approach analysis]

## 💡 Learning Points
[Educational takeaways]

## 🐛 Troubleshooting
[Common issues and solutions]

## 📖 Additional Resources
[Links to relevant documentation]

## ✅ Success Criteria
[How to verify solution works]

---
**Challenge Type:** [Summary]
**Key Skills:** [Skills demonstrated]
```

## 💻 Code Standards

### Python Scripts

```python
#!/usr/bin/env python3
"""
Challenge Name - Solution Script

Brief description of what this script does.

Target: [IP:Port or URL]
Category: [Category]
Vulnerability: [Vulnerability type]

Author: [Your name/handle]
Date: [YYYY-MM-DD]
"""

import sys
# Standard library imports first
# Then third-party imports
# Then local imports

# Use type hints where appropriate
def main() -> int:
    """Main execution function"""
    # Your code here
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Shell Scripts

```bash
#!/bin/bash
#
# Challenge Name - Solution Script
# Description: Brief description
# Author: Your name
#

set -e  # Exit on error

# Clear variable names
TARGET_HOST="localhost"
TARGET_PORT=1337

# Functions for reusability
function exploit() {
    echo "[*] Running exploit..."
    # Your code
}

# Main execution
main() {
    exploit
}

main "$@"
```

### Documentation in Code

- Add docstrings to all functions
- Comment complex logic
- Explain "why" not just "what"
- Use clear variable names that don't need comments

## 📝 Documentation Guidelines

### Writing Style

- **Be Clear:** Use simple, direct language
- **Be Comprehensive:** Cover all important aspects
- **Be Accurate:** Test all commands before documenting
- **Be Helpful:** Include troubleshooting and examples
- **Be Educational:** Explain the "why" behind techniques

### Command Examples

Always show complete, working examples:

```bash
# Good - Shows complete command with expected output
$ python3 solve.py target.htb 1337
[*] Connecting to target.htb:1337
[+] Flag: HTB{example}

# Bad - Incomplete or unclear
$ python solve.py
```

### Screenshots

- Include screenshots for GUI-based challenges
- Use annotations to highlight important areas
- Keep file sizes reasonable (< 1MB)
- Store in `docs/images/` directory

## 🔧 Requirements Files

### Python - requirements.txt

```txt
# Main dependencies
requests==2.31.0
pwntools==4.11.0

# Optional dependencies
# beautifulsoup4==4.12.0  # For HTML parsing
```

- Pin versions for reproducibility
- Add comments for optional dependencies
- Group related dependencies
- Keep it minimal - only actual requirements

## 📦 Commit Guidelines

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

### Types

- `feat:` New challenge organized
- `docs:` Documentation improvements
- `fix:` Bug fixes in solutions
- `refactor:` Code restructuring
- `chore:` Maintenance tasks

### Examples

```
feat: organize Misc/Character challenge with comprehensive docs

- Created proper folder structure
- Moved solve.py to solution/
- Added comprehensive README with socket programming details
- Enhanced script with colored output

Closes #123
```

## 🔍 Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b organize/challenge-name
   ```

2. **Make Changes**
   - Follow all standards above
   - Test your solutions
   - Update documentation

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: organize challenge-name"
   ```

4. **Push and Create PR**
   ```bash
   git push origin organize/challenge-name
   ```

5. **PR Description Must Include:**
   - What challenge(s) were organized
   - What changes were made
   - Any special considerations
   - Checklist of completed items

### PR Checklist

- [ ] README.md created with all required sections
- [ ] Files organized into proper folders
- [ ] Solution tested and working
- [ ] No sensitive data committed
- [ ] No temporary files committed
- [ ] Code follows style guidelines
- [ ] Documentation is clear and comprehensive

## ⚠️ Important Rules

### DO:
- ✅ Test all solutions before committing
- ✅ Document everything clearly
- ✅ Follow the standard structure
- ✅ Use descriptive names
- ✅ Include troubleshooting sections
- ✅ Add learning points

### DON'T:
- ❌ Commit sensitive data (real flags, credentials)
- ❌ Commit temporary files (.tmp, .swp, etc.)
- ❌ Commit large binary files unnecessarily
- ❌ Skip documentation
- ❌ Use unclear variable names
- ❌ Include personal paths in scripts

## 🆘 Getting Help

If you're unsure about any of these guidelines:

1. Look at existing organized challenges as examples
2. Check the CHANGELOG.md for recent changes
3. Review crypto_blessed as the reference template
4. Ask for clarification in issues

## 📚 References

- [Markdown Guide](https://www.markdownguide.org/)
- [Python PEP 8](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

**Thank you for contributing to making CTF challenges more accessible and educational!** 🎉
