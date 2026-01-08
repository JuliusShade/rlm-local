# Local LLM Setup Guide

## Qwen2.5-Coder 14B (RTX 5080) --- Local Endpoint + RAG-Ready

This guide walks you **start → finish** through setting up
**Qwen2.5-Coder 14B** as a **local AI coding model** running on your PC,
exposed as a **local HTTP endpoint** you can call from tools, scripts,
or IDEs.

Target system: - GPU: RTX 5080 (16 GB VRAM) - RAM: 32 GB DDR5 - OS:
Windows / Linux - Use case: Local coding assistant + RAG

------------------------------------------------------------------------

## High-Level Architecture

    Your IDE / App / Script
            ↓  HTTP (OpenAI-style)
    Local Endpoint (localhost)
            ↓
    Ollama Runtime
            ↓
    Qwen2.5-Coder 14B (GPU)

You are **not training** anything.\
You are **running inference only**.

------------------------------------------------------------------------

## Step 1 --- Install Ollama (Local Model Runtime)

Ollama is a local LLM runtime that: - Uses your GPU automatically -
Exposes an HTTP API - Requires zero CUDA setup

### Download

https://ollama.com

### Verify install

``` bash
ollama --version
```

If this prints a version number, you're good.

------------------------------------------------------------------------

## Step 2 --- Download the Model (One-Time)

Pull Qwen2.5-Coder 14B:

``` bash
ollama pull qwen2.5-coder:14b
```

Optional (for RAG embeddings later):

``` bash
ollama pull nomic-embed-text
```

This step may take several minutes depending on internet speed.

------------------------------------------------------------------------

## Step 3 --- Start the Local LLM Server

Ollama runs automatically in the background.

To confirm the model runs:

``` bash
ollama run qwen2.5-coder:14b
```

If you see a prompt and get a response, GPU inference is working.

------------------------------------------------------------------------

## Step 4 --- Confirm the Local HTTP Endpoint

By default, Ollama exposes an API at:

    http://localhost:11434

OpenAI-compatible endpoints: - `/v1/chat/completions` - `/v1/embeddings`

### Quick test (curl)

``` bash
curl http://localhost:11434/v1/models
```

You should see `qwen2.5-coder:14b` listed.

------------------------------------------------------------------------

## Step 5 --- Calling the Model from Code (Example)

### JavaScript (Node.js)

``` js
import fetch from "node-fetch";

const response = await fetch("http://localhost:11434/v1/chat/completions", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer local"
  },
  body: JSON.stringify({
    model: "qwen2.5-coder:14b",
    messages: [
      { role: "system", content: "You are a senior software engineer." },
      { role: "user", content: "Explain this function and suggest improvements." }
    ]
  })
});

const data = await response.json();
console.log(data.choices[0].message.content);
```

### Python

``` python
import requests

resp = requests.post(
    "http://localhost:11434/v1/chat/completions",
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer local"
    },
    json={
        "model": "qwen2.5-coder:14b",
        "messages": [
            {"role": "system", "content": "You are a senior software engineer."},
            {"role": "user", "content": "Refactor this code for readability."}
        ]
    }
)

print(resp.json()["choices"][0]["message"]["content"])
```

------------------------------------------------------------------------

## Step 6 --- Preparing for RAG (Highly Recommended)

RAG = Retrieval-Augmented Generation\
This allows: - Large effective context - Faster responses - Better
accuracy - No VRAM blowups

### What you'll need

-   Embeddings model (`nomic-embed-text`)
-   Vector store (local)
-   Retriever logic

Most IDE tools (e.g., Continue) handle this automatically.

------------------------------------------------------------------------

## Step 7 --- (Optional) IDE Integration via Continue

If using **VS Code**:

1.  Install **Continue** extension
2.  Configure it to use:
    -   Provider: `ollama`
    -   Model: `qwen2.5-coder:14b`
    -   Embeddings: `nomic-embed-text`
3.  Index your repository

This gives: - Codebase awareness - File-targeted reasoning - Patch-style
edits

------------------------------------------------------------------------

## Recommended Runtime Settings (RTX 5080)

  Setting           Value
  ----------------- -------------------
  Model             Qwen2.5-Coder 14B
  Quantization      Default (Q4)
  Context Window    8k--12k
  Offloading        None
  RAG Chunk Size    300--500 tokens
  Top-K Retrieval   5--10

------------------------------------------------------------------------

## Common Pitfalls (Avoid These)

❌ Using massive context windows\
❌ Offloading model layers to CPU\
❌ Running 30B+ models on 16 GB VRAM\
❌ Sending entire repos instead of RAG

------------------------------------------------------------------------

## Summary

You now have: - A **local LLM endpoint** - GPU-backed inference -
OpenAI-compatible API - RAG-ready architecture - Zero token costs

This setup gives you a **Claude-like local coding assistant** that you
fully control.

------------------------------------------------------------------------

Happy hacking.
