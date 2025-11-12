# OmniWatch

A hard-difficulty CTF challenge featuring web exploitation through cache poisoning, CRLF injection, SQL injection, and JWT manipulation.

## Quick Start

```bash
chmod +x build_docker.sh
./build_docker.sh
```

The challenge will be available at `http://localhost:1337`

## Challenge Description

You have found the IP of a web interface gunners use to track and spy on foes. Hack in and retrieve the last known location of a caravan that got ambushed in order to find an infamous black market seller to trade with.

## Architecture

- **Varnish Cache** (port 1337) - Entry point
- **Flask Controller** (port 3000) - Web application
- **Zig Oracle** (port 4000) - Device tracking API
- **MySQL Database** - Data storage
- **Selenium Bot** - Automated moderator

## Solve

Run the automated solver:

```bash
python3 solver.py
```

## Documentation

- `CHALLENGE_SUMMARY.md` - Quick reference guide
- `doc.md` - Complete writeup with screenshots

## Difficulty

**Hard** | 1000 Points | Web Exploitation

## Author

Lean