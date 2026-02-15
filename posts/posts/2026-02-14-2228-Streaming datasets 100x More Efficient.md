---
title: "Streaming datasets: 100x More Efficient"
date: "2026-02-14T22:28:05.630043"
source: "HuggingFace"
author: "Unknown"
link: "https://huggingface.co/blog/streaming-datasets"
published: "Mon, 27 Oct 2025 00:00:00 GMT"
---

We boosted load_dataset('dataset', streaming=True), streaming datasets without downloading them with one line of code!
Start training on multi-TB datasets immediately, without complex setups, downloading, no "disk out of space", or 429 “stop requesting!” errors.It's super fast! Outrunning our local SSDs when training on 64xH100 with 256 workers downloading data.
We've improved streaming to have 100x fewer requests, → 10× faster data resolution → 2x sample/sec, → 0 worker crashes at 256 concurren...

[Read full article](https://huggingface.co/blog/streaming-datasets)
