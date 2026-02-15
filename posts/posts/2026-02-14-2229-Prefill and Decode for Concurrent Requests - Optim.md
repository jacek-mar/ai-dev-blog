---
title: "Prefill and Decode for Concurrent Requests - Optimizing LLM Performance"
date: "2026-02-14T22:29:22.286895"
source: "HuggingFace"
author: "Unknown"
link: "https://huggingface.co/blog/tngtech/llm-performance-prefill-decode-concurrent-requests"
published: "Wed, 16 Apr 2025 10:10:58 GMT"
---

Handling load from multiple users in parallel is crucial for the performance of LLM applications. In the previous part of our series on LLM performance, we discussed queueing strategies for the prioritization of different users. In this second part, we will now focus on the concurrent processing of requests, and how it impacts relevant metrics such as latency and throughput as well as GPU resource utilization.
At TNG, we are self-hosting numerous Large Language Models on our cluster of 24 H100 G...

[Read full article](https://huggingface.co/blog/tngtech/llm-performance-prefill-decode-concurrent-requests)
