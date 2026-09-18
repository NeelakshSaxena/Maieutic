# Hardware Requirements

MentorAI runs a multi-container Docker stack alongside a local Large Language Model (LLM) via Ollama. Because it hosts an 8-billion parameter model (`Qwen/Qwen3-8B`) locally, the hardware requirements are primarily dictated by the LLM inference engine.

## Minimum Specifications (4-bit Quantization)
These specs are sufficient to run the web application, backend API, and a highly compressed (4-bit/Q4) version of the `Qwen3-8B` model with a restricted context window.

- **OS:** Linux, macOS (M-series), or Windows 10/11 (with WSL2)
- **CPU:** 4-core modern processor (Intel Core i5 8th Gen / AMD Ryzen 5 or equivalent)
- **RAM:** 16 GB System RAM
- **GPU / VRAM:** 8 GB VRAM (e.g., NVIDIA RTX 3060 / 4060) or Apple Silicon Unified Memory
- **Storage:** 20 GB available space (SSD recommended) for Docker images, database volumes, and model weights.

*Note: Without a dedicated GPU, Ollama will fall back to CPU inference, which will be extremely slow (often 1-3 tokens per second) and is not recommended for a real-time tutoring experience.*

## Recommended Specifications
These specs provide a smooth, low-latency tutoring experience and allow the model to use a larger context window for complex programming or math problems.

- **OS:** Linux (Ubuntu 22.04+) or Windows 11 with WSL2
- **CPU:** 8-core modern processor (Intel Core i7/i9 12th Gen+ / AMD Ryzen 7/9)
- **RAM:** 32 GB System RAM
- **GPU / VRAM:** 12 GB - 16 GB VRAM (e.g., NVIDIA RTX 3080 / 4070 / 4080) or 32GB+ Apple Silicon Unified Memory
- **Storage:** 50 GB available space (NVMe SSD strongly recommended)

## Developer / Training Specifications
If you intend to participate in Phase 9 (Model Retraining/Fine-tuning) and run QLoRA scripts locally, the requirements are substantially higher.

- **GPU / VRAM:** 24 GB VRAM (NVIDIA RTX 3090 / 4090) is **strictly required** for training the 8B model with a 4096 sequence length.
- **RAM:** 64 GB System RAM
- **Storage:** 100 GB+ NVMe SSD (for checkpoints and evaluation datasets)

## Component Breakdown

To help you scale resources, here is the approximate memory footprint of the stack at idle:

| Component | Approximate RAM / VRAM Usage |
| :--- | :--- |
| **Next.js Frontend** | ~150 MB RAM |
| **FastAPI Backend** | ~200 MB RAM |
| **PostgreSQL** | ~100 MB RAM |
| **Qdrant (Vector DB)** | ~300 MB RAM |
| **Redis** | ~50 MB RAM |
| **Ollama (Qwen3-8B Q4)** | ~6.5 GB VRAM |
| **Ollama (Qwen3-8B FP16)** | ~16.0 GB VRAM |
