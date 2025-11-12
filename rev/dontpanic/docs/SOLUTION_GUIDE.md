# HTB Challenge: Don't Panic! - Complete Solution Guide

## Challenge Information
- **Name:** Don't Panic!
- **Category:** Reversing (Reverse Engineering)
- **Difficulty:** Easy
- **Points:** 975

---

## Challenge Description
You've made a deal with the Brotherhood to retrieve their stolen weapons cache. Using stealth technology, you've bypassed guards and reached the inner sanctum. Now you must disable a highly sensitive heat-signature detection robot without setting off the alarm. Can you find the correct input to bypass the security system?

---

## Files Provided

- **dontpanic** - ELF 64-bit executable (3.7 MB)
  - Linux x86-64 binary
  - Rust language binary  
  - With debug info, not stripped
  - Dynamically linked

---

## Quick Solution

### **TL;DR - The Flag:**

```
HTB{d0nt_p4n1c_c4tch_the_3rror}
```

**Translation:** "don't panic catch the error"

---

## Step-by-Step Solution

### **Method 1: Reverse Engineering with objdump**

#### **Step 1: Identify the Binary**

```bash
file dontpanic
```

Output:
```
dontpanic: ELF 64-bit LSB pie executable, x86-64, with debug_info, not stripped
```

#### **Step 2: Check for Rust**

```bash
strings dontpanic | grep -i rust | head -5
```

Output shows Rust runtime strings - this is a **Rust binary**!

---

#### **Step 3: Find Key Functions**

```bash
nm dontpanic | grep -i "flag\|check\|main"
```

Output shows:
```
0000000000009060 t _ZN3src10check_flag17h397d174e03dc8c74E
0000000000009230 t _ZN3src4main17hf9bc229851763ab9E
```

The `check_flag` function at `0x9060` is our target!

---

#### **Step 4: Analyze check_flag Function**

```bash
objdump -d dontpanic | grep -A 200 "9060 <_ZN3src10check_flag"
```

**Key findings:**
1. Compares input length to `0x1f` (31 bytes)
2. Creates array of function pointers on stack
3. Loops through each character and calls corresponding check function
4. Each check function validates one character

**Algorithm:**
```rust
fn check_flag(input: &str) {
    assert!(input.len() == 31);
    
    let checkers = [func0, func1, func2, ...];  // 31 functions
    
    for (i, ch) in input.chars().enumerate() {
        checkers[i](ch);  // Each function checks one char
    }
}
```

---

#### **Step 5: Extract Check Functions**

The check functions are stored starting at `%rsp+0x10`:
```
mov %rax, 0x10(%rsp)   # Function 0 for char 0
mov %rax, 0x18(%rsp)   # Function 1 for char 1
mov %rax, 0x20(%rsp)   # Function 2 for char 2
...
```

**Function addresses in order:**
```
0x8b80 -> 'H'
0x8d80 -> 'T'
0x8d40 -> 'B'
0x8e00 -> '{'
0x8e40 -> 'd'
0x8c00 -> '0'
0x8c80 -> 'n'
0x8ac0 -> 't'
0x8b00 -> '_'
0x8a80 -> 'p'
0x8d00 -> '4'
0x8c80 -> 'n'  (reused)
0x8cc0 -> '1'
0x8b40 -> 'c'
0x8b00 -> '_'  (reused)
0x8b40 -> 'c'  (reused)
0x8d00 -> '4'  (reused)
0x8ac0 -> 't'  (reused)
0x8b40 -> 'c'  (reused)
0x8a40 -> 'h'
0x8b00 -> '_'  (reused)
0x8ac0 -> 't'  (reused)
0x8a40 -> 'h'  (reused)
0x8dc0 -> 'e'
0x8b00 -> '_'  (reused)
0x8e80 -> '3'
0x8c40 -> 'r'
0x8c40 -> 'r'  (reused)
0x8bc0 -> 'o'
0x8c40 -> 'r'  (reused)
0x8ec0 -> '}'
```

---

#### **Step 6: Examine a Check Function**

```bash
objdump -d dontpanic | grep -A 10 "8b80 <"
```

Output:
```
8b80 <...>:
    8b80:   push   %rax
    8b81:   cmp    $0x48,%dil      # Compare with 'H' (0x48)
    8b85:   jb     8b8b            # If below, panic
    8b87:   jne    8ba4            # If not equal, panic
    8b89:   pop    %rax
    8b8a:   ret                     # Success!
    8b8b:   ...panic code...
```

Each function:
1. Compares input character with expected value
2. Panics if wrong (calls panic!)
3. Returns if correct

---

#### **Step 7: Extract All Characters**

Using Python script:

```python
# Map function addresses to characters
func_to_char = {
    0x8a40: 'h', 0x8a80: 'p', 0x8ac0: 't',
    0x8b00: '_', 0x8b40: 'c', 0x8b80: 'H',
    0x8bc0: 'o', 0x8c00: '0', 0x8c40: 'r',
    0x8c80: 'n', 0x8cc0: '1', 0x8d00: '4',
    0x8d40: 'B', 0x8d80: 'T', 0x8dc0: 'e',
    0x8e00: '{', 0x8e40: 'd', 0x8e80: '3',
    0x8ec0: '}',
}

# Stack layout (rsp+offset -> function address)
stack = {
    0x10: 0x8b80,  # H
    0x18: 0x8d80,  # T
    0x20: 0x8d40,  # B
    # ... etc for all 31 positions
}

flag = ''.join([func_to_char[stack[off]] for off in sorted(stack.keys())])
print(flag)  # HTB{d0nt_p4n1c_c4tch_the_3rror}
```

---

### **Method 2: Dynamic Analysis with GDB**

#### **Step 1: Run with Debugger**

```bash
gdb ./dontpanic
```

#### **Step 2: Set Breakpoint**

```gdb
break check_flag
run
```

Program asks for input. You could provide test input and see where it fails.

#### **Step 3: Examine Check Functions**

```gdb
x/31gx $rsp+0x10
```

This shows all 31 function pointers in the array.

#### **Step 4: Disassemble Each Function**

```gdb
disas 0x8b80
```

Look for the `cmp $0xNN,%dil` instruction to find expected character.

---

### **Method 3: Using Ghidra**

#### **Step 1: Load Binary**

1. Open Ghidra
2. Create project
3. Import `dontpanic`
4. Analyze (this takes a while - 3.7 MB binary)

#### **Step 2: Find check_flag**

Search for functions:
- Use **Symbol Tree**
- Look for `check_flag` or search decompilation

#### **Step 3: Decompiled Code**

Ghidra shows pseudo-Rust code:
```c
void check_flag(char *input, ulong len) {
    if (len != 0x1f) {
        panic("assertion failed");
    }
    
    // Array of function pointers
    func_ptr checkers[31] = {...};
    
    for (int i = 0; i < 31; i++) {
        checkers[i](input[i]);
    }
}
```

#### **Step 4: View Check Functions**

Click on each function pointer to see what character it checks.

---

## Understanding the Challenge

### **Rust's Panic System**

This challenge is all about **Rust's error handling**:

1. **Don't Panic!**
   - Famous phrase from "The Hitchhiker's Guide to the Galaxy"
   - Also Rust's motto for error handling
   - `panic!()` macro terminates program

2. **Catch the Error**
   - Rust has `catch_unwind()` to catch panics
   - Proper error handling uses `Result<T, E>`
   - The flag tells you: "don't panic, catch the error"

### **Why This Works**

```rust
fn check_char_H(c: char) {
    if c != 'H' {
        panic!("Wrong character!");
    }
}

fn check_flag(input: &str) {
    let checkers = [
        check_char_H,
        check_char_T,
        check_char_B,
        // ... 31 total
    ];
    
    for (i, ch) in input.chars().enumerate() {
        checkers[i](ch);  // Panics if wrong!
    }
    
    println!("All is well");  // Only if no panics
}
```

---

## Flag Breakdown

```
HTB{d0nt_p4n1c_c4tch_the_3rror}
```

**Decoded (leetspeak):**
- `d0nt` = "don't"
- `p4n1c` = "panic"
- `c4tch` = "catch"
- `the` = "the"  
- `3rror` = "error"

**Message:** "don't panic catch the error"

**Context:**
- Rust programming language motto
- Reference to error handling best practices
- Play on "Don't Panic!" from Hitchhiker's Guide

---

## Rust Reverse Engineering

### **Why Rust Binaries are Different**

1. **Larger Size**
   - 3.7 MB for simple program!
   - Includes entire standard library
   - Monomorphization creates many specialized functions

2. **Name Mangling**
   - `_ZN3src10check_flag17h397d174e03dc8c74E`
   - Format: `_ZN{module}{len}{name}{hash}E`
   - Use `rustfilt` to demangle

3. **Panic Infrastructure**
   - Lots of panic-related code
   - Stack unwinding support
   - Error formatting

4. **Optimization**
   - Aggressive inlining
   - Loop unrolling
   - Function specialization

### **Common Rust Patterns**

**Pattern 1: Match/Enum**
```rust
match value {
    Some(x) => process(x),
    None => panic!("unwrap failed"),
}
```

**Pattern 2: Array Iteration**
```rust
for (i, item) in array.iter().enumerate() {
    process(i, item);
}
```

**Pattern 3: Closures**
```rust
let checkers: Vec<Box<dyn Fn(char)>> = vec![
    Box::new(|c| assert_eq!(c, 'H')),
    Box::new(|c| assert_eq!(c, 'T')),
];
```

---

## Tools for Rust RE

### **Demangling**

```bash
# Install rustfilt
cargo install rustfilt

# Use it
nm dontpanic | rustfilt
```

Output:
```
src::check_flag
src::main
```

### **Cargo Inspection**

If you have source:
```bash
cargo build --release
objdump -d target/release/program
```

### **Debug vs Release**

- **Debug:** Easier to RE (less optimization)
- **Release:** Heavily optimized, harder to follow

---

## Security Implications

### **Anti-RE Techniques**

This challenge demonstrates that Rust makes RE harder:
1. **Size:** 3.7 MB discourages analysis
2. **Complexity:** Lots of generated code
3. **Mangling:** Hard to identify functions
4. **Optimization:** Logic is transformed

### **But Still Reversible!**

- **Symbols present:** Not stripped
- **Debug info:** Makes it easier
- **Logic is there:** Just need patience
- **Patterns emerge:** Recognize Rust idioms

---

## Challenge Walkthrough

### **What We Did:**

1. **Identification**
   - Recognized Rust binary
   - Found `check_flag` function
   - Saw panic-related strings

2. **Static Analysis**
   - Disassembled check_flag
   - Found array of function pointers
   - Extracted 31 check functions

3. **Pattern Recognition**
   - Each function checks one character
   - Simple comparison: `cmp $0xNN,%dil`
   - Functions are reused (optimization)

4. **Extraction**
   - Mapped stack offsets to functions
   - Mapped functions to characters
   - Built flag character by character

---

## Quick Reference

### **Automated Solution Script**

```python
#!/usr/bin/env python3
import subprocess, re

# Get disassembly
dis = subprocess.run(['objdump', '-d', 'dontpanic'], 
                     capture_output=True, text=True).stdout

# Find check_flag and extract function addresses
# ... (see solution script above) ...

# Output: HTB{d0nt_p4n1c_c4tch_the_3rror}
```

### **Manual Commands**

```bash
# Find check function
nm dontpanic | grep check

# Disassemble it
objdump -d dontpanic | less
# Search for: /9060

# Extract each check function
objdump -d dontpanic | grep -A 10 "8b80 <"
# Look for: cmp $0x...
```

---

## Common Mistakes

1. **❌ Not recognizing it's Rust**
   - Rust binaries have unique characteristics
   - Look for panic strings, Result types

2. **❌ Trying to run it for flag**
   - Program expects correct input
   - Wrong input causes panic (crash)

3. **❌ Not finding check_flag**
   - Use `nm` to list symbols
   - Search for "check" or "flag"

4. **❌ Misreading function order**
   - Stack layout matters!
   - Functions stored at rsp+0x10, rsp+0x18, etc.
   - Array indexed by character position

5. **❌ Missing reused functions**
   - Some functions check multiple characters
   - Same function pointer appears multiple times
   - Example: 0x8b40 checks 'c' three times

---

## Learning Objectives

This challenge teaches:
- ✅ **Rust binary analysis** - unique patterns
- ✅ **Function pointer arrays** - indirect calls
- ✅ **Character-by-character validation** - common CTF pattern
- ✅ **Static analysis** - no dynamic execution needed
- ✅ **Pattern recognition** - identifying check functions

---

## Additional Resources

### **Learn Rust RE:**

1. **Books:**
   - "The Rust Programming Language" - understand the source
   - "Practical Reverse Engineering" - general RE skills

2. **Tools:**
   - **rustfilt** - Demangle Rust symbols
   - **cargo-binutils** - Rust-aware binary tools
   - **Ghidra** - Supports Rust (with plugins)

3. **Practice:**
   - Reverse your own Rust programs
   - CrackMes in Rust
   - CTF Rust challenges

### **Rust Security:**

- **Memory Safety:** No buffer overflows (in safe code)
- **Type Safety:** Strong type system
- **But:** Still vulnerable to logic bugs
- **RE Difficulty:** Medium (better than C++, worse than C)

---

## Summary Checklist

- [ ] Extract dontpanic binary
- [ ] Identify as Rust binary (strings)
- [ ] Find check_flag function (nm or objdump)
- [ ] Disassemble check_flag
- [ ] Extract 31 function pointers from stack
- [ ] Disassemble each check function
- [ ] Extract comparison value (cmp instruction)
- [ ] Build flag: HTB{d0nt_p4n1c_c4tch_the_3rror}
- [ ] Submit flag

---

## Flag Format

```
HTB{d0nt_p4n1c_c4tch_the_3rror}
```

**Translation:**
```
"don't panic catch the error"
```

**Context:**
- Rust error handling philosophy
- Reference to The Hitchhiker's Guide to the Galaxy
- Proper error handling > panicking

---

## Conclusion

**Don't Panic!** is an excellent introduction to Rust reverse engineering. It demonstrates:
1. Rust binaries are larger but still reversible
2. Function pointer arrays are common in compiled code
3. Character-by-character validation is a CTF staple
4. Pattern recognition beats brute force

The flag itself is a lesson: in programming (and RE), don't panic - methodically catch and handle errors!

---

**Last Updated:** November 2025  
**Challenge Solved By:** Static analysis of Rust binary with function pointer array  
**Difficulty Rating:** Easy (with Rust knowledge) to Medium (without)  
**Time Required:** 30-60 minutes  
**Skills Learned:** Rust RE, function pointers, static analysis, pattern recognition
