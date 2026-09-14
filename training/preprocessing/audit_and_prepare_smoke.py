import os
import json
import random
import numpy as np
from collections import defaultdict
from transformers import AutoTokenizer

def normalize_text(text):
    return "".join(c.lower() for c in text if c.isalnum())

def get_ngrams(text, n=10):
    tokens = text.split()
    return set(" ".join(tokens[i:i+n]) for i in range(max(1, len(tokens) - n + 1)))

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../.."))
    
    benchmark_path = os.path.join(project_root, "training/evaluation/mentorai_benchmark.jsonl")
    dataset_path = os.path.join(project_root, "training/datasets/socratic/socratic_pilot_v1_5.jsonl")
    cleaned_dataset_path = os.path.join(project_root, "training/datasets/socratic/socratic_pilot_v1_5_cleaned.jsonl")
    smoke_dataset_path = os.path.join(project_root, "training/datasets/socratic/socratic_smoke_test.jsonl")

    # Load tokenizer for token length calculation
    print("Loading Qwen3 tokenizer for length analysis...")
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
    
    # 1. Load benchmark and build leakage index
    benchmark_ids = set()
    benchmark_texts = []
    
    if os.path.exists(benchmark_path):
        with open(benchmark_path, "r", encoding="utf-8") as f:
            for line in f:
                item = json.loads(line)
                benchmark_ids.add(item["id"])
                
                # Create a concatenated text representation for content overlap
                text = " ".join([m.get("content", "") for m in item.get("messages", [])])
                benchmark_texts.append({
                    "id": item["id"],
                    "norm": normalize_text(text),
                    "ngrams": get_ngrams(normalize_text(text), n=20)
                })
    else:
        print(f"WARNING: Benchmark not found at {benchmark_path}")

    # 2. Process dataset & Audit
    original_count = 0
    overlap_count = 0
    malformed_count = 0
    duplicate_count = 0
    
    seen_ids = set()
    cleaned_dataset = []
    
    stats = {
        "socratic": 0,
        "reasoning": 0,
        "single_turn": 0,
        "multi_turn": 0,
        "token_lengths": []
    }
    
    print("Auditing Phase 1.5 Dataset...")
    
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            original_count += 1
            try:
                item = json.loads(line)
            except:
                malformed_count += 1
                continue
                
            messages = item.get("messages", [])
            if not messages:
                malformed_count += 1
                continue
                
            item_id = item.get("id")
            
            # Check for duplicates within dataset
            if item_id in seen_ids:
                duplicate_count += 1
                continue
            seen_ids.add(item_id)
            
            # Check leakage via ID
            if item_id in benchmark_ids:
                overlap_count += 1
                continue
                
            # Check leakage via semantic/N-gram overlap
            text = " ".join([m.get("content", "") for m in messages])
            norm_text = normalize_text(text)
            item_ngrams = get_ngrams(norm_text, n=20)
            
            has_leakage = False
            for b_item in benchmark_texts:
                if len(item_ngrams.intersection(b_item["ngrams"])) > 10: # arbitrary threshold for 20-gram overlap
                    has_leakage = True
                    break
            
            if has_leakage:
                overlap_count += 1
                continue
            
            # Add to cleaned dataset
            cleaned_dataset.append(item)
            
            # Update stats
            metadata = item.get("metadata", {})
            if item.get("type") == "reasoning_replay" or metadata.get("strategy_used") == "reasoning_replay":
                stats["reasoning"] += 1
            else:
                stats["socratic"] += 1
                
            if metadata.get("is_multiturn") or len([m for m in messages if m.get("role") in ["user", "assistant"]]) > 2:
                stats["multi_turn"] += 1
            else:
                stats["single_turn"] += 1
                
            # Compute tokens
            chat_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
            if chat_text:
                tokens = tokenizer.encode(chat_text)
                stats["token_lengths"].append(len(tokens))
            else:
                stats["token_lengths"].append(0)

    # Calculate token length percentiles
    token_lengths = np.array(stats["token_lengths"]) if stats["token_lengths"] else np.array([0])
    avg_tokens = np.mean(token_lengths)
    p50_tokens = np.percentile(token_lengths, 50)
    p95_tokens = np.percentile(token_lengths, 95)
    max_tokens = np.max(token_lengths)

    print("\n" + "="*50)
    print("DATASET SANITY REPORT")
    print("="*50)
    print(f"Total examples (original): {original_count}")
    print(f"Malformed examples:        {malformed_count}")
    print(f"Duplicate examples:        {duplicate_count}")
    print(f"Benchmark overlap:         {overlap_count}")
    print(f"Total examples (cleaned):  {len(cleaned_dataset)}")
    print("-"*50)
    
    total_valid = len(cleaned_dataset)
    if total_valid > 0:
        print(f"Socratic %:                {(stats['socratic']/total_valid)*100:.1f}%")
        print(f"Reasoning %:               {(stats['reasoning']/total_valid)*100:.1f}%")
        print(f"Single-turn %:             {(stats['single_turn']/total_valid)*100:.1f}%")
        print(f"Multi-turn %:              {(stats['multi_turn']/total_valid)*100:.1f}%")
    print("-"*50)
    print(f"Average tokens:            {avg_tokens:.1f}")
    print(f"p50 tokens:                {p50_tokens:.1f}")
    print(f"p95 tokens:                {p95_tokens:.1f}")
    print(f"Max tokens:                {max_tokens}")
    print("="*50 + "\n")

    # Save cleaned dataset
    print(f"Saving cleaned dataset to {cleaned_dataset_path}...")
    with open(cleaned_dataset_path, "w", encoding="utf-8") as f:
        for item in cleaned_dataset:
            f.write(json.dumps(item) + "\n")

    # 3. Deterministic Smoke Test Sampling (seed=42, ~200 samples, preserving 75/25 ratio)
    print("Creating deterministic 200-example smoke dataset (seed=42)...")
    random.seed(42)
    
    socratic_pool = [x for x in cleaned_dataset if x.get("type") != "reasoning_replay" and x.get("metadata", {}).get("strategy_used") != "reasoning_replay"]
    reasoning_pool = [x for x in cleaned_dataset if x.get("type") == "reasoning_replay" or x.get("metadata", {}).get("strategy_used") == "reasoning_replay"]
    
    # Sort pools by ID for determinism before sampling
    socratic_pool.sort(key=lambda x: x["id"])
    reasoning_pool.sort(key=lambda x: x["id"])

    # If reasoning pool is 0 (as currently happens because lmsys is missing), fallback gracefully
    if len(reasoning_pool) == 0:
        print("Warning: Reasoning pool is empty! Smoke test will be 100% Socratic.")
        smoke_sample = random.sample(socratic_pool, min(200, len(socratic_pool)))
    else:
        target_socratic = int(200 * 0.75)
        target_reasoning = 200 - target_socratic
        
        sampled_socratic = random.sample(socratic_pool, min(target_socratic, len(socratic_pool)))
        sampled_reasoning = random.sample(reasoning_pool, min(target_reasoning, len(reasoning_pool)))
        
        smoke_sample = sampled_socratic + sampled_reasoning
        
    # Shuffle smoke sample to mix socratic and reasoning
    random.shuffle(smoke_sample)

    with open(smoke_dataset_path, "w", encoding="utf-8") as f:
        for item in smoke_sample:
            f.write(json.dumps(item) + "\n")
            
    print(f"Saved {len(smoke_sample)} examples to {smoke_dataset_path}")
    print("\nFirst example serialized:\n")
    print(tokenizer.apply_chat_template(smoke_sample[0].get("messages", []), tokenize=False, add_generation_prompt=False))

    print("Audit and preparation complete!")

if __name__ == "__main__":
    main()
