# An Unusual Sighting - CTF Challenge

## 📋 Challenge Information

**Category:** Forensics  
**Difficulty:** Easy  
**Challenge Type:** Log Analysis / Linux Forensics  

## 📝 Challenge Description

Analyze bash history and SSH logs to investigate suspicious activity on a Linux system. Identify unauthorized access, commands executed, and extract evidence of system compromise.

## 🎯 Solution Overview

The challenge involves:
1. Analyzing bash command history
2. Reviewing SSH authentication logs
3. Identifying suspicious commands or access patterns
4. Reconstructing the attack timeline
5. Extracting the flag from logged activity

## 🚀 Quick Start

### Prerequisites
- Basic Linux command-line knowledge
- Text analysis tools (grep, awk, sed)
- Understanding of SSH logs and bash history

### Running the Analysis
```bash
# Navigate to challenge directory
cd forensics/an_unusual_sighting

# Analyze bash history
cat data/bash_history.txt
grep -i "flag\|pass\|secret\|key" data/bash_history.txt

# Review SSH logs
cat data/sshd.log
grep "Accepted\|Failed" data/sshd.log
grep -i "unusual\|suspicious" data/sshd.log

# Look for patterns
awk '{print $1, $2, $3}' data/sshd.log | sort | uniq -c
```

## 📁 Folder Structure

```
an_unusual_sighting/
├── README.md              # This file
├── data/                  # Challenge files
│   ├── bash_history.txt  # Bash command history
│   └── sshd.log          # SSH daemon logs
├── docs/                  # Additional documentation
└── solution/              # Solution scripts
```

## 🔧 Technical Details

### Analysis Steps

1. **Bash History Analysis**
   - Review executed commands
   - Look for suspicious activity (downloads, exfiltration, privilege escalation)
   - Identify encoded or obfuscated commands
   - Check for curl/wget with unusual URLs

2. **SSH Log Analysis**
   - Identify successful logins
   - Check for brute force attempts
   - Review IP addresses and usernames
   - Look for unusual login times or patterns

3. **Timeline Reconstruction**
   - Correlate bash history with SSH login times
   - Identify when unauthorized access occurred
   - Map commands to specific sessions

4. **Flag Extraction**
   - Look for base64 encoded strings
   - Check for hex encoded data
   - Search for HTB{} pattern
   - Decode any suspicious strings

### Common Patterns to Look For

```bash
# Encoded commands
echo "..." | base64 -d
echo "..." | xxd -r -p

# Downloads
curl http://...
wget http://...

# Data exfiltration
nc -e /bin/bash ...
cat /etc/passwd | ...

# Privilege escalation
sudo su
chmod +s ...
```

## 💡 Learning Points

1. **Log Analysis:** Understanding Linux system logs
2. **Bash History:** Interpreting command history
3. **SSH Forensics:** Analyzing authentication logs
4. **Encoding:** Recognizing and decoding obfuscated data
5. **Timeline Analysis:** Reconstructing attack sequences

## 🐛 Troubleshooting

### No Flag Found
- Check for encoded strings (base64, hex)
- Review all commands, not just suspicious ones
- Look in SSH logs for transmitted data
- Search for patterns like "flag", "htb", "HTB{"

### Multiple Suspicious Activities
- Focus on the most recent or unusual
- Look for commands that output to files
- Check for network-related commands

## ✅ Success Criteria

- Successfully analyze bash history
- Identify suspicious SSH activity
- Reconstruct attack timeline
- Extract and decode the flag
- Flag format: `HTB{...}`

---

**Challenge Type:** Log Forensics  
**Key Skills:** Linux forensics, log analysis, pattern recognition  
**Difficulty:** Easy (requires basic log analysis)
