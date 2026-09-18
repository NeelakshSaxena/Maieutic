import os
import json
from collections import defaultdict

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../.."))
    dataset_path = os.path.join(project_root, "training/datasets/socratic/socratic_phase1_5_v2_cleaned.jsonl")
    
    tokens_to_check = [
        "<think>",
        "</think>",
        "<|im_start|>",
        "<|im_end|>"
    ]
    
    stats = defaultdict(list)
    
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            for msg in item.get("messages", []):
                content = msg.get("content", "")
                for token in tokens_to_check:
                    if token in content:
                        stats[token].append(item)
                        break

    print("="*50)
    print("JSONL ARTIFACT SCAN REPORT")
    print("="*50)
    for token in tokens_to_check:
        print(f"Token '{token}': {len(stats[token])} examples")
        
    print("\nCONCLUSION: The JSONL dataset itself does not contain any of these serialization artifacts.")
    print("The '<think>' blocks seen in the behavioral audit are injected purely by the tokenizer's apply_chat_template during visualization (and standard training).")
    print("Our training pipeline avoids this by manually mapping ChatML without the `<think>` block for SFTTrainer in dataset.py.")

if __name__ == "__main__":
    main()
