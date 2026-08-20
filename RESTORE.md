# How to Restore MentorAI Project

This document outlines the concise commands and procedures needed to restore the MentorAI project from scratch on a new RunPod GPU instance.

## 1. Environment Setup

Clone the project repository:
```bash
git clone https://github.com/NeelakshSaxena/Maieutic.git
cd Maieutic
```

Install training and evaluation dependencies:
```bash
pip install -r training/requirements.txt
```

Authenticate with Hugging Face:
```bash
export HF_TOKEN="your_huggingface_write_token"
huggingface-cli login --token $HF_TOKEN
```

## 2. Download the Experiment #1 Adapter

To download the QLoRA adapter and associated configurations from the private Hugging Face repository (`NeelakshSaxena/mentorai`), use `huggingface-cli`:
```bash
# Download the adapter files directly to outputs directory
huggingface-cli download NeelakshSaxena/mentorai \
  --include "adapter_config.json" "adapter_model.safetensors" "chat_template.jinja" "tokenizer.json" "tokenizer_config.json" \
  --local-dir ./outputs/qwen-8b-socratic-v1
```

## 3. Load Adapter & Run Inference

Use the following Python snippet to verify loading and run a basic Socratic tutoring inference test:
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

base_model_name = "Qwen/Qwen3-8B"
adapter_dir = "./outputs/qwen-8b-socratic-v1"

# Load base model & tokenizer
tokenizer = AutoTokenizer.from_pretrained(adapter_dir)
model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Load PEFT adapter
model = PeftModel.from_pretrained(model, adapter_dir)
model.eval()

# Run a test Socratic prompt
messages = [
    {"role": "system", "content": "You are MentorAI, an expert Socratic tutor. You must never give the student the direct answer. Instead, ask guiding questions, provide hints, and help them arrive at the answer themselves."},
    {"role": "user", "content": "What is the formula for the area of a circle?"}
]

prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=150)
    print(tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True))
```

## 4. Resume Evaluation

To download the evaluation logs, raw responses, and rescore evaluations:
```bash
# Download evaluation directory
huggingface-cli download NeelakshSaxena/mentorai \
  --include "evaluation/*" \
  --local-dir ./training/
```
Once downloaded, run the rescoring script:
```bash
python training/evaluation/rescore_evaluations.py
```

## 5. Locate Phase 1.5 Pilot Artifacts

The Phase 1.5 pilot data artifacts (including the pilot dataset, rejections list, and generation statistics) can be retrieved as follows:
```bash
huggingface-cli download NeelakshSaxena/mentorai \
  --include "pilot/*" \
  --local-dir ./training/datasets/socratic/
```
These will be available at:
- Dataset: `./training/datasets/socratic/pilot/socratic_pilot.jsonl`
- Rejections: `./training/datasets/socratic/pilot/rejections.jsonl`
- Stats: `./training/datasets/socratic/pilot/pilot_stats.json`
