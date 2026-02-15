---
title: "Tiny Agents in Python: a MCP-powered agent in ~70 lines of code"
date: "2026-02-14T22:29:07.795575"
source: "HuggingFace"
author: "Unknown"
link: "https://huggingface.co/blog/python-tiny-agents"
published: "Fri, 23 May 2025 00:00:00 GMT"
---

NEW: tiny-agents now supports AGENTS.md standard. 🥳
Inspired by Tiny Agents in JS, we ported the idea to Python 🐍 and extended the huggingface_hub client SDK to act as a MCP Client so it can pull tools from MCP servers and pass them to the LLM during inference.
MCP (Model Context Protocol) is an open protocol that standardizes how Large Language Models (LLMs) interact with external tools and APIs. Essentially, it removed the need to write custom integrations for each tool, making it simpler to p...

[Read full article](https://huggingface.co/blog/python-tiny-agents)
