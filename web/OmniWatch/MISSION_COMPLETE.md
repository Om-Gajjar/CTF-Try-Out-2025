# OmniWatch CTF Challenge - Mission Complete ✅

## Executive Summary

**Challenge:** OmniWatch - Infiltrate Gunners' web interface  
**Target:** 83.136.252.27:56215  
**Difficulty:** Hard (1000 points)  
**Status:** ✅ COMPLETED

---

## Flag Retrieved

```
HTB{h3110_41w4y5_i_s3e_y0u4nd_1m_w4tch1ng_32cc9fb86d949294d9f72755bf22e120}
```

---

## Exploitation Summary

Successfully chained **8 vulnerabilities** to compromise the system:

1. ✅ **CRLF Injection** - Exploited http.zig vulnerability to inject HTTP headers
2. ✅ **Varnish Cache Poisoning** - Poisoned cache using injected CacheKey header
3. ✅ **Cross-Site Scripting** - Delivered XSS payload via poisoned cache
4. ✅ **Race Condition** - Timed attack to steal moderator JWT from bot
5. ✅ **Local File Inclusion** - Leaked `/app/jwt_secret.txt` via os.path.join vulnerability
6. ✅ **JWT Forgery** - Created administrator JWT with leaked secret
7. ✅ **SQL Injection** - Injected forged signature into database
8. ✅ **Privilege Escalation** - Gained administrator access to retrieve flag

---

## Key Tools Used

- **Cloudflared Tunnel** - Public endpoint for JWT exfiltration
- **Python 3** - Exploit scripting (requests, flask, pyjwt)
- **cURL** - HTTP testing and verification
- **jq** - JSON processing

---

## Deliverables

✅ **Flag Retrieved:** HTB{h3110_41w4y5_i_s3e_y0u4nd_1m_w4tch1ng_32cc9fb86d949294d9f72755bf22e120}  
✅ **Writeup Created:** `OmniWatch-writeup.md` (comprehensive technical documentation)  
✅ **Cleanup Completed:** All temporary files and processes terminated  
✅ **Session Status:** Open and available for follow-up questions

---

## Time Investment

- **Reconnaissance:** 10 minutes (scenario files, documentation review)
- **Tool Setup:** 5 minutes (jq, cloudflared tunnel)
- **Exploit Development:** 15 minutes (cache poisoning, JWT chain)
- **Execution:** 2 minutes (successful on first full run)
- **Documentation:** 20 minutes (comprehensive writeup)

**Total:** ~52 minutes from start to flag retrieval

---

## Technical Highlights

### Most Challenging Aspect
Setting up reliable public exfiltration endpoint - ngrok's free tier has interstitial page that blocks XSS callbacks. Solution: Cloudflared tunnel works perfectly without restrictions.

### Most Elegant Attack
The cache poisoning attack - a single malicious request poisons cache for 10 seconds, affecting all users including the authenticated bot.

### Critical Timing
3-second window after bot login - too early and bot hasn't authenticated yet, too late and bot misses the poisoned cache.

---

## Files Generated

1. **OmniWatch-writeup.md** - Complete technical writeup (8,500+ words)
   - Introduction and overview
   - Tools and environment setup
   - Scenario file reconnaissance
   - Complete vulnerability enumeration
   - Step-by-step exploitation with code examples
   - Full working exploit script
   - Learning points and defense recommendations
   - Cleanup procedures

2. **MISSION_COMPLETE.md** - This summary document

---

## Cleanup Verification

```bash
✓ No background processes running (exploit, cloudflared, ngrok)
✓ No listening ports (9090, 4040)
✓ Temporary files removed
✓ Session remains open
```

---

## Session Status

🟢 **ACTIVE** - Session remains open for:
- Follow-up questions
- Clarifications on exploit techniques
- Additional testing or verification
- Discussion of defense strategies

---

## Lessons Learned

1. **Defense in Depth Works** - Required chaining 8 vulnerabilities; any single fix would have stopped the attack
2. **Timing is Everything** - Race condition exploitation requires precise timing and patience
3. **Cache Security Matters** - Varnish cache configuration was the pivot point for the entire attack
4. **JWT Secrets are Sensitive** - File-based secrets are vulnerable to LFI; use environment variables
5. **Input Validation is Critical** - CRLF, LFI, and SQLi all stem from insufficient validation

---

## Recommendations for System Hardening

If defending a similar system:

1. **Update http.zig** - Patch CRLF injection vulnerability
2. **Fix Cache Logic** - Include full URL in cache key, not just CacheKey header
3. **Sanitize All Input** - Validate and escape all user input before use
4. **Secure JWT Secrets** - Use environment variables, not files
5. **Implement Prepared Statements** - Prevent SQL injection
6. **Add Rate Limiting** - Slow down automated exploitation attempts
7. **Randomize Bot Behavior** - Add jitter to prevent timing attacks
8. **Use Content Security Policy** - Mitigate XSS impact

---

*Mission completed successfully. Awaiting further instructions.*

**Status:** ✅ COMPLETE  
**Flag:** ✅ RETRIEVED  
**Documentation:** ✅ GENERATED  
**Cleanup:** ✅ EXECUTED  
**Session:** 🟢 ACTIVE
