/*
 * Tunnel - HackTheBox Challenge
 * Reconstructed from reverse engineering the binary
 * 3D Maze Navigation Game
 */

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

// Cell structure for maze
typedef struct {
    int x;
    int y;
    int z;
    int type;
} Cell;

// Position structure  
typedef struct {
    int x;
    int y;
    int z;
} Position;

// External maze data (see maze_data.c for full array)
// In the real binary, this is in .rodata section at offset 0x20e0
extern Cell maze[8000];

/*
 * get_cell - Get cell at position (x, y, z)
 * 
 * Algorithm from disassembly:
 *   rax = x * 5 * 5 * 16 = x * 400
 *   rdx = y * 5 * 4 = y * 20
 *   rax = x * 400 + y * 20 + z
 *   rax = rax * 16 (shift left 4)
 *   return &maze[index]
 */
Cell* get_cell(Position* pos) {
    int x = pos->x;
    int y = pos->y;
    int z = pos->z;
    
    // Calculate index: (x * 400 + y * 20 + z) * 16 bytes
    // But since Cell is 16 bytes, the array index is just:
    // x * 400 + y * 20 + z
    int index = x * 400 + y * 20 + z;
    
    return &maze[index];
}

/*
 * get_flag - Read and display flag from /flag.txt
 */
void get_flag() {
    FILE* fp;
    char buffer[128];
    
    // Clear buffer
    memset(buffer, 0, sizeof(buffer));
    
    fp = fopen("/flag.txt", "r");
    if (fp == NULL) {
        puts("Flag file not found!");
        return;
    }
    
    fgets(buffer, 128, fp);
    puts(buffer);
    fclose(fp);
}

/*
 * prompt_and_update_pos - Get user input and update position
 * 
 * Reads a direction character (L/R/F/B/U/D/Q)
 * Validates the move by checking if target cell is not a wall (type 2)
 * Updates position if valid, otherwise prints error
 */
void prompt_and_update_pos(Position* pos) {
    char input;
    Position temp_pos;
    Cell* target_cell;
    
    printf("Direction (L/R/F/B/U/D/Q)? ");
    
    if (scanf(" %c", &input) != 1) {
        exit(-1);
    }
    
    // Convert to uppercase
    input = toupper(input);
    
    // Copy current position to temp
    temp_pos.x = pos->x;
    temp_pos.y = pos->y;
    temp_pos.z = pos->z;
    
    // Switch based on input character
    // The binary uses a jump table at offset 0x2080
    switch (input) {
        case 'B':  // Backward: x--
            if (pos->x == 0) {
                puts("Cannot move that way");
                return;
            }
            temp_pos.x = pos->x - 1;
            target_cell = get_cell(&temp_pos);
            if (target_cell->type == 2) {
                puts("Cannot move that way");
                return;
            }
            pos->x = temp_pos.x;
            pos->z = temp_pos.z;
            break;
            
        case 'F':  // Forward: x++
            if (pos->x == 19) {
                puts("Cannot move that way");
                return;
            }
            temp_pos.x = pos->x + 1;
            target_cell = get_cell(&temp_pos);
            if (target_cell->type == 2) {
                puts("Cannot move that way");
                return;
            }
            pos->x = temp_pos.x;
            pos->z = temp_pos.z;
            break;
            
        case 'L':  // Left: y--
            if (pos->y == 0) {
                puts("Cannot move that way");
                return;
            }
            temp_pos.y = pos->y - 1;
            target_cell = get_cell(&temp_pos);
            if (target_cell->type == 2) {
                puts("Cannot move that way");
                return;
            }
            pos->x = temp_pos.x;
            pos->z = temp_pos.z;
            break;
            
        case 'R':  // Right: y++
            if (pos->y == 19) {
                puts("Cannot move that way");
                return;
            }
            temp_pos.y = pos->y + 1;
            target_cell = get_cell(&temp_pos);
            if (target_cell->type == 2) {
                puts("Cannot move that way");
                return;
            }
            pos->x = temp_pos.x;
            pos->z = temp_pos.z;
            break;
            
        case 'D':  // Down: z--
            if (pos->z == 0) {
                puts("Cannot move that way");
                return;
            }
            temp_pos.z = pos->z - 1;
            target_cell = get_cell(&temp_pos);
            if (target_cell->type == 2) {
                puts("Cannot move that way");
                return;
            }
            pos->x = temp_pos.x;
            pos->z = temp_pos.z;
            break;
            
        case 'U':  // Up: z++
            if (pos->z == 19) {
                puts("Cannot move that way");
                return;
            }
            temp_pos.z = pos->z + 1;
            target_cell = get_cell(&temp_pos);
            if (target_cell->type == 2) {
                puts("Cannot move that way");
                return;
            }
            pos->x = temp_pos.x;
            pos->z = temp_pos.z;
            break;
            
        case 'Q':  // Quit
            puts("Goodbye!");
            exit(0);
            break;
            
        default:
            // Invalid input, do nothing
            break;
    }
}

/*
 * main - Main game loop
 * 
 * Initialize position to (0, 0, 0)
 * Loop:
 *   - Print newline
 *   - Get user input and update position
 *   - Check if current cell type is 3 (goal)
 *   - If goal, print success message and get flag
 */
int main() {
    Position pos;
    Cell* current_cell;
    
    // Initialize starting position
    pos.x = 0;
    pos.y = 0;
    pos.z = 0;
    
    // Main game loop
    while (1) {
        putchar('\n');
        
        prompt_and_update_pos(&pos);
        
        current_cell = get_cell(&pos);
        
        // Check if reached goal (cell type 3)
        if (current_cell->type == 3) {
            puts("You break into the vault and read the secrets within...");
            get_flag();
            return 0;
        }
    }
    
    return 0;
}
