# HTB Challenge: LootStash - Complete Solution Guide

## Challenge Information
- **Name:** LootStash
- **Category:** Reversing (Reverse Engineering)
- **Difficulty:** Very Easy
- **Points:** 950

---

## Challenge Description
A giant stash of powerful weapons and gear have been dropped into the arena - but there's one item you have in mind. Can you filter through the stack to get to the one thing you really need?

---

## Files Provided

- **stash** - ELF 64-bit executable (30 KB)
  - Linux x86-64 binary
  - Not stripped (has debug symbols)
  - Dynamically linked

---

## Quick Solution

### **Method 1: Strings (Fastest - 10 seconds)**

The simplest approach is to search for the flag in the binary's strings:

```bash
strings stash | grep HTB
```

**Output:**
```
HTB{n33dl3_1n_a_l00t_stack}
```

**That's it!** Flag found in literally 10 seconds. 🎯

---

## Detailed Solutions

### **Method 2: Running the Program**

#### **Step 1: Execute the Binary**

```bash
./stash
```

**Output:**
```
Diving into the stash - let's see what we can find.
.....
You got: 'Phantomdream, Trinket of the Corrupted'. Now run, before anyone tries to steal it!
```

The program:
1. Displays a loading animation (dots with sleep)
2. Randomly selects an item from the loot stash
3. Displays the selected item name

#### **Step 2: Run Multiple Times**

Each time you run it, you get a different random item:

```bash
./stash
# Output: Ebony, Core of Perdition

./stash
# Output: Moonlight, Glory of the Lasting Night

./stash
# Output: HTB{n33dl3_1n_a_l00t_stack}  # Eventually!
```

**Problem:** There are **100+ items** in the stash. You'd need to run it many times to get the flag by chance!

---

### **Method 3: Full String Analysis**

#### **View All Items in the Stash**

```bash
strings stash | more
```

You'll see a huge list of fantasy item names:
```
Ebony, Core of Perdition
Phantomdream, Trinket of the Corrupted
Earthsong, Dawn of Visions
Torment, Beacon of Twilight's End
Moonshard, Baton of the Wind
Mirage, Bead of Secrets
...
HTB{n33dl3_1n_a_l00t_stack}  ← THE FLAG!
...
Draughtbane, Fan of Perdition
```

The flag is disguised among ~100 fantasy item names!

---

### **Method 4: Grep for Flag Pattern**

```bash
strings stash | grep -E "HTB\{.*\}"
```

**Output:**
```
HTB{n33dl3_1n_a_l00t_stack}
```

This filters for the HTB flag format specifically.

---

### **Method 5: Reverse Engineering (Overkill)**

For learning purposes, let's see what the program actually does:

#### **Disassemble Main Function**

```bash
objdump -d stash | grep -A 50 "<main>:"
```

**Algorithm discovered:**
1. Seeds random number generator with `time(NULL)`
2. Prints loading message
3. Prints 5 dots with 1-second delays
4. Calls `rand()` to pick random index
5. Uses modulo to select from item array
6. Prints selected item name

**Item Array Location:**
- Stored in `.rodata` section
- Array of string pointers
- Flag is one of the items in the array

#### **Using Ghidra/IDA**

Load in Ghidra and navigate to main:

**Decompiled code (pseudo):**
```c
void main(void) {
    char *item;
    int i, random_index;
    
    setvbuf(stdout, NULL, 2, 0);
    srand(time(NULL));
    
    puts("Diving into the stash - let's see what we can find.");
    
    for (i = 0; i <= 4; i++) {
        putchar('.');
        sleep(1);
    }
    
    random_index = rand() % NUM_ITEMS;
    item = item_array[random_index];
    
    printf("\nYou got: '%s'. Now run, before anyone tries to steal it!\n", item);
}
```

The `item_array` contains all the loot names, including the flag!

---

## Understanding the Challenge

### **The Concept**

This challenge is a play on the phrase **"needle in a haystack"**.

- **Haystack** = Stack of loot items (100+ fantasy weapon/trinket names)
- **Needle** = The flag `HTB{n33dl3_1n_a_l00t_stack}`

The flag is literally hidden in a "loot stack" and you need to filter through to find it.

### **Flag Breakdown**

```
HTB{n33dl3_1n_a_l00t_stack}
```

**Decoded (leetspeak):**
- `n33dl3` = "needle"
- `1n` = "in"
- `a` = "a"
- `l00t` = "loot"
- `stack` = "stack"

**Message:** "needle in a loot stack"

A clever reference to finding specific items in loot drops in video games!

---

## Why This is Easy

### **No Actual Reversing Required**

1. **Flag is in plaintext** - Not encrypted or obfuscated
2. **Standard strings command works** - No packing or protection
3. **No anti-debugging** - Not stripped, no obfuscation
4. **Simple grep finds it** - Standard CTF flag format

### **Intended Learning Outcome**

This challenge teaches:
- ✅ Basic use of `strings` command
- ✅ Searching binary files for text
- ✅ Recognizing flag formats
- ✅ Simple static analysis

**Reality:** In real malware/protected software, strings are often:
- Encrypted or encoded
- Obfuscated or split up
- Stripped from the binary
- Generated dynamically at runtime

---

## Tools Used

### **Essential Tools:**

```bash
# View file type
file stash

# List all printable strings
strings stash

# Search for pattern
strings stash | grep HTB

# Or use ripgrep (faster)
rg "HTB\{" stash

# Hex dump to see raw data
xxd stash | less

# Disassemble
objdump -d stash

# Full reverse engineering
ghidra
```

---

## Real-World Applications

### **String Analysis in Security**

**Uses:**
1. **Malware Analysis**
   - Find C2 server addresses
   - Discover hardcoded credentials
   - Identify ransomware notes
   - Detect embedded scripts

2. **Incident Response**
   - Extract IOCs (Indicators of Compromise)
   - Find embedded URLs
   - Discover attacker tools

3. **Vulnerability Research**
   - Find debug messages
   - Locate version strings
   - Discover error messages with sensitive info

**Example - Real Malware:**
```bash
strings suspicious.exe | grep -E "http|ftp|\.exe|\.dll"
```

Might reveal:
```
http://evil-c2-server.com/beacon
C:\Windows\System32\payload.exe
admin:password123
```

---

## CTF Tips

### **String Searching Best Practices**

1. **Always try strings first**
   ```bash
   strings binary | grep -i flag
   strings binary | grep HTB
   strings binary | grep -E "[A-Za-z0-9+/]{20,}==" # Base64
   ```

2. **Search for common patterns**
   ```bash
   strings binary | grep -E "http|ftp|ssh"  # URLs
   strings binary | grep -E "key|pass|token"  # Credentials
   strings binary | grep -E "[0-9]{1,3}\.[0-9]{1,3}\." # IPs
   ```

3. **Use different encodings**
   ```bash
   strings -e l binary  # 16-bit little-endian
   strings -e b binary  # 16-bit big-endian
   strings -e L binary  # 32-bit little-endian
   ```

4. **Combine with other tools**
   ```bash
   strings binary | sort -u  # Unique strings only
   strings binary | tr -d '\n' | grep pattern  # Remove newlines
   ```

---

## Challenge Walkthrough

### **What We Did:**

1. **Reconnaissance**
   - Identified file type (ELF 64-bit)
   - Ran program to understand behavior
   - Saw it outputs random items

2. **Static Analysis**
   - Ran `strings` command
   - Found 100+ fantasy item names
   - Located flag among the items

3. **Solution**
   - Used `grep` to filter for HTB format
   - Found flag immediately
   - No reversing actually needed!

4. **Understanding**
   - Examined disassembly to understand logic
   - Program uses `rand()` to select items
   - Flag is just another item in the array

---

## Quick Reference

### **One-Line Solution:**

```bash
strings stash | grep HTB
```

**Output:**
```
HTB{n33dl3_1n_a_l00t_stack}
```

### **Alternative One-Liners:**

```bash
# Using ripgrep (faster)
rg "HTB" stash

# Using grep directly on binary
grep -a "HTB{" stash

# Find all items and grep
strings stash | grep -i trinket | head -20

# Count total items
strings stash | grep -E "^[A-Z]" | wc -l
```

---

## Flag Format

```
HTB{n33dl3_1n_a_l00t_stack}
```

**Translation:**
```
"needle in a loot stack"
```

**Context:**
- Gaming reference (loot drops in RPGs)
- Common phrase "needle in a haystack"
- One specific item among many random drops

---

## Common Mistakes

1. **❌ Running the program 100+ times hoping to get flag**
   - Inefficient, could take hours
   - Use static analysis instead

2. **❌ Trying to reverse engineer the rand() logic**
   - Unnecessary complexity
   - Flag is in plaintext, just extract it

3. **❌ Not using strings command**
   - First tool to try for any CTF binary
   - Fast and effective

4. **❌ Missing flag because of too many results**
   - Use grep with pattern matching
   - Filter for HTB{ format

---

## Learning Objectives

This challenge teaches:
- ✅ **Static analysis basics** - strings command
- ✅ **Pattern matching** - grep for flags
- ✅ **CTF flag formats** - HTB{...} structure
- ✅ **Data hiding** - concealing info in noise
- ✅ **Basic binary analysis** - finding embedded data

---

## Practice Exercises

### **Try These:**

1. **Find all items containing "Shadow"**
   ```bash
   strings stash | grep -i shadow
   ```

2. **Count total unique items**
   ```bash
   strings stash | grep -E "^[A-Z][a-z]+," | wc -l
   ```

3. **Extract items to file**
   ```bash
   strings stash | grep "," > loot_items.txt
   ```

4. **Find pattern in item names**
   ```bash
   strings stash | grep -E "Trinket|Bead|Globe"
   ```

---

## Additional Resources

### **Learn More:**

1. **Binary Analysis:**
   - "Practical Binary Analysis" by Dennis Andriesse
   - "The Art of Exploitation" by Jon Erickson
   - Binary exploitation tutorials

2. **Tools to Master:**
   - **strings** - Extract printable strings
   - **grep** - Pattern matching
   - **ripgrep** - Fast searching
   - **xxd/hexdump** - Hex viewers
   - **objdump** - Disassembler
   - **Ghidra** - Full RE suite

3. **CTF Resources:**
   - picoCTF - Beginner challenges
   - OverTheWire - Progressive difficulty
   - crackmes.one - Practice reversing

---

## Summary Checklist

- [ ] Extract stash binary
- [ ] Run `file stash` to identify type
- [ ] Execute `./stash` to see behavior
- [ ] Run `strings stash | grep HTB`
- [ ] Get flag: HTB{n33dl3_1n_a_l00t_stack}
- [ ] Submit flag
- [ ] (Optional) Disassemble to understand logic

---

## Gaming Reference

### **Loot Systems in Games**

This challenge references loot drop mechanics from games like:

**Diablo Series:**
- Random item drops from monsters
- Rare items hidden among common loot
- "Grinding" for specific legendary items

**World of Warcraft:**
- Boss loot tables
- Random stat rolls
- Searching for "Best in Slot" items

**Borderlands:**
- Billions of procedurally generated weapons
- Finding that one perfect legendary
- "One more run" for better loot

**The Challenge Metaphor:**
You're "looting" the binary to find that one special item (the flag) among dozens of common drops!

---

## Security Implications

### **Why Strings Matter:**

**In Malware Analysis:**
1. **Hardcoded credentials** often visible
2. **C2 server domains** in plaintext
3. **Ransom notes** embedded as strings
4. **Debug messages** reveal functionality

**In Software Auditing:**
1. **API keys** accidentally committed
2. **Database credentials** in binaries
3. **Internal URLs** exposed
4. **Version info** for vulnerability matching

**Protection Methods:**
1. **String encryption** - Decrypt at runtime
2. **Obfuscation** - XOR, base64, custom encoding
3. **String splitting** - Reconstruct dynamically
4. **Binary packing** - Compress/encrypt entire binary

---

## Real Example - AWS Key Leak

**Common mistake:**
```c
// Hardcoded in source
const char* AWS_KEY = "AKIAIOSFODNN7EXAMPLE";
```

**Result:**
```bash
$ strings myapp | grep AKIA
AKIAIOSFODNN7EXAMPLE
```

**Impact:**
- Full AWS account access
- Potential data breach
- Financial losses

**Proper approach:**
- Use environment variables
- Secrets management (Vault, AWS Secrets Manager)
- Never hardcode credentials

---

## Conclusion

**LootStash** is a beginner-friendly introduction to binary analysis that teaches the importance of:
1. Static analysis before dynamic
2. Using the right tools (strings, grep)
3. Pattern recognition (flag formats)
4. Understanding data in binaries

The flag literally tells you what you did: found a "needle in a loot stack" by filtering through the noise!

---

**Last Updated:** November 2025  
**Challenge Solved By:** String analysis and pattern matching  
**Difficulty Rating:** Very Easy (5-10 seconds with right command)  
**Time Required:** 10 seconds - 5 minutes  
**Skills Learned:** strings command, grep, static analysis, CTF basics
