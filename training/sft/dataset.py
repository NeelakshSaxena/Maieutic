import os
import json
from datasets import Dataset

def load_and_format_dataset(file_paths, tokenizer=None, max_samples=None):
    """
    Loads JSONL files from Phase 1 and formats them for SFT.
    If a tokenizer is provided, it applies the chat template.
    """
    formatted_data = {"text": []}
    
    # Simple ChatML template fallback if no tokenizer provided
    chatml_template = "<|im_start|>{role}\n{content}<|im_end|>\n"
    
    count = 0
    for path in file_paths:
        if not os.path.exists(path):
            print(f"Warning: Dataset file not found: {path}")
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if max_samples and count >= max_samples:
                    break
                
                sample = json.loads(line)
                messages = sample.get("messages", [])
                
                # We inject a system prompt to enforce Socratic tutoring behavior
                system_message = {
                    "role": "system", 
                    "content": "You are MentorAI, an expert Socratic tutor. You must never give the student the direct answer. Instead, ask guiding questions, provide hints, and help them arrive at the answer themselves."
                }
                
                # Prefix system message
                if not any(m.get("role") == "system" for m in messages):
                    messages.insert(0, system_message)
                
                if tokenizer and hasattr(tokenizer, "apply_chat_template"):
                    try:
                        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
                        formatted_data["text"].append(text)
                    except Exception as e:
                        # Fallback
                        text = "".join([chatml_template.format(role=m["role"], content=m["content"]) for m in messages])
                        formatted_data["text"].append(text)
                else:
                    text = "".join([chatml_template.format(role=m["role"], content=m["content"]) for m in messages])
                    formatted_data["text"].append(text)
                    
                count += 1

    return Dataset.from_dict(formatted_data)

if __name__ == "__main__":
    # Smoke test the dataset formatter
    print("Testing dataset formatting...")
    dummy_paths = ["training/datasets/processed/lmsys_processed.jsonl", "training/datasets/processed/NuminaMath_processed.jsonl"]
    ds = load_and_format_dataset(dummy_paths, max_samples=5)
    print(f"Loaded {len(ds)} samples.")
    if len(ds) > 0:
        print("Sample 0 text preview:\n")
        print(ds[0]["text"][:500] + "...\n")
        
        # Verify it has the Socratic system prompt
        assert "You are MentorAI" in ds[0]["text"], "System prompt missing!"
        print("[SUCCESS] Dataset formatting passed smoke test.")
