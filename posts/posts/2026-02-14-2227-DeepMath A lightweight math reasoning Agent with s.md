---
title: "DeepMath: A lightweight math reasoning Agent with smolagents"
date: "2026-02-14T22:27:51.219473"
source: "HuggingFace"
author: "Unknown"
link: "https://huggingface.co/blog/intel-deepmath"
published: "Thu, 04 Dec 2025 00:00:00 GMT"
---

By Intel AI Software Group
DeepMath is an aligned math reasoning agent built on Qwen3-4B Thinking and fine-tuned with GRPO (Group Relative Policy Optimization). Instead of verbose text, the model emits tiny Python snippets for intermediate steps, runs them in a secure sandbox, and folds the results back into its reasoning, reducing errors and output length. The agent is implemented using the smolagents library.
We evaluate DeepMath on four math datasets: MATH500, AIME, HMMT, and HLE, and show th...

[Read full article](https://huggingface.co/blog/intel-deepmath)
