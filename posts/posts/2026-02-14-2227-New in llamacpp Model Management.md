---
title: "New in llama.cpp: Model Management"
date: "2026-02-14T22:27:49.127302"
source: "HuggingFace"
author: "Unknown"
link: "https://huggingface.co/blog/ggml-org/model-management-in-llamacpp"
published: "Thu, 11 Dec 2025 15:47:44 GMT"
---

llama.cpp server now ships with router mode, which lets you dynamically load, unload, and switch between multiple models without restarting.
Reminder: llama.cpp server is a lightweight, OpenAI-compatible HTTP server for running LLMs locally.
This feature was a popular request to bring Ollama-style model management to llama.cpp. It uses a multi-process architecture where each model runs in its own process, so if one model crashes, others remain unaffected.
Start the server in router mode by not s...

[Read full article](https://huggingface.co/blog/ggml-org/model-management-in-llamacpp)
