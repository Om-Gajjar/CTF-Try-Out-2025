# Dynamic Path Sum - CTF Coding Challenge

## 📋 Challenge Information

**Category:** Coding / Programming  
**Difficulty:** Medium  
**Challenge Type:** Dynamic Programming - Minimum Path Sum  
**Tests:** 100 test cases  

## 📝 Challenge Description

This is a programming challenge where you must solve 100 minimum path sum problems in real-time. You connect to a server that provides grid dimensions and values, and you must calculate the minimum sum path from top-left to bottom-right, moving only down or right.

## 🎯 Problem Statement

Given a grid of size `i × j` where `2 <= i, j <= 100`, with values `n_i,j` where `1 <= n_i,j <= 50`:

- Start at top-left corner
- Goal: reach bottom-right corner
- Constraint: can only move **down** or **right**
- Objective: minimize the sum of all numbers on the path

### Example

**Input:**
```
4 3
2 5 1 9 2 3 9 1 3 11 7 4
```

**Grid:**
```
 2  5  1
 9  2  3
 9  1  3
11  7  4
```

**Output:** `17`  
**Optimal Path:** 2 → 5 → 2 → 1 → 3 → 4

## 🚀 Quick Start

### Prerequisites

- Python 3.6+
- Network access to challenge server
- No external dependencies (uses only standard library)

### Running the Solution

```bash
# Navigate to the solution directory
cd coding/solution

# Run the final solution (recommended)
python3 solve_final.py

# Or try other solution versions
python3 solve_dynamic_paths.py
python3 solve3.py
python3 solve2.py
```

## 📁 Folder Structure

```
coding/
├── README.md              # This file
├── solution/              # Solution scripts
│   ├── solve_final.py    # Final working solution (recommended)
│   ├── solve_dynamic_paths.py  # Alternative implementation
│   ├── solve3.py         # Version 3
│   └── solve2.py         # Version 2
├── data/                  # Test data and logs
│   ├── output.log        # Solution output
│   └── result.log        # Detailed results
└── docs/                  # Additional documentation
```

## 🔧 Technical Details

### Algorithm: Dynamic Programming

The solution uses a 2D DP table where `dp[i][j]` represents the minimum sum to reach cell `(i, j)`.

**Approach:**
```python
def solve_min_path(rows, cols, grid):
    # Initialize DP table
    dp = [[0] * cols for _ in range(rows)]
    dp[0][0] = grid[0][0]
    
    # Fill first row (can only come from left)
    for j in range(1, cols):
        dp[0][j] = dp[0][j-1] + grid[0][j]
    
    # Fill first column (can only come from above)
    for i in range(1, rows):
        dp[i][0] = dp[i-1][0] + grid[i][0]
    
    # Fill rest of table (min of coming from above or left)
    for i in range(1, rows):
        for j in range(1, cols):
            dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])
    
    return dp[rows-1][cols-1]
```

### Time Complexity
- Per grid: `O(rows × cols)`
- Total: `O(100 × rows × cols)`
- Worst case: `O(100 × 100 × 100) = O(1,000,000)` operations

### Space Complexity
- `O(rows × cols)` for DP table
- Can be optimized to `O(min(rows, cols))` with rolling array

## 💡 Solution Walkthrough

### Step 1: Connect to Server
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))
f = sock.makefile('rw', buffering=1)
```

### Step 2: Parse Input
```python
# Read dimensions
dims_line = f.readline().strip()
rows, cols = map(int, dims_line.split())

# Read values
values_line = f.readline().strip()
nums = list(map(int, values_line.split()))

# Build grid
grid = [[nums[i * cols + j] for j in range(cols)] for i in range(rows)]
```

### Step 3: Solve with DP
```python
result = solve_min_path(rows, cols, grid)
```

### Step 4: Submit Answer
```python
f.write(f"{result}\n")
f.flush()
```

### Step 5: Check for Flag
```python
response = f.readline()
if 'HTB{' in response:
    print(f"FLAG: {response}")
```

## 🐛 Troubleshooting

### Connection Issues
```bash
# Test connectivity
nc -zv <host> <port>

# Check if server is responding
echo "test" | nc <host> <port>
```

### Parsing Errors
- Ensure you skip any empty lines or test headers
- Verify dimensions before accessing grid
- Check for off-by-one errors

### Wrong Answers
- Verify DP initialization (first cell is grid[0][0])
- Ensure you're taking minimum of (up, left) not maximum
- Check that you're reading correct number of values

### Timeout Issues
- The solution should complete in < 1 second per grid
- If timing out, optimize by avoiding unnecessary operations
- Consider using iterative approach instead of recursive

## 📖 Learning Points

1. **Dynamic Programming:** Classic minimum path sum problem
2. **Socket Programming:** Real-time server interaction
3. **Input Parsing:** Handling structured text input
4. **Algorithm Optimization:** Time complexity considerations
5. **Automation:** Solving 100 test cases programmatically

## ✅ Expected Output

```
Test 1/100
=== Test 1/100 ===
4x3 -> Answer: 17
Response: Correct!

Test 2/100
=== Test 2/100 ===
5x5 -> Answer: 42
Response: Correct!

...

Test 100/100
=== Test 100/100 ===
100x100 -> Answer: 5234
Response: HTB{dynamic_programming_master_2025}

===FLAG: HTB{...}===
```

## 🏆 Success Criteria

- Successfully solve all 100 test cases
- Implement correct DP algorithm
- Handle all edge cases (2x2 minimum, 100x100 maximum)
- Extract the flag from final response
- Flag format: `HTB{...}`

---

**Challenge Type:** Algorithmic Problem Solving  
**Key Algorithm:** Dynamic Programming (Minimum Path Sum)  
**Difficulty:** Medium (requires DP knowledge and fast implementation)  
**Time Limit:** Real-time solving (typically ~1 second per test case)
