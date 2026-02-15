---
title: "Make your ZeroGPU Spaces go brrr with ahead-of-time compilation"
date: "2026-02-14T22:28:30.752738"
source: "HuggingFace"
author: "Unknown"
link: "https://huggingface.co/blog/zerogpu-aoti"
published: "Tue, 02 Sep 2025 00:00:00 GMT"
---

ZeroGPU lets anyone spin up powerful Nvidia H200 hardware in Hugging Face Spaces without keeping a GPU locked for idle traffic.
It’s efficient, flexible, and ideal for demos but it doesn’t always make full use of everything the GPU and CUDA stack can offer.
Generating images or videos can take a significant amount of time. Being able to squeeze out more performance, taking advantage of the H200 hardware, does matter in this case.
This is where PyTorch ahead-of-time (AoT) compilation comes in.

[Read full article](https://huggingface.co/blog/zerogpu-aoti)
