---
title: "No GPU left behind: Unlocking Efficiency with Co-located vLLM in TRL"
date: "2026-02-14T22:29:04.833348"
source: "HuggingFace"
author: "Unknown"
link: "https://huggingface.co/blog/vllm-colocate"
published: "Tue, 03 Jun 2025 00:00:00 GMT"
---

TRL supports training LLMs using GRPO, an online learning algorithm recently introduced in the DeepSeekMath paper. In GRPO, the model learns from its own outputs: it generates responses during training, receives feedback, and uses that feedback to improve itself over time.
This makes generation a critical step in the training loop — and also a major bottleneck. To speed up generation, TRL integrates with vLLM.

[Read full article](https://huggingface.co/blog/vllm-colocate)
