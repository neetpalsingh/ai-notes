---
title: Semantic chunking beats fixed-size chunking
date: 2026-10-26
type: til
category: rag
tags: [chunking, extraction, context-window]
---

# Semantic chunking beats fixed-size chunking

**TL;DR:** Split long documents on paragraph/heading boundaries with a small overlap, not on a fixed token count. In Agent Studio this improved downstream extraction accuracy by about 40%.

## Context
Agent APIs in Agent Studio had to process 100+ page PDFs, far beyond any single model's context window. The first version split on a fixed token count and regularly cut sentences in half.

## What I learned
1. **Gate on a token budget first.** Reserve ~25% of the model's context window for the response and only chunk when the prompt exceeds what's left.
2. **Chunk on structure.** Paragraph and heading boundaries keep facts intact; a ~200-token overlap preserves context that spans a boundary.
3. **Merge by output format.** JSON results merge structurally (arrays concatenated, objects combined); free text is joined with a visible separator so reviewers can see chunk boundaries.

```python
available = context_limit * 0.75            # keep 25% for the answer
if count_tokens(prompt) <= available:
    return await llm.ainvoke(prompt)
chunks = chunk_text(prompt, max_tokens=int(available), overlap=200)   # paragraph/heading aware
results = [await llm.ainvoke(c) for c in chunks]
return merge_json_results(results) if want_json else "\n\n---\n\n".join(results)
```

## Why it matters
Most "the model missed it" extraction bugs were really chunking bugs. Fix the split before reaching for a bigger model.
