---
title: Nothing over ~2 seconds belongs in the request cycle
date: 2026-10-26
type: til
category: backend
tags: [fastapi, rabbitmq, websockets, async]
---

# Nothing over ~2 seconds belongs in the request cycle

**TL;DR:** Moving document ingestion out of the FastAPI handler into a queue worker cut upload response time from ~45 s to ~200 ms and stopped duplicate uploads.

## Context
Uploads used to run inline: extract text, chunk, embed, write to the vector DB, then respond. That took 30–45 s for a large PDF.

## What went wrong
- Users watched a spinner past the point of trusting it and clicked upload again, which created duplicates.
- Anything over 60 s hit the API timeout and died.
- FastAPI's limited worker pool meant one slow upload stalled unrelated requests.

## The fix
1. Accept the file, save it to temporary storage, return `{"status": "queued"}` in ~200 ms.
2. A RabbitMQ worker does extraction, chunking and embedding off the request path.
3. A WebSocket event tells the UI when it's done, so it shows real progress instead of a stuck spinner.

## Why it matters
The same rule covers crawling, exports, emails and payments: if it can take more than ~2 s, queue it and notify.
