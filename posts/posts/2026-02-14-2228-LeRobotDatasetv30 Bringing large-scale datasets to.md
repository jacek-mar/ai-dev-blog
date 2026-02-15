---
title: "`LeRobotDataset:v3.0`: Bringing large-scale datasets to `lerobot`"
date: "2026-02-14T22:28:24.237426"
source: "HuggingFace"
author: "Unknown"
link: "https://huggingface.co/blog/lerobot-datasets-v3"
published: "Tue, 16 Sep 2025 00:00:00 GMT"
---

TL;DR Today we release LeRobotDataset:v3! In our previous LeRobotDataset:v2 release, we stored one episode per file, hitting file-system limitations when scaling datasets to millions of episodes. LeRobotDataset:v3 packs multiple episodes in a single file, using relational metadata to retrieve information at the individual episode level from multi-episode files. The new format also natively supports accessing datasets in streaming mode, allowing to process large datasets on the fly.We provide a o...

[Read full article](https://huggingface.co/blog/lerobot-datasets-v3)
