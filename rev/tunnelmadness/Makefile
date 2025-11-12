# Makefile for Tunnel Challenge Reconstruction

CC = gcc
CFLAGS = -Wall -O2 -g
TARGET = tunnel_rebuilt

all: $(TARGET)

$(TARGET): tunnel_reconstructed.c maze_data.c
	$(CC) $(CFLAGS) -o $(TARGET) tunnel_reconstructed.c maze_data.c

clean:
	rm -f $(TARGET) *.o

test: $(TARGET)
	@echo "Testing with local flag file..."
	@echo "HTB{test_flag_for_local_testing}" > flag.txt
	@echo "U\nU\nU\nR\nQ" | ./$(TARGET)
	@rm flag.txt

.PHONY: all clean test
