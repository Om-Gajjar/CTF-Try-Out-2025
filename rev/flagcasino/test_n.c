#include <stdio.h>
#include <stdlib.h>

int main() {
    // Test if 'n' produces the expected value
    srand('n');  // 'n' = 0x6e
    unsigned int result = rand();
    printf("srand('n' = 0x6e) -> rand() = 0x%08x\n", result);
    printf("Expected: 0x33c4d4b0\n");
    
    if (result == 0x33c4d4b0) {
        printf("MATCH! The character is 'n'\n");
    } else {
        printf("No match. Trying nearby characters...\n");
        for (int c = 'a'; c <= 'z'; c++) {
            srand(c);
            if (rand() == 0x33c4d4b0) {
                printf("Found: '%c' (0x%02x)\n", c, c);
                return 0;
            }
        }
    }
    
    return 0;
}
