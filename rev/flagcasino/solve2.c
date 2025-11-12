#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

// Let me re-extract these values more carefully
uint32_t check[] = {
    0x244b28be, 0x0af77805, 0x110dfc17, 0x07afc3a1,
    0x6afec533, 0x4ed659a2, 0x33c4d4b0, 0x286582b8,
    0x43383720, 0x055a14fc, 0x19195f9f, 0x43383720,
    0x631493, 0x615ab299, 0x6afec533, 0x6c6fcfb8,
    0x43383720, 0x0f3da237, 0x6afec533, 0x615ab299,
    0x286582b8, 0x055a14fc, 0x3ae44994, 0x06d7dfe9,
    0x4ed659a2, 0x0ccd4acd, 0x57d8ed64, 0x615ab299,
    0x22e9bc2a
};

int main() {
    char flag[30] = {0};
    int num_checks = sizeof(check) / sizeof(check[0]);
    
    printf("Trying extended ASCII range...\n");
    
    for (int i = 0; i < num_checks; i++) {
        int found = 0;
        // Try all possible byte values 0-255
        for (int c = 0; c <= 255; c++) {
            srand(c);
            uint32_t result = rand();
            
            if (result == check[i]) {
                if (c >= 32 && c <= 126) {
                    flag[i] = c;
                    printf("[%d] Found: '%c' (0x%02x) -> 0x%08x\n", i, c, c, result);
                } else {
                    flag[i] = c;
                    printf("[%d] Found: <0x%02x> -> 0x%08x\n", i, c, result);
                }
                found = 1;
                break;
            }
        }
        
        if (!found) {
            printf("[%d] NOT FOUND for: 0x%08x\n", i, check[i]);
            flag[i] = '?';
        }
    }
    
    printf("\nFlag characters:\n");
    for (int i = 0; i < num_checks; i++) {
        if (flag[i] >= 32 && flag[i] <= 126) {
            printf("%c", flag[i]);
        } else {
            printf("[0x%02x]", (unsigned char)flag[i]);
        }
    }
    printf("\n");
    
    return 0;
}
