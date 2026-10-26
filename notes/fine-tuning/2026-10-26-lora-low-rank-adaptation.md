---
title: "LoRA: Low-Rank Adaptation of Large Language Models"
date: 2026-10-26
type: paper
category: fine-tuning
tags: [lora, peft, fine-tuning]
paper: https://arxiv.org/abs/2106.09685
---

# LoRA: Low-Rank Adaptation of Large Language Models

**TL;DR:** Freeze the pretrained weights and learn a low-rank update `ΔW = B·A` for selected layers. You get a tiny number of trainable parameters, no extra inference latency, and quality on par with full fine-tuning. *(Hu et al., 2021)*

## Problem
Full fine-tuning updates every weight, so each task needs a full copy of a huge model, plus heavy GPU memory for gradients and optimizer state.

## Key idea
For a frozen weight `W₀ ∈ ℝ^{d×k}`, learn `B ∈ ℝ^{d×r}` and `A ∈ ℝ^{r×k}` with rank `r ≪ min(d, k)`:

```
h = W₀x + (α / r) · B·A·x        # B starts at zero, so training starts from W₀
```

The paper applies it to the attention projections (mainly `W_q` and `W_v`). After training, `B·A` can be merged into `W₀`, so inference costs the same as the base model.

## Results
- On GPT-3 175B: about **10,000× fewer trainable parameters** and **3× less GPU memory** than full fine-tuning.
- Matches or beats full fine-tuning on RoBERTa, DeBERTa, GPT-2 and GPT-3 benchmarks.
- Very small ranks (even r = 1–8) work surprisingly well, which suggests task-specific updates are low-rank.

## My take
- This is what made fine-tuning LLaMA 7B and Mistral on compliance-domain data practical for me. QLoRA (4-bit base model + LoRA adapters) plus Unsloth pushed it onto a single GPU.
- One small adapter per domain is easy to version and swap without duplicating the base model.
- Watch out: the rank, alpha and target modules matter. Start with `r=16`, `α=32` on attention projections and evaluate on held-out domain data.

## References
- Hu et al., *LoRA: Low-Rank Adaptation of Large Language Models*, 2021: https://arxiv.org/abs/2106.09685
- Dettmers et al., *QLoRA: Efficient Finetuning of Quantized LLMs*, 2023: https://arxiv.org/abs/2305.14314
