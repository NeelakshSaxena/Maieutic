import os
import json
import random

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    processed_dir = os.path.join(root_dir, "training", "datasets", "processed")
    eval_dir = os.path.join(root_dir, "training", "evaluation")
    os.makedirs(eval_dir, exist_ok=True)
    
    # Load all processed samples
    all_samples = []
    for filename in os.listdir(processed_dir):
        if filename.endswith(".jsonl"):
            filepath = os.path.join(processed_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    all_samples.append(json.loads(line))
                    
    # Stratify samples by domain
    # Our datasets:
    # NuminaMath (math, logic)
    # LMSYS / WildChat (chat, reasoning, programming, general)
    
    math_samples = []
    programming_samples = []
    science_reasoning_samples = []
    misconception_samples = [] # Multi-step or reasoning heavy
    
    for sample in all_samples:
        metadata = sample.get("metadata", {})
        domain = sample.get("domain", "")
        source = sample.get("source_dataset", "").lower()
        
        # We try to infer category based on source and metadata
        if "numina" in source or domain == "math":
            if metadata.get("has_reasoning"):
                misconception_samples.append(sample)
            else:
                math_samples.append(sample)
        else:
            # For LMSYS/WildChat, we don't have explicit programming/science tags, 
            # so we'll just hash them deterministically based on ID to create pools
            if hash(sample["id"]) % 3 == 0:
                programming_samples.append(sample)
            elif hash(sample["id"]) % 3 == 1:
                science_reasoning_samples.append(sample)
            else:
                misconception_samples.append(sample)
                
    # Deterministically sample target counts
    # We use a fixed seed based on sample IDs to ensure reproducible splits
    def deterministic_sample(population, k):
        # Sort by ID to ensure deterministic order
        population.sort(key=lambda x: x["id"])
        # Use a fixed random seed
        rng = random.Random(42)
        return rng.sample(population, min(k, len(population)))

    benchmark_samples = []
    benchmark_samples.extend(deterministic_sample(math_samples, 40))
    benchmark_samples.extend(deterministic_sample(programming_samples, 25))
    benchmark_samples.extend(deterministic_sample(science_reasoning_samples, 20))
    benchmark_samples.extend(deterministic_sample(misconception_samples, 15))
    
    # In case we couldn't get enough of one category, fill the rest from anything
    remaining_needed = 100 - len(benchmark_samples)
    if remaining_needed > 0:
        seen_ids = {s["id"] for s in benchmark_samples}
        leftover = [s for s in all_samples if s["id"] not in seen_ids]
        benchmark_samples.extend(deterministic_sample(leftover, remaining_needed))
        
    benchmark_samples.sort(key=lambda x: x["id"]) # Final stable sort
    
    # Save the benchmark samples
    benchmark_path = os.path.join(eval_dir, "mentorai_benchmark.jsonl")
    benchmark_ids_path = os.path.join(eval_dir, "benchmark_ids.json")
    
    benchmark_ids = []
    
    with open(benchmark_path, "w", encoding="utf-8") as f:
        for sample in benchmark_samples:
            benchmark_ids.append(sample["id"])
            f.write(json.dumps(sample) + "\n")
            
    with open(benchmark_ids_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_ids, f, indent=2)
        
    print(f"Successfully extracted {len(benchmark_samples)} evaluation samples.")
    print(f"Saved benchmark to: {benchmark_path}")
    print(f"Saved benchmark IDs to: {benchmark_ids_path}")

if __name__ == "__main__":
    main()
