<h1 align="center">🧠 AI Notes · Neetpal Singh</h1>

<p align="center">
  A weekend learning log: short TILs, paper summaries and snippets from building<br/>
  agent platforms, MCP servers, Hybrid RAG and fine-tuned LLMs in production.
</p>

<p align="center">
  <a href="https://neetpalsingh.github.io/about.github.io/"><img src="https://img.shields.io/badge/Portfolio-FA5D19?style=flat-square" alt="Portfolio" /></a>
  <a href="https://github.com/neetpalsingh"><img src="https://img.shields.io/badge/GitHub-262626?style=flat-square&logo=github&logoColor=white" alt="GitHub" /></a>
  <a href="https://www.linkedin.com/in/neetpal-singh-690330218"><img src="https://img.shields.io/badge/LinkedIn-262626?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
</p>

---

<!-- INDEX:START -->
**2 notes** · 2 TILs · 0 papers · 0 snippets · 2 topics · active in 1 month

### 🆕 Latest

| Date | Note | Type | Topic |
|---|---|---|---|
| 2026-10-26 | [Semantic chunking beats fixed-size chunking](notes/rag/2026-10-26-semantic-chunking-beats-fixed-size-chunking.md) | 💡 TIL | `rag` |
| 2026-10-26 | [Nothing over ~2 seconds belongs in the request cycle](notes/backend/2026-10-26-keep-slow-work-out-of-the-request-cycle.md) | 💡 TIL | `backend` |

### 🗂️ By topic

<details><summary><b>backend</b> (1)</summary>

- 2026-10-26 · [Nothing over ~2 seconds belongs in the request cycle](notes/backend/2026-10-26-keep-slow-work-out-of-the-request-cycle.md) `fastapi` `rabbitmq` `websockets` `async`

</details>
<details><summary><b>rag</b> (1)</summary>

- 2026-10-26 · [Semantic chunking beats fixed-size chunking](notes/rag/2026-10-26-semantic-chunking-beats-fixed-size-chunking.md) `chunking` `extraction` `context-window`

</details>

### 🏷️ Tags

`chunking`×1 `extraction`×1 `context-window`×1 `fastapi`×1 `rabbitmq`×1 `websockets`×1 `async`×1
<!-- INDEX:END -->

---

## ✍️ Adding a note

**Queue it (recommended).** Write notes whenever you like; they publish themselves on weekends:

```bash
python scripts/new_note.py til "What I learned" --category rag --tags chunking,embeddings --draft
# fill in the note in drafts/, then:
git add . && git commit -m "Draft: what I learned" && git push
```

Every **Saturday and Sunday**, the [weekend publish](.github/workflows/weekend-publish.yml) workflow moves the oldest drafts into `notes/`, 2–3 per day at random times between ~11:00 and ~22:00 IST. It dates each one, rebuilds the index and commits it as Neetpal Singh. When `drafts/` is empty, it publishes nothing.

**Or publish straight away:**

```bash
python scripts/new_note.py paper "Paper title" --category agents     # also: til, snippet
python scripts/build_index.py                                        # optional; CI does it too
git add . && git commit -m "Paper: title" && git push
```

To publish a queued draft on demand: **Actions → Weekend publish → Run workflow**.

Topics live in `notes/`: `rag`, `agents`, `mcp`, `llm`, `fine-tuning`, `backend`. Any new `--category` creates a new folder.
