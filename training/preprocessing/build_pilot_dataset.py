import os
import json
import random
from transform_socratic import transform_sample_to_socratic
from quality_filter import validate_socratic_sample

SYSTEM_PROMPT = "You are Maieutic, an expert Socratic tutor. You must never give the student the direct answer. Instead, ask guiding questions, provide hints, and help them arrive at the answer themselves."

def main():
    socratic_dir = "/workspace/Maieutic/training/datasets/socratic"
    os.makedirs(socratic_dir, exist_ok=True)
    
    pilot_file = os.path.join(socratic_dir, "socratic_pilot.jsonl")
    rejections_file = os.path.join(socratic_dir, "rejections.jsonl")
    stats_file = os.path.join(socratic_dir, "pilot_stats.json")
    
    # Source datasets
    sources = [
        ("/workspace/Maieutic/training/datasets/processed/lmsys_processed.jsonl", "chat"),
        ("/workspace/Maieutic/training/datasets/processed/NuminaMath_processed.jsonl", "math")
    ]
    
    raw_samples = []
    for path, domain in sources:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    item = json.loads(line)
                    item["domain"] = domain
                    raw_samples.append(item)
                    
    print(f"Total raw source samples available: {len(raw_samples)}")
    
    # Target pilot count: 300 samples
    target_count = 300
    random.seed(42)
    sample_candidates = random.sample(raw_samples, min(target_count * 2, len(raw_samples)))
    
    accepted_count = 0
    rejected_count = 0
    
    accepted_items = []
    rejected_items = []
    
    domain_counts = {}
    token_lengths = []
    leakage_count = 0
    correctness_count = 0
    
    print(f"\nBuilding Socratic Pilot Dataset (Target: {target_count} accepted samples)...")
    
    for idx, candidate in enumerate(sample_candidates):
        if accepted_count >= target_count:
            break
            
        messages = candidate.get("messages", [])
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
        asst_msg = next((m["content"] for m in messages if m["role"] == "assistant"), None)
        domain = candidate.get("domain", "chat")
        
        if not user_msg or not asst_msg:
            continue
            
        # 1. Transform
        transform_data = transform_sample_to_socratic(user_msg, asst_msg, domain=domain)
        if not transform_data or "transformed_response" not in transform_data:
            rejected_items.append({
                "id": candidate.get("id"),
                "user_prompt": user_msg,
                "rejection_reason": "transformation_failed"
            })
            rejected_count += 1
            continue
            
        transformed_text = transform_data["transformed_response"]
        
        # 2. Quality Filter
        is_accepted, eval_data = validate_socratic_sample(user_msg, transformed_text)
        
        if is_accepted:
            accepted_count += 1
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            token_lengths.append(len(transformed_text.split()))
            
            if not eval_data.get("has_answer_leakage", False):
                leakage_count += 0 # No leakage
            else:
                leakage_count += 1
                
            if eval_data.get("is_correct", True):
                correctness_count += 1
                
            pilot_entry = {
                "id": candidate.get("id"),
                "source_dataset": candidate.get("source_dataset", "unknown"),
                "domain": domain,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                    {"role": "assistant", "content": transformed_text}
                ],
                "metadata": {
                    "strategy_used": transform_data.get("strategy_used"),
                    "socratic_score": eval_data.get("socratic_score", 5)
                }
            }
            accepted_items.append(pilot_entry)
            if accepted_count % 25 == 0 or accepted_count == 1:
                print(f"  Accepted {accepted_count}/{target_count} samples...")
        else:
            rejected_count += 1
            rejected_items.append({
                "id": candidate.get("id"),
                "user_prompt": user_msg,
                "transformed_response": transformed_text,
                "rejection_reason": eval_data.get("rejection_reason", "failed_quality_filter"),
                "audit": eval_data
            })

    # Save outputs
    with open(pilot_file, "w", encoding="utf-8") as f:
        for item in accepted_items:
            f.write(json.dumps(item) + "\n")
            
    with open(rejections_file, "w", encoding="utf-8") as f:
        for item in rejected_items:
            f.write(json.dumps(item) + "\n")
            
    total_processed = accepted_count + rejected_count
    stats = {
        "source_examples_examined": total_processed,
        "transformed_accepted_examples": accepted_count,
        "rejected_examples": rejected_count,
        "rejection_rate_percent": round((rejected_count / total_processed * 100), 2) if total_processed > 0 else 0,
        "leakage_rate_percent": round((leakage_count / accepted_count * 100), 2) if accepted_count > 0 else 0,
        "correctness_rate_percent": round((correctness_count / accepted_count * 100), 2) if accepted_count > 0 else 0,
        "category_distribution": domain_counts,
        "avg_token_length": round(sum(token_lengths) / len(token_lengths), 1) if token_lengths else 0
    }
    
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        
    print("\n--- PHASE 1.5 PILOT DATASET COMPLETE ---")
    print(json.dumps(stats, indent=2))
    print(f"Saved pilot dataset to {pilot_file}")
    print(f"Saved rejections to {rejections_file}")

if __name__ == "__main__":
    main()
