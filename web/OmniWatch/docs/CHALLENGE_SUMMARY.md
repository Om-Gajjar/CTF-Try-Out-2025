# OmniWatch CTF Challenge

## Overview

OmniWatch is a hard-difficulty CTF challenge that simulates a vulnerable web interface used by the mercenary group "Gunners" to track and spy on their enemies. The goal is to exploit multiple vulnerabilities to gain administrator access and retrieve the flag containing the last known location of an ambushed caravan.

## Challenge Architecture

The challenge consists of three main services running behind a Varnish cache:

1. **Controller Service** (Flask, port 3000) - Web application with authentication and device management
2. **Oracle Service** (Zig, port 4000) - HTTP API for device location tracking
3. **Varnish Cache** (port 1337) - Caching layer that routes requests to backend services

## Deployment

### Build and Run

```bash
chmod +x build_docker.sh
./build_docker.sh
```

This will:
- Build the Docker image
- Remove any existing container
- Run the challenge on port 1337

### Manual Build

```bash
docker build -t web_omniwatch .
docker run --name=web_omniwatch --rm -p1337:1337 -it web_omniwatch
```

## Vulnerability Chain

This challenge requires chaining multiple vulnerabilities:

### 1. CRLF Injection (http.zig)
- **Location**: `challenge/oracle/modules/response.zig`
- **Description**: The `header()` function doesn't sanitize input, allowing CRLF injection via `\r\n`
- **Impact**: Arbitrary HTTP header injection

### 2. Cache Poisoning (Varnish)
- **Location**: `config/cache.vcl`
- **Description**: Uses `CacheKey` header for cache hash generation
- **Impact**: Can poison cache to serve malicious responses to all users

### 3. XSS via Content-Type Manipulation
- **Description**: Combine CRLF injection with XSS payload in URL parameters
- **Impact**: Steal cookies from authenticated users

### 4. Race Condition (Selenium Bot)
- **Location**: `challenge/controller/application/util/bot.py`
- **Description**: Bot logs in every 30 seconds and visits random oracle endpoints
- **Impact**: Timing window to steal moderator JWT cookie

### 5. Local File Inclusion (LFI)
- **Location**: `challenge/controller/application/blueprints/routes.py` (firmware endpoint)
- **Description**: Uses `os.path.join()` with user input without validation
- **Impact**: Read arbitrary files including JWT secret

### 6. SQL Injection
- **Location**: `challenge/controller/application/util/database.py` (fetch_device method)
- **Description**: F-string interpolation without sanitization
- **Impact**: Insert arbitrary JWT signatures into database

### 7. JWT Forgery
- **Description**: Combine leaked JWT secret with SQL injection to bypass tamper protection
- **Impact**: Gain administrator access

## Solution Steps

1. Monitor bot status via `/controller/bot_running`
2. Wait for bot activation
3. Poison cache with XSS payload + CRLF headers (CacheKey: enable, Content-Type: text/html)
4. Steal moderator JWT cookie
5. Use moderator access to exploit LFI: read `/app/jwt_secret.txt`
6. Forge administrator JWT with leaked secret
7. Exploit SQL injection to insert forged JWT signature
8. Access `/controller/admin` with forged JWT
9. Retrieve flag

## Solver Script

A complete solver script is provided at `solver.py` that automates the entire exploit chain:

```bash
python3 solver.py
```

**Note**: The solver requires:
- Challenge running on localhost:1337
- Network access to 172.17.0.1:9090 for exfiltration server

## Security Features (Intentional Weaknesses)

This challenge intentionally includes:
- Outdated http.zig version with CRLF vulnerability
- Insecure Varnish configuration
- SQL injection vulnerabilities
- Path traversal in file operations
- Weak JWT implementation

These are for educational purposes only and demonstrate real-world vulnerability patterns.

## Flag Format

The flag follows the format: `HTB{...}`

## Difficulty

**Hard** - Requires:
- Understanding of Varnish cache mechanics
- Knowledge of HTTP header injection
- Python and Zig programming knowledge
- JWT manipulation skills
- Race condition exploitation
- SQL injection techniques

## Credits

- **Author**: Lean
- **Category**: Web
- **Difficulty**: Hard
- **Points**: 1000

## Documentation

For a detailed writeup including screenshots and code analysis, see `doc.md`.
