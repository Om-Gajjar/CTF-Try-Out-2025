# HTB Challenge: FlagCasino - Complete Solution Guide

## Challenge Information
- **Name:** FlagCasino
- **Category:** Reversing (Reverse Engineering)
- **Difficulty:** Very Easy
- **Points:** 925

---

## Challenge Description
The team enters a long-abandoned casino where robotic dealers come to life. A dealer promises great wealth if you can win their game. Can you beat the house and gather funds for the mission?

---

## Files Provided

- **casino** - ELF 64-bit executable (17 KB)
  - Linux x86-64 binary
  - Not stripped (has debug symbols)
  - Dynamically linked

---

## Step-by-Step Solution

### **Method 1: Quick String Analysis (Fast)**

#### **Step 1: Run the Program**

```bash
./casino
```

**Output:**
```
[ ** WELCOME TO ROBO CASINO **]
     ,     ,
    (\____/)
     (_oo_)
       (O)
     __||__    \)
  []/______\[] /
  / \______/ \/
 /    /__\
(\   /____\
---------------------
[*** PLEASE PLACE YOUR BETS ***]
>
```

It asks for input, and if you enter anything wrong, it kicks you out:
```
[ * INCORRECT * ]
[ *** ACTIVATING SECURITY SYSTEM - PLEASE VACATE *** ]
```

---

#### **Step 2: Basic Analysis**

```bash
file casino
```

Output:
```
casino: ELF 64-bit LSB pie executable, x86-64, not stripped
```

Check for obvious strings:
```bash
strings casino | grep -E "CORRECT|INCORRECT"
```

Output:
```
[ * CORRECT *]
[ * INCORRECT * ]
```

So there's a correct answer!

---

### **Method 2: Reverse Engineering (Complete)**

#### **Step 1: Disassemble the Main Function**

```bash
objdump -d casino | grep -A 100 "<main>:" | head -120
```

**Key observations from disassembly:**

1. **Input Loop:** Runs 29 times (0x1c + 1)
2. **Per-character processing:**
   - Reads one character
   - Uses it as seed: `srand(character)`
   - Calls `rand()`
   - Compares result to array at offset `0x4080` (check array)
   - Must match for "CORRECT"

3. **Algorithm:**
```c
for (i = 0; i < 29; i++) {
    scanf("%c", &input);
    srand(input);
    if (rand() != check[i]) {
        print("INCORRECT");
        exit();
    }
    print("CORRECT");
}
```

---

#### **Step 2: Extract the Check Array**

```bash
objdump -s -j .data casino
```

Output shows data at `0x4080`:
```
4080 be284b24 0578f70a 17fc0d11 a1c3af07  .(K$.x..........
4090 33c5fe6a a259d64e b0d4c533 b8826528  3..j.Y.N...3..e(
40a0 20373843 fc145a05 9f5f1919 20373843   78C..Z.._.. 78C
40b0 80931463 99b25a61 33c5fe6a b8cf6f6c  ...c..Za3..j..ol
40c0 20373843 37a23d0f 33c5fe6a 99b25a61   78C7.=.3..j..Za
40d0 b8826528 fc145a05 9449e43a e9dfd706  ..e(..Z..I.:....
40e0 a259d64e cd4acd0c 64edd857 99b25a61  .Y.N.J..d..W..Za
40f0 2abce922                             *.."
```

These are 29 uint32_t values (little-endian):
```
0x244b28be, 0x0af77805, 0x110dfc17, 0x07afc3a1,
0x6afec533, 0x4ed659a2, 0x33c5d4b0, 0x286582b8,
0x43383720, 0x055a14fc, 0x19195f9f, 0x43383720,
0x63149380, 0x615ab299, 0x6afec533, 0x6c6fcfb8,
0x43383720, 0x0f3da237, 0x6afec533, 0x615ab299,
0x286582b8, 0x055a14fc, 0x3ae44994, 0x06d7dfe9,
0x4ed659a2, 0x0ccd4acd, 0x57d8ed64, 0x615ab299,
0x22e9bc2a
```

---

#### **Step 3: Brute Force Solution**

Create `solve.c`:

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

uint32_t check[] = {
    0x244b28be, 0x0af77805, 0x110dfc17, 0x07afc3a1,
    0x6afec533, 0x4ed659a2, 0x33c5d4b0, 0x286582b8,
    0x43383720, 0x055a14fc, 0x19195f9f, 0x43383720,
    0x63149380, 0x615ab299, 0x6afec533, 0x6c6fcfb8,
    0x43383720, 0x0f3da237, 0x6afec533, 0x615ab299,
    0x286582b8, 0x055a14fc, 0x3ae44994, 0x06d7dfe9,
    0x4ed659a2, 0x0ccd4acd, 0x57d8ed64, 0x615ab299,
    0x22e9bc2a
};

int main() {
    char flag[30] = {0};
    int num_checks = sizeof(check) / sizeof(check[0]);
    
    for (int i = 0; i < num_checks; i++) {
        for (int c = 32; c <= 126; c++) {  // Printable ASCII
            srand(c);
            if (rand() == check[i]) {
                flag[i] = c;
                printf("[%d] '%c'\n", i, c);
                break;
            }
        }
    }
    
    printf("\nFlag: %s\n", flag);
    return 0;
}
```

Compile and run:
```bash
gcc solve.c -o solve
./solve
```

**Output:**
```
[0] 'H'
[1] 'T'
[2] 'B'
[3] '{'
[4] 'r'
[5] '4'
[6] 'n'
[7] 'd'
[8] '_'
[9] '1'
[10] 's'
[11] '_'
[12] 'v'
[13] '3'
[14] 'r'
[15] 'y'
[16] '_'
[17] 'p'
[18] 'r'
[19] '3'
[20] 'd'
[21] '1'
[22] 'c'
[23] 't'
[24] '4'
[25] 'b'
[26] 'l'
[27] '3'
[28] '}'

Flag: HTB{r4nd_1s_v3ry_pr3d1ct4bl3}
```

---

#### **Step 4: Verify the Flag**

```bash
echo "HTB{r4nd_1s_v3ry_pr3d1ct4bl3}" | ./casino
```

**Output:**
```
[*** PLEASE PLACE YOUR BETS ***]
> [ * CORRECT *]
> [ * CORRECT *]
> [ * CORRECT *]
... (29 times)
[ ** HOUSE BALANCE $0 - PLEASE COME BACK LATER ** ]
```

Success! 🎰

---

### **Method 3: Using Ghidra/IDA (GUI)**

#### **Step 1: Load in Ghidra**

1. Open Ghidra
2. Create new project
3. Import `casino` binary
4. Analyze with default settings

#### **Step 2: Navigate to Main**

In the Symbol Tree, double-click `main` function.

**Decompiled pseudo-code:**
```c
void main(void) {
  int iVar1;
  uint local_14;
  char local_d;
  
  puts("[ ** WELCOME TO ROBO CASINO **]");
  puts(banner);
  puts("---------------------");
  puts("[*** PLEASE PLACE YOUR BETS ***]");
  
  local_14 = 0;
  while (local_14 < 0x1d) {  // Loop 29 times
    printf("> ");
    iVar1 = __isoc99_scanf("%c", &local_d);
    
    if (iVar1 != 1) {
      exit(-1);
    }
    
    srand((int)local_d);
    iVar1 = rand();
    
    if (iVar1 != check[local_14]) {
      puts("[ * INCORRECT * ]");
      puts("[ *** ACTIVATING SECURITY SYSTEM - PLEASE VACATE *** ]");
      exit(-2);
    }
    
    puts("[ * CORRECT *]");
    local_14 = local_14 + 1;
  }
  
  puts("[ ** HOUSE BALANCE $0 - PLEASE COME BACK LATER ** ]");
  return;
}
```

#### **Step 3: View Check Array**

Click on `check` symbol → shows array of 29 uint32_t values.

Use the same brute force approach to find matching characters.

---

## Understanding the Vulnerability

### **Why is rand() Predictable?**

1. **Deterministic Algorithm**
   - `rand()` is a Pseudo-Random Number Generator (PRNG)
   - Same seed → same sequence
   - Formula: `state = (state * 1103515245 + 12345) % 2^31`

2. **Single-Byte Seed**
   - Using ASCII characters (32-126) as seeds
   - Only ~95 possible seeds
   - Easy to brute force

3. **No Cryptographic Security**
   - `rand()` is NOT cryptographically secure
   - Should never be used for security-critical applications
   - Use `/dev/urandom`, `getrandom()`, or `arc4random()` instead

### **Attack Approach**

```
For each position in flag:
  For each possible ASCII character:
    srand(character)
    if rand() == expected_value:
      Found the character!
```

**Complexity:** O(n * m) where n=29, m=95 → ~2,755 operations (trivial)

---

## Flag Breakdown

```
HTB{r4nd_1s_v3ry_pr3d1ct4bl3}
```

**Decoded (leetspeak):**
- `r4nd` = "rand" (the C function)
- `1s` = "is"
- `v3ry` = "very"
- `pr3d1ct4bl3` = "predictable"

**Message:** "rand is very predictable"

**Security Lesson:**
Never use `rand()` for security! It's meant for simulations and games, not cryptography.

---

## Key Concepts

### **PRNG (Pseudo-Random Number Generator)**

**How rand() works:**
```c
static unsigned long state = 1;

int rand(void) {
    state = state * 1103515245 + 12345;
    return (state / 65536) % 32768;
}

void srand(unsigned int seed) {
    state = seed;
}
```

**Properties:**
- ✅ Fast
- ✅ Good statistical distribution
- ❌ Completely predictable if seed is known
- ❌ NOT cryptographically secure

### **Secure Alternatives**

```c
// Linux - use getrandom()
#include <sys/random.h>
getrandom(buffer, size, 0);

// Or read from /dev/urandom
FILE *f = fopen("/dev/urandom", "rb");
fread(buffer, 1, size, f);
fclose(f);

// OpenBSD - use arc4random()
uint32_t random_value = arc4random();
```

---

## Real-World Examples

### **1. Netscape SSL (1994)**
- Used predictable PRNG for SSL keys
- Seed based on time + process ID
- Easily guessable → broken security

### **2. Debian OpenSSL Bug (2008)**
- Limited entropy in key generation
- Only 32,768 possible SSH keys
- Millions of servers vulnerable

### **3. Android Bitcoin Wallets (2013)**
- Bad RNG in SecureRandom
- Private keys could be predicted
- Bitcoin theft from wallets

### **4. Slot Machines Hacks**
- Real slot machines use PRNGs
- Some used predictable seeds (time-based)
- Hackers could predict winning spins

---

## Tools for Reverse Engineering

### **Static Analysis:**
- **Ghidra** - Free, powerful decompiler
- **IDA Pro** - Industry standard (commercial)
- **radare2/Cutter** - Open-source, advanced
- **Binary Ninja** - Modern GUI, good for learning
- **objdump** - Command-line disassembler

### **Dynamic Analysis:**
- **gdb** - GNU debugger
- **ltrace** - Library call tracer
- **strace** - System call tracer
- **Valgrind** - Memory debugger

### **Quick Commands:**

```bash
# Check file type
file casino

# List strings
strings casino

# Disassemble
objdump -d casino

# View sections
readelf -S casino

# Extract data section
objdump -s -j .data casino

# Debug
gdb casino
```

---

## Challenge Walkthrough

### **What We Did:**

1. **Reconnaissance**
   - Identified binary type (ELF 64-bit)
   - Ran program to understand behavior
   - Found "CORRECT"/"INCORRECT" messages

2. **Static Analysis**
   - Disassembled main function
   - Found input loop (29 iterations)
   - Discovered srand/rand pattern
   - Located check array

3. **Solution Development**
   - Extracted expected rand() values
   - Wrote brute force solver
   - Found each character matches specific rand() output

4. **Verification**
   - Tested flag with original program
   - All 29 checks passed
   - Got success message

---

## Quick Reference

### **One-Line Solutions:**

**Extract and brute force:**
```bash
# Create solver
cat > solve.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>
uint32_t c[]={0x244b28be,0x0af77805,0x110dfc17,0x07afc3a1,0x6afec533,0x4ed659a2,0x33c5d4b0,0x286582b8,0x43383720,0x055a14fc,0x19195f9f,0x43383720,0x63149380,0x615ab299,0x6afec533,0x6c6fcfb8,0x43383720,0x0f3da237,0x6afec533,0x615ab299,0x286582b8,0x055a14fc,0x3ae44994,0x06d7dfe9,0x4ed659a2,0x0ccd4acd,0x57d8ed64,0x615ab299,0x22e9bc2a};
int main(){char f[30]={0};for(int i=0;i<29;i++)for(int x=32;x<=126;x++){srand(x);if(rand()==c[i]){f[i]=x;break;}}printf("%s\n",f);}
EOF

gcc solve.c -o solve && ./solve
```

**Test flag:**
```bash
echo "HTB{r4nd_1s_v3ry_pr3d1ct4bl3}" | ./casino
```

### **Flag:**
```
HTB{r4nd_1s_v3ry_pr3d1ct4bl3}
```

**Translation:**
```
"rand is very predictable"
```

---

## Common Mistakes

1. **❌ Trying to input the flag all at once**
   - The program reads character-by-character
   - Each character is processed individually

2. **❌ Not understanding little-endian**
   - Hex bytes `be 28 4b 24` = `0x244b28be` (not `0xbe284b24`)
   - x86 is little-endian

3. **❌ Wrong check array extraction**
   - Must use correct memory offset
   - Verify with multiple tools (objdump, xxd, Ghidra)

4. **❌ Assuming rand() is truly random**
   - It's deterministic!
   - Same seed always gives same output

---

## Learning Objectives

This challenge teaches:
- ✅ **Basic reverse engineering** with objdump/Ghidra
- ✅ **PRNG vulnerabilities** and predictability
- ✅ **Brute force attacks** on weak algorithms
- ✅ **Character-by-character validation** weaknesses
- ✅ **Static binary analysis** techniques
- ✅ **Little-endian byte order** understanding

---

## Practice Exercises

### **Try These Variations:**

1. **Modify the check array**
   - Change expected values
   - Recompile and solve

2. **Add more rounds**
   - Extend to 50+ characters
   - See how brute force scales

3. **Use different seeds**
   - What if seed was 2 bytes?
   - What if it used time() as seed?

4. **Implement secure version**
   - Replace rand() with /dev/urandom
   - Add proper crypto

---

## Additional Resources

### **Learn More:**

1. **Reverse Engineering:**
   - "Practical Reverse Engineering" by Bruce Dang
   - "The IDA Pro Book" by Chris Eagle
   - Ghidra tutorials on YouTube

2. **Cryptography:**
   - "Cryptography Engineering" by Ferguson & Schneier
   - OWASP Cryptographic Storage Cheat Sheet
   - Random.org - Understanding Randomness

3. **CTF Platforms:**
   - crackmes.one - Reversing challenges
   - reversing.kr - Korean reversing site
   - pwnable.kr - Exploitation challenges

### **Tools to Learn:**
- Ghidra - Free reverse engineering
- gdb + pwndbg - Debugging with superpowers
- radare2 - Command-line RE framework
- angr - Symbolic execution framework

---

## Summary Checklist

- [ ] Extract casino binary
- [ ] Run and observe behavior
- [ ] Disassemble with objdump or Ghidra
- [ ] Identify srand/rand pattern
- [ ] Extract check array from .data section
- [ ] Write brute force solver in C
- [ ] Compile and run solver
- [ ] Get flag: HTB{r4nd_1s_v3ry_pr3d1ct4bl3}
- [ ] Verify with original program
- [ ] Submit flag

---

## Security Takeaways

### **For Developers:**

1. **Never use rand() for security**
   - Predictable by design
   - Use cryptographically secure alternatives

2. **Input validation per-character is weak**
   - Allows targeted brute forcing
   - Use HMAC or full-input hashing

3. **Secrets in binaries are extractable**
   - Don't hardcode keys
   - Use secure key storage

### **For Attackers (Ethical):**

1. **Check for weak PRNGs**
   - rand(), mt_rand(), LCG patterns
   - Time-based seeds

2. **Character-by-character validation**
   - Allows position-specific attacks
   - Test each byte independently

3. **Static analysis first**
   - Often faster than dynamic
   - Strings and disassembly reveal much

---

## Real Casino Slot Machine Security

**Interesting fact:** Real slot machines also use PRNGs!

**How they protect against this attack:**
1. **Hardware RNG** - Uses physical entropy source
2. **Cryptographic PRNG** - With 128+ bit internal state
3. **Frequent reseeding** - From hardware entropy
4. **Timing-independent** - Can't predict based on button press time
5. **Audited algorithms** - Certified by gaming commissions
6. **Tamper-evident hardware** - Physical security

**But exploits still happen:**
- 2009: "Slot machine hacker" exploited timing patterns
- Predictable PRNGs in older machines
- Modern machines are much more secure

---

## Flag Format

```
HTB{r4nd_1s_v3ry_pr3d1ct4bl3}
```

**Leetspeak Translation:**
```
rand is very predictable
```

**Security Lesson:**
The C `rand()` function is a **weak PRNG** suitable only for simulations, not security. Always use cryptographically secure random number generators for any security-sensitive application!

---

**Last Updated:** November 2025  
**Challenge Solved By:** Reverse engineering and brute force attack on weak PRNG  
**Difficulty Rating:** Very Easy (with basic RE skills)  
**Time Required:** 15-25 minutes  
**Skills Learned:** Binary analysis, PRNG weaknesses, brute force attacks, reverse engineering basics
