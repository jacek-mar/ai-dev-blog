---
title: "Accelerating Qwen3-8B Agent on Intel® Core™ Ultra with Depth-Pruned Draft Models"
date: "2026-02-14T22:28:17.076321"
source: "HuggingFace"
author: "Unknown"
link: "https://huggingface.co/blog/intel-qwen3-agent"
published: "Mon, 29 Sep 2025 00:00:00 GMT"
---

TL;DR:
Qwen3-8B is one of the most exciting recent releases—a model with  native agentic capabilities, making it a natural fit for the AIPC.
With OpenVINO.GenAI, we’ve been able to accelerate generation by ~1.3× using speculative decoding with a lightweight Qwen3-0.6B draft.
By using speculative decoding and applying a simple pruning process to the draft, we pushed the speedup even further to ~1.4×
We wrapped this up by showing how these improvements can be used to run a fast, local AI Agent wit...

[Read full article](https://huggingface.co/blog/intel-qwen3-agent)
