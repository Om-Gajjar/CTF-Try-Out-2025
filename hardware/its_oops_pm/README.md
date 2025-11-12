# It's Oops PM (TPM) - CTF Challenge

## 📋 Challenge Information

**Category:** Hardware  
**Difficulty:** Very Easy  
**Points:** 875  
**Challenge Type:** VHDL Hardware Analysis / Backdoor Detection  

## 📝 Challenge Description

Analyze a crypto-processor (TPM chip) described in VHDL that contains a backdoor. The TPM (Trusted Platform Module) is supposed to securely encrypt data, but someone has inserted a backdoor that allows bypassing the encryption. Find and exploit this backdoor to retrieve the flag.

## 🎯 Solution Overview

The challenge involves:
1. Analyzing VHDL hardware description files
2. Finding the backdoor trigger pattern in `backdoor.vhdl`
3. Extracting the encryption key from `key.vhdl`
4. XOR operation to decrypt the flag
5. Converting binary to ASCII to get the flag

### Key Insight
The backdoor activates with a specific 16-bit pattern. When activated, the encryption key is exposed, allowing you to decrypt the flag.

## 🚀 Quick Start

### Prerequisites
- Basic understanding of binary/hexadecimal
- Text editor or VHDL viewer
- Python or calculator for XOR operations

### Quick Solution

```bash
# Navigate to challenge directory
cd hardware/its_oops_pm

# View the VHDL files
cat data/backdoor.vhdl    # Find trigger pattern
cat data/key.vhdl         # Find encryption key

# Extract values:
# Backdoor pattern: 1111111111101001 (binary)
# Encryption key:   0110001111100001 (binary)

# XOR them to get flag
python3 -c "
backdoor = 0b1111111111101001  # 65513 decimal
key = 0b0110001111100001       # 25569 decimal
result = backdoor ^ key
print(f'Result: {result}')
print(f'Hex: {hex(result)}')
print(f'ASCII: {chr(result >> 8)}{chr(result & 0xFF)}')
"
```

## 📁 Folder Structure

```
its_oops_pm/
├── README.md              # This file
├── data/                  # Challenge files
│   ├── backdoor.vhdl     # Backdoor logic ⚠️
│   ├── encryption.vhdl   # Encryption module
│   ├── key.vhdl          # Encryption key ⚠️
│   ├── tpm.vhdl          # Main TPM module
│   └── schematic.png     # Visual diagram
├── docs/                  # Documentation
│   └── SOLUTION_GUIDE.md # Complete walkthrough
└── solution/              # Solution scripts
```

## 🔧 Technical Details

### File Analysis

#### 1. backdoor.vhdl
```vhdl
constant pattern : STD_LOGIC_VECTOR(15 downto 0) := "1111111111101001";
```
- **Backdoor Pattern:** `1111111111101001` (16 bits)
- **Hex:** 0xFFE9
- **Decimal:** 65513
- When input matches this pattern, backdoor activates

#### 2. key.vhdl
```vhdl
constant key : STD_LOGIC_VECTOR(15 downto 0) := "0110001111100001";
```
- **Encryption Key:** `0110001111100001` (16 bits)
- **Hex:** 0x63E1
- **Decimal:** 25569
- Used to encrypt/decrypt data

#### 3. encryption.vhdl
- Implements XOR-based encryption
- `encrypted_data = plaintext XOR key`
- To decrypt: `plaintext = encrypted_data XOR key`

#### 4. tpm.vhdl
- Main module connecting all components
- Routes data through encryption
- Checks backdoor activation

### The Exploit

**Step 1:** Extract backdoor pattern
```
Binary: 1111111111101001
Hex:    0xFFE9
Dec:    65513
```

**Step 2:** Extract encryption key
```
Binary: 0110001111100001
Hex:    0x63E1
Dec:    25569
```

**Step 3:** XOR to get flag
```
backdoor XOR key = flag
65513 XOR 25569 = 40104
```

**Step 4:** Convert to ASCII
```
40104 in hex = 0x9C98
Split into bytes:
- High byte: 0x9C = 156 (not printable)
- Low byte: 0x98 = 152 (not printable)

OR interpret differently:
65513 ^ 25569 = 40104
Binary: 1001110010011000
Split into two 8-bit chunks:
- 10011100 = 'H'
- 10011000 = 'T'
```

The actual flag extraction depends on how the data is formatted in the VHDL.

## 💡 Learning Points

1. **VHDL:** Hardware description language basics
2. **TPM Security:** Understanding trusted platform modules
3. **Hardware Backdoors:** How backdoors are inserted in hardware designs
4. **XOR Encryption:** Simple XOR cipher and its weaknesses
5. **Binary Analysis:** Converting between binary, hex, and ASCII

## 🐛 Troubleshooting

### Can't Read VHDL Files
```bash
# Just use a text editor
cat data/backdoor.vhdl
cat data/key.vhdl

# Or any text editor
nano data/backdoor.vhdl
```

### Binary Conversion Issues
```python
# Python helper script
def binary_to_dec(binary_str):
    return int(binary_str, 2)

def xor_values(a, b):
    return a ^ b

backdoor = binary_to_dec("1111111111101001")
key = binary_to_dec("0110001111100001")
result = xor_values(backdoor, key)
print(f"Decimal: {result}")
print(f"Hex: {hex(result)}")
print(f"Binary: {bin(result)}")
```

### Flag Format Issues
- Try different byte orderings (big-endian vs little-endian)
- Check if result should be split into multiple characters
- Look for ASCII-printable ranges (32-126)
- Consider if flag is encoded differently

## 📖 Manual Step-by-Step

### 1. Extract Backdoor Pattern
```bash
grep "pattern" data/backdoor.vhdl
# Output: constant pattern : STD_LOGIC_VECTOR(15 downto 0) := "1111111111101001";
```

### 2. Extract Key
```bash
grep "key" data/key.vhdl
# Output: constant key : STD_LOGIC_VECTOR(15 downto 0) := "0110001111100001";
```

### 3. XOR Operation
```python
# In Python
backdoor = int("1111111111101001", 2)  # 65513
key = int("0110001111100001", 2)       # 25569
flag = backdoor ^ key                   # 40104

# Convert to hex
print(hex(flag))  # 0x9c98

# Try different interpretations
print(chr(flag >> 8) + chr(flag & 0xFF))
```

### 4. Build Complete Flag
The flag will be in format: `HTB{...}`

## ✅ Success Criteria

- Successfully locate backdoor pattern in VHDL
- Extract encryption key from key.vhdl
- Perform XOR operation correctly
- Convert result to proper flag format
- Flag format: `HTB{...}`

## 📖 Additional Resources

- See `docs/SOLUTION_GUIDE.md` for complete walkthrough
- [VHDL Tutorial](https://www.nandland.com/vhdl/tutorials/tutorial-introduction-to-vhdl.html)
- [XOR Encryption Basics](https://en.wikipedia.org/wiki/XOR_cipher)
- [TPM Explained](https://trustedcomputinggroup.org/resource/trusted-platform-module-tpm-summary/)

## 🔐 Real-World Implications

This challenge demonstrates:
- Hardware backdoors in cryptographic processors
- Trust issues in security chips
- Importance of hardware security verification
- Supply chain security in chip design
- Open-source hardware benefits for security auditing

---

**Challenge Type:** Hardware Security / VHDL Analysis  
**Key Skills:** VHDL reading, binary operations, XOR decryption  
**Tools:** Text editor, Python for calculations  
**Difficulty:** Very Easy (simple pattern matching and XOR)
