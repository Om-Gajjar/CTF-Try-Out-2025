# Labyrinth - PWN Challenge

**Status:** ✅ SOLVED  
**Difficulty:** Easy (1000 points)  
**Flag:** `HTB{3sc4p3_fr0m_4b0v3}`

## Quick Start

```bash
# Run the exploit
python3 exploit.py
```

## Files

- `labyrinth` - The vulnerable binary
- `exploit.py` - Working exploit script (documented)
- `SOLUTION_GUIDE.md` - Complete walkthrough for 2nd year BSc IT students
- `flag.txt` - Local test flag

## Challenge Summary

This challenge involves:
1. Finding door 69 triggers a second prompt
2. Exploiting a buffer overflow (68 bytes read into 48-byte buffer)
3. Overwriting the return address with `escape_plan` function address
4. Using a RET gadget for x64 stack alignment

## Key Learning Points

- Buffer overflow exploitation basics
- Return address overwrite technique
- x64 stack alignment requirements
- Binary analysis with objdump/nm
- Pwntools usage

## Solution in 3 Steps

1. **Select door 69** at first prompt
2. **Send overflow payload**: 56 bytes padding + RET gadget (0x401016) + escape_plan (0x401255)
3. **Receive flag** from the hidden `escape_plan` function

See `SOLUTION_GUIDE.md` for detailed explanation!
