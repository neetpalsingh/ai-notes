---
title: HttpOnly cookies over JWTs in localStorage
date: 2026-10-26
type: til
category: backend
tags: [auth, security, xss, csrf, sso]
---

# HttpOnly cookies over JWTs in localStorage

**TL;DR:** Storing auth tokens in HttpOnly cookies instead of localStorage removes the XSS token-theft surface, and SameSite adds CSRF protection for free.

## Why I switched
- JavaScript can't read an HttpOnly cookie, so an XSS bug can't exfiltrate the token.
- `SameSite` gives built-in CSRF protection.
- It works cleanly with an iframe-embedded chatbot widget and Google/Microsoft OAuth.

## The trade-offs
- Native mobile clients find cookies more awkward than bearer tokens.
- You can't inspect the token in DevTools as easily.
- Some statelessness is lost: Redis now tracks active sessions.

## Gotcha
Every frontend request needs `credentials: 'include'`, and the backend needs matching CORS settings. In Agent Studio that touch-every-endpoint migration took about three weeks, but SSO got noticeably simpler afterwards.
