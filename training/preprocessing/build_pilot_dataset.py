import os
import json
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from transform_socratic import transform_sample_to_socratic
from quality_filter import validate_socratic_sample

SYSTEM_PROMPT = "You are Maieutic, an expert Socratic tutor. You must never give the student the direct answer. Instead, ask guiding questions, provide hints, and help them arrive at the answer themselves."

def process_socratic(candidate):
    messages = candidate.get("messages", [])
    user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
    asst_msg = next((m["content"] for m in messages if m["role"] == "assistant"), None)
    domain = candidate.get("domain", "chat")
    
    if not user_msg or not asst_msg:
        return None, {"rejection_reason": "missing_messages"}
        
    transform_data = transform_sample_to_socratic(user_msg, asst_msg, domain=domain)
    if not transform_data or "transformed_response" not in transform_data:
        return None, {"rejection_reason": "transformation_failed"}
        
    transformed_text = transform_data["transformed_response"]
    is_multiturn = transform_data.get("is_multiturn", False)
    is_accepted, eval_data = validate_socratic_sample(user_msg, transformed_text)
    
    if is_accepted:
        pilot_entry = {
            "id": candidate.get("id"),
            "source_dataset": candidate.get("source_dataset", "unknown"),
            "domain": domain,
            "type": "socratic",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": transformed_text}
            ],
            "metadata": {
                "strategy_used": transform_data.get("strategy_used"),
                "socratic_score": eval_data.get("socratic_score", 5),
                "is_multiturn": is_multiturn
            }
        }
        return pilot_entry, eval_data
    else:
        return None, eval_data

def process_replay(candidate):
    messages = candidate.get("messages", [])
    user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
    asst_msg = next((m["content"] for m in messages if m["role"] == "assistant"), None)
    domain = candidate.get("domain", "math")
    
    if not user_msg or not asst_msg:
        return None
        
    # Hack for Qwen3 template: ensure it has <think> tags so it doesn't get empty ones injected
    if "<think>" not in asst_msg:
        asst_msg = f"<think>\nSolving the problem logically.\n</think>\n{asst_msg}"
        
    pilot_entry = {
        "id": candidate.get("id"),
        "source_dataset": candidate.get("source_dataset", "unknown"),
        "domain": domain,
        "type": "reasoning_replay",
        "messages": [
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": asst_msg}
        ],
        "metadata": {
            "strategy_used": "reasoning_replay"
        }
    }
    return pilot_entry

def main():
    socratic_dir = "/workspace/Maieutic/training/datasets/socratic"
    os.makedirs(socratic_dir, exist_ok=True)
    
    pilot_file = os.path.join(socratic_dir, "socratic_pilot.jsonl")
    rejections_file = os.path.join(socratic_dir, "rejections.jsonl")
    stats_file = os.path.join(socratic_dir, "pilot_stats.json")
    
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
    
    target_socratic = 700
    target_replay = 300
    
    random.seed(42)
    random.shuffle(raw_samples)
    
    accepted_items = []
    rejected_items = []
    
    domain_counts = {}
    type_counts = {"socratic": 0, "reasoning_replay": 0}
    token_lengths = []
    leakage_count = 0
    correctness_count = 0
    multiturn_count = 0
    
    # Process Replay (fast)
    print(f"\nBuilding Reasoning Replay (Target: {target_replay})...")
    replay_candidates = [s for s in raw_samples if s["domain"] == "math"]
    for candidate in replay_candidates:
        if type_counts["reasoning_replay"] >= target_replay:
            break
        entry = process_replay(candidate)
        if entry:
            accepted_items.append(entry)
            type_counts["reasoning_replay"] += 1
            domain_counts[entry["domain"]] = domain_counts.get(entry["domain"], 0) + 1
            
    print(f"Built {type_counts['reasoning_replay']} Reasoning Replay samples.")
    
    # Process Socratic (slow)
    print(f"\nBuilding Socratic (Target: {target_socratic})...")
    # Take a chunk to process concurrently
    socratic_candidates = [s for s in raw_samples if s not in replay_candidates[:target_replay]]
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_cand = {executor.submit(process_socratic, cand): cand for cand in socratic_candidates[:target_socratic * 3]}
        
        for future in as_completed(future_to_cand):
            if type_counts["socratic"] >= target_socratic:
                break
                
            try:
                entry, eval_data = future.result()
                if entry:
                    accepted_items.append(entry)
                    type_counts["socratic"] += 1
                    domain_counts[entry["domain"]] = domain_counts.get(entry["domain"], 0) + 1
                    token_lengths.append(len(entry["messages"][-1]["content"].split()))
                    if eval_data.get("has_answer_leakage", False):
                        leakage_count += 1
                    if eval_data.get("is_correct", True):
                        correctness_count += 1
                    if entry["metadata"].get("is_multiturn", False):
                        multiturn_count += 1
                        
                    if type_counts["socratic"] % 50 == 0:
                        print(f"  Accepted {type_counts['socratic']}/{target_socratic} Socratic samples...")
                else:
                    cand = future_to_cand[future]
                    rejected_items.append({
                        "id": cand.get("id"),
                        "rejection_reason": eval_data.get("rejection_reason", "unknown")
                    })
            except Exception as e:
                print(f"Error processing sample: {e}")
                
    with open(pilot_file, "w", encoding="utf-8") as f:
        for item in accepted_items:
            f.write(json.dumps(item) + "\n")
            
    with open(rejections_file, "w", encoding="utf-8") as f:
        for item in rejected_items:
            f.write(json.dumps(item) + "\n")
            
    total_processed = type_counts["socratic"] + len(rejected_items)
    stats = {
        "total_pilot_samples": len(accepted_items),
        "type_distribution": type_counts,
        "category_distribution": domain_counts,
        "socratic_stats": {
            "source_examples_examined": total_processed,
            "transformed_accepted_examples": type_counts["socratic"],
            "rejected_examples": len(rejected_items),
            "rejection_rate_percent": round((len(rejected_items) / total_processed * 100), 2) if total_processed > 0 else 0,
            "leakage_rate_percent": round((leakage_count / type_counts["socratic"] * 100), 2) if type_counts["socratic"] > 0 else 0,
            "correctness_rate_percent": round((correctness_count / type_counts["socratic"] * 100), 2) if type_counts["socratic"] > 0 else 0,
            "multiturn_percent": round((multiturn_count / type_counts["socratic"] * 100), 2) if type_counts["socratic"] > 0 else 0,
            "avg_token_length": round(sum(token_lengths) / len(token_lengths), 1) if token_lengths else 0
        }
    }
    
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        
    print("\n--- PHASE 1.5 PILOT DATASET COMPLETE ---")
    print(json.dumps(stats, indent=2))
    print(f"Saved pilot dataset to {pilot_file}")

if __name__ == "__main__":
    main()
