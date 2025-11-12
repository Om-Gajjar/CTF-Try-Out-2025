# HTB Challenge: It's Oops PM - Complete Solution Guide

## Challenge Information
- **Name:** It's Oops PM
- **Category:** Hardware
- **Difficulty:** Very Easy
- **Points:** 875

---

## Challenge Description
The challenge involves analyzing a crypto-processor (TPM chip) described in VHDL that contains a backdoor. The goal is to find and exploit this backdoor to retrieve the flag.

---

## Step-by-Step Solution Process

### **Step 1: Understand the Files**

You'll receive 5 files:
1. `backdoor.vhdl` - Contains the backdoor logic
2. `encryption.vhdl` - Handles data encryption
3. `key.vhdl` - Stores the encryption key
4. `tpm.vhdl` - Main module that connects everything
5. `schematic.png` - Visual diagram (optional)

---

### **Step 2: Analyze the Backdoor (`backdoor.vhdl`)**

```vhdl
constant pattern : STD_LOGIC_VECTOR(15 downto 0) := "1111111111101001";
```

**Key Finding:**
- The backdoor activates when input matches: `1111111111101001`
- This is a 16-bit binary pattern
- When matched, output `B` becomes '1' (TRUE)

**Convert to decimal (optional):**
- Binary: `1111111111101001`
- Hex: `0xFFE9`
- Decimal: `65513`

---

### **Step 3: Analyze the Key (`key.vhdl`)**

```vhdl
constant key : STD_LOGIC_VECTOR(15 downto 0) := "0110001111100001";
```

**Key Information:**
- The secret encryption key is: `0110001111100001`
- Binary: `0110001111100001`
- Hex: `0x63E1`
- Decimal: `25569`

---

### **Step 4: Understand the Encryption (`encryption.vhdl`)**

```vhdl
for i in 1 to 15 loop
    E(i) <= D(i) XOR K(i);
end loop;

E(0) <= NOT K(0);
E(6) <= NOT K(6);
E(13) <= NOT K(13);
```

**How it works:**
- Most bits: `Output = Input XOR Key`
- Bits 0, 6, 13: `Output = NOT Key[bit]`
- This encrypts the input data

---

### **Step 5: Analyze the Main TPM Module (`tpm.vhdl`)**

```vhdl
case B is
    when '1' =>
        Output(i) <= Key(i);  -- Backdoor: Output the key!
    when others =>
        Output(i) <= Encrypted(i);  -- Normal: Output encrypted data
end case;
```

**Critical Vulnerability:**
- **Normal mode (B='0'):** Input gets encrypted → Output is encrypted data
- **Backdoor mode (B='1'):** Input is ignored → Output is the RAW KEY!

**The Exploit:**
When you send the backdoor pattern as input, the system outputs the secret key directly!

---

### **Step 6: Connect to the Challenge Server**

```bash
nc <IP_ADDRESS> <PORT>
```

**Example:**
```bash
nc 83.136.251.67 51692
```

You'll see:
```
The input must be a binary signal of 16 bits.

Input :
```

---

### **Step 7: Trigger the Backdoor**

**Type the backdoor pattern:**
```
1111111111101001
```

**Press Enter**

---

### **Step 8: Get the Flag**

**Expected Output:**
```
Input : 1111111111101001
Output: 0110001111100001

You triggered the backdoor here is the flag: HTB{4_7yp1c41_53cu23_TPM_ch1p}
```

**Flag:** `HTB{4_7yp1c41_53cu23_TPM_ch1p}`

---

## Quick Reference Commands

### Connect to Server
```bash
nc <IP> <PORT>
```

### Backdoor Pattern to Send
```
1111111111101001
```

---

## Understanding the Binary Pattern

| Format | Value |
|--------|-------|
| Binary | 1111111111101001 |
| Hexadecimal | 0xFFE9 |
| Decimal | 65513 |

### Visual Breakdown:
```
Position: 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0
Pattern:   1  1  1  1  1  1 1 1 1 1 1 0 1 0 0 1
```

---

## Key Concepts Explained

### **What is VHDL?**
- Hardware Description Language
- Used to design digital circuits and chips
- Like programming, but for hardware instead of software

### **What is XOR?**
- Exclusive OR operation
- `0 XOR 0 = 0`
- `0 XOR 1 = 1`
- `1 XOR 0 = 1`
- `1 XOR 1 = 0`

### **What is a TPM (Trusted Platform Module)?**
- A hardware chip that stores cryptographic keys
- Used for encryption and secure boot
- Should NEVER leak its keys (but this one has a backdoor!)

### **What is a Hardware Backdoor?**
- A hidden feature in chip design
- Allows bypass of security measures
- Hard to detect and can't be patched easily

---

## Common Mistakes to Avoid

1. **❌ Sending decimal numbers** → Send binary strings only
2. **❌ Wrong bit count** → Must be exactly 16 bits
3. **❌ Spaces in binary** → No spaces: `1111111111101001` ✓
4. **❌ Reading wrong file** → The pattern is in `backdoor.vhdl`

---

## Real-World Context

This challenge simulates real vulnerabilities found in:
- **Intel Management Engine** - Backdoor access to computers
- **NSA's Dual_EC_DRBG** - Backdoored random number generator
- **Huawei Equipment** - Alleged hardware backdoors
- **USB Controllers** - BadUSB vulnerabilities

**Why it matters:**
- Hardware backdoors are permanent (burned into silicon)
- Software patches can't fix them
- Complete system compromise is possible
- Supply chain attacks can inject them

---

## Tools Used

- **netcat (nc)** - Network connection tool
- **Text editor** - To read VHDL files
- **Basic knowledge** - Binary numbers, logic gates

---

## Additional Resources

### Learn More About:
1. **VHDL/Verilog** - Hardware description languages
2. **Digital Logic Design** - Gates, flip-flops, circuits
3. **Cryptographic Hardware** - TPM, HSM, secure elements
4. **Hardware Security** - Side-channel attacks, fault injection

### Practice Similar Challenges:
- PicoCTF Hardware challenges
- CryptoHack (for crypto understanding)
- Embedded Security CTF
- RISCURE Training

---

## Summary Checklist

- [ ] Read all VHDL files
- [ ] Find backdoor pattern in `backdoor.vhdl`
- [ ] Understand the TPM logic in `tpm.vhdl`
- [ ] Connect to challenge server with netcat
- [ ] Send backdoor pattern: `1111111111101001`
- [ ] Receive and submit the flag

---

## Flag Format
```
HTB{4_7yp1c41_53cu23_TPM_ch1p}
```

**Flag Meaning:** "A typical secure TPM chip" (in leetspeak)

---

## Author Notes

This challenge teaches:
- ✅ Hardware reverse engineering basics
- ✅ Reading and understanding VHDL code
- ✅ Identifying security vulnerabilities in hardware designs
- ✅ The importance of hardware security in modern systems

**Difficulty:** Very Easy (once you understand VHDL basics)
**Time Required:** 10-20 minutes
**Skills Learned:** Hardware security, VHDL analysis, backdoor exploitation

---

## Questions & Troubleshooting

**Q: Connection refused/timeout?**
- Check if Docker instance is running
- Verify IP and PORT are correct
- Try reconnecting

**Q: Invalid input error?**
- Ensure exactly 16 bits
- No spaces in the pattern
- Use binary (1s and 0s only)

**Q: No flag appears?**
- Verify you sent the correct pattern
- Check for typos in binary string
- Review backdoor.vhdl again

---

**Last Updated:** November 2025
**Challenge Solved By:** Analysis of VHDL hardware backdoor implementation
