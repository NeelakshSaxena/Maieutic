import os
import json
from datasets import Dataset, load_dataset
from dotenv import load_dotenv

load_dotenv()

def load_and_format_dataset(file_paths=None, tokenizer=None, max_samples=None):
    """
    Loads dataset from Hugging Face Hub or local JSONL files from Phase 1 and formats them for SFT.
    Supports DATASET_SOURCE, HF_DATASET_REPO, and DATASET_REVISION environment variables.
    """
    formatted_data = {"text": []}
    chatml_template = "<|im_start|>{role}\n{content}<|im_end|>\n"
    
    dataset_source = os.getenv("DATASET_SOURCE", "auto")
    hf_repo = os.getenv("HF_DATASET_REPO")
    revision = os.getenv("DATASET_REVISION", "main")
    
    samples = []
    
    # Try loading from HF Hub if requested or configured
    if dataset_source == "hub" or (dataset_source == "auto" and hf_repo):
        print(f"Loading dataset from Hugging Face Hub: {hf_repo} (revision: {revision})...")
        try:
            hf_ds = load_dataset(hf_repo, revision=revision, split="train")
            for item in hf_ds:
                if max_samples and len(samples) >= max_samples:
                    break
                if "messages" in item:
                    samples.append(item)
        except Exception as e:
            print(f"Warning: Failed to load dataset from HF Hub ({e}). Falling back to local files.")
            
    # Fallback to local files if no HF samples were loaded
    if not samples and file_paths:
        count = 0
        for path in file_paths:
            if not os.path.exists(path):
                print(f"Warning: Dataset file not found: {path}")
                continue
                
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if max_samples and count >= max_samples:
                        break
                    samples.append(json.loads(line))
                    count += 1

    if not samples:
        print("Warning: No dataset samples loaded.")
        return Dataset.from_dict({"text": []})

    # Format samples
    for sample in samples:
        messages = sample.get("messages", [])
        
        # Inject MentorAI Socratic tutor system message
        system_message = {
            "role": "system", 
            "content": "You are MentorAI, an expert Socratic tutor. You must never give the student the direct answer. Instead, ask guiding questions, provide hints, and help them arrive at the answer themselves."
        }
        
        if not any(m.get("role") == "system" for m in messages):
            messages.insert(0, system_message)
            
        if tokenizer and hasattr(tokenizer, "apply_chat_template"):
            try:
                text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
                formatted_data["text"].append(text)
            except Exception:
                text = "".join([chatml_template.format(role=m["role"], content=m["content"]) for m in messages])
                formatted_data["text"].append(text)
        else:
            text = "".join([chatml_template.format(role=m["role"], content=m["content"]) for m in messages])
            formatted_data["text"].append(text)

    return Dataset.from_dict(formatted_data)

if __name__ == "__main__":
    print("Testing dataset formatting...")
    dummy_paths = ["training/datasets/processed/lmsys_processed.jsonl", "training/datasets/processed/NuminaMath_processed.jsonl"]
    ds = load_and_format_dataset(dummy_paths, max_samples=5)
    print(f"Loaded {len(ds)} samples.")
    if len(ds) > 0:
        print("Sample 0 text preview:\n")
        print(ds[0]["text"][:500] + "...\n")
        assert "You are MentorAI" in ds[0]["text"], "System prompt missing!"
        print("[SUCCESS] Dataset formatting passed smoke test.")
    else:
        print("[INFO] No dataset files available on local disk or HF Hub.")
