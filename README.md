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
**4 notes** · 3 TILs · 1 paper · 0 snippets · 3 topics · active in 1 month

### 🆕 Latest

| Date | Note | Type | Topic |
|---|---|---|---|
| 2026-10-26 | [Semantic chunking beats fixed-size chunking](notes/rag/2026-10-26-semantic-chunking-beats-fixed-size-chunking.md) | 💡 TIL | `rag` |
| 2026-10-26 | [Nothing over ~2 seconds belongs in the request cycle](notes/backend/2026-10-26-keep-slow-work-out-of-the-request-cycle.md) | 💡 TIL | `backend` |
| 2026-10-26 | [LoRA: Low-Rank Adaptation of Large Language Models](notes/fine-tuning/2026-10-26-lora-low-rank-adaptation.md) | 📄 Paper | `fine-tuning` |
| 2026-10-26 | [HttpOnly cookies over JWTs in localStorage](notes/backend/2026-10-26-httponly-cookies-over-jwt-in-localstorage.md) | 💡 TIL | `backend` |

### 🗂️ By topic

<details><summary><b>backend</b> (2)</summary>

- 2026-10-26 · [Nothing over ~2 seconds belongs in the request cycle](notes/backend/2026-10-26-keep-slow-work-out-of-the-request-cycle.md) `fastapi` `rabbitmq` `websockets` `async`
- 2026-10-26 · [HttpOnly cookies over JWTs in localStorage](notes/backend/2026-10-26-httponly-cookies-over-jwt-in-localstorage.md) `auth` `security` `xss` `csrf` `sso`

</details>
<details><summary><b>fine-tuning</b> (1)</summary>

- 2026-10-26 · [LoRA: Low-Rank Adaptation of Large Language Models](notes/fine-tuning/2026-10-26-lora-low-rank-adaptation.md) `lora` `peft` `fine-tuning`

</details>
<details><summary><b>rag</b> (1)</summary>

- 2026-10-26 · [Semantic chunking beats fixed-size chunking](notes/rag/2026-10-26-semantic-chunking-beats-fixed-size-chunking.md) `chunking` `extraction` `context-window`

</details>

### 🏷️ Tags

`chunking`×1 `extraction`×1 `context-window`×1 `fastapi`×1 `rabbitmq`×1 `websockets`×1 `async`×1 `lora`×1 `peft`×1 `fine-tuning`×1 `auth`×1 `security`×1 `xss`×1 `csrf`×1 `sso`×1
<!-- INDEX:END -->

---

## ✍️ Adding a note

```bash
# TIL, paper summary or snippet: creates notes/<topic>/<date>-<slug>.md from a template
python scripts/new_note.py til "What I learned" --category rag --tags chunking,embeddings
python scripts/new_note.py paper "Paper title" --category agents
python scripts/new_note.py snippet "Useful helper" --category backend

# optional: rebuild the index locally (the GitHub Action also does this on every push)
python scripts/build_index.py

git add . && git commit -m "TIL: what I learned" && git push
```

Topics live in `notes/`: `rag`, `agents`, `mcp`, `llm`, `fine-tuning`, `backend`. Any new `--category` creates a new folder.
