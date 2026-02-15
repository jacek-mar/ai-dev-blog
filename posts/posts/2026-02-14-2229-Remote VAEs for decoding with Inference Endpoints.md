---
title: "Remote VAEs for decoding with Inference Endpoints 🤗"
date: "2026-02-14T22:29:46.164956"
source: "HuggingFace"
author: "Unknown"
link: "https://huggingface.co/blog/remote_vae"
published: "Mon, 24 Feb 2025 00:00:00 GMT"
---

(This post was authored by hlky and Sayak)
When operating with latent-space diffusion models for high-resolution image and video synthesis, the VAE decoder can consume quite a bit more memory. This makes it hard for the users to run these models on consumer GPUs without going through latency sacrifices and others alike.
For example, with offloading, there is a device transfer overhead, causing delays in the overall inference latency.

[Read full article](https://huggingface.co/blog/remote_vae)
