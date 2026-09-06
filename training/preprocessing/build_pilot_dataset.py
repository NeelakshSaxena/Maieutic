import os
import json
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from transform_socratic import transform_sample_to_socratic
from quality_filter import validate_socratic_sample

SYSTEM_PROMPT = "You are Maieutic, an expert Socratic tutor. You must never give the student the direct answer. Instead, ask guiding questions, provide hints, and help them arrive at the answer themselves."

TRANSFORM_CONCURRENCY = 4
TRANSFORM_BATCH_SIZE = 8

def process_replay(candidate):
    messages = candidate.get("messages", [])
    user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
    asst_msg = next((m["content"] for m in messages if m["role"] == "assistant"), None)
    domain = candidate.get("domain", "math")
    
    if not user_msg or not asst_msg:
        return None
        
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

def count_tokens(text):
    return len(text.split())

def do_transform(candidate):
    cand_id = candidate.get("id", "unknown")
    print(f"DEBUG: Starting transform for {cand_id}", flush=True)
    messages = candidate.get("messages", [])
    user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
    asst_msg = next((m["content"] for m in messages if m["role"] == "assistant"), None)
    domain = candidate.get("domain", "chat")
    
    if not user_msg or not asst_msg:
        return candidate, {"error": "missing_messages"}
        
    transform_data = transform_sample_to_socratic(user_msg, asst_msg, domain=domain)
    print(f"DEBUG: Finished transform for {cand_id}", flush=True)
    return candidate, transform_data

def do_judge(candidate, transform_data):
    cand_id = candidate.get("id", "unknown")
    print(f"DEBUG: Starting judge for {cand_id}", flush=True)
    messages = candidate.get("messages", [])
    user_msg = next((m["content"] for m in messages if m["role"] == "user"), None)
    transformed_messages = transform_data["messages"]
    transformed_text = json.dumps(transformed_messages)
    
    is_accepted, eval_data = validate_socratic_sample(user_msg, transformed_text)
    print(f"DEBUG: Finished judge for {cand_id}", flush=True)
    return candidate, transform_data, is_accepted, eval_data

def main():
    socratic_dir = "/workspace/Maieutic/training/datasets/socratic"
    os.makedirs(socratic_dir, exist_ok=True)
    
    pilot_file = os.path.join(socratic_dir, "socratic_pilot.jsonl")
    rejections_file = os.path.join(socratic_dir, "rejections.jsonl")
    stats_file = os.path.join(socratic_dir, "pilot_stats.json")
    live_log = os.path.join(socratic_dir, "live_generation.log")
    
    # Load already processed IDs to avoid duplicate work
    processed_ids = set()
    if os.path.exists(pilot_file):
        with open(pilot_file, "r", encoding="utf-8") as f:
            for line in f:
                processed_ids.add(json.loads(line).get("id"))
    if os.path.exists(rejections_file):
        with open(rejections_file, "r", encoding="utf-8") as f:
            for line in f:
                processed_ids.add(json.loads(line).get("id"))
                
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
                    if item.get("id") not in processed_ids:
                        raw_samples.append(item)
                    
    print(f"Loaded existing processing state. Remaining unprocessed samples: {len(raw_samples)}")
    
    target_socratic = 50
    target_replay = 0
    
    random.seed(42)
    random.shuffle(raw_samples)
    
    # Try to load existing stats to keep numbers accurate if resuming
    stats = {"total_pilot_samples": 0, "type_distribution": {"socratic": 0, "reasoning_replay": 0}, "category_distribution": {}, "socratic_stats": {"source_examples_examined": 0, "transformed_accepted_examples": 0, "rejected_examples": 0}}
    token_lengths = []
    leakage_count = 0
    correctness_count = 0
    multiturn_count = 0
    
    if os.path.exists(stats_file):
        try:
            with open(stats_file, "r", encoding="utf-8") as f:
                old_stats = json.load(f)
                stats["type_distribution"]["socratic"] = old_stats.get("type_distribution", {}).get("socratic", 0)
                stats["socratic_stats"]["rejected_examples"] = old_stats.get("socratic_stats", {}).get("rejected_examples", 0)
                stats["socratic_stats"]["source_examples_examined"] = old_stats.get("socratic_stats", {}).get("source_examples_examined", 0)
        except:
            pass

    print(f"\nBuilding Reasoning Replay (Target: {target_replay})...")
    
    with open(live_log, "a", encoding="utf-8") as lf:
        lf.write(f"--- RESUMING PILOT GENERATION LOG (Current Accepted: {stats['type_distribution']['socratic']}) ---\n")

    print(f"\nBuilding Socratic (Target: {target_socratic})...", flush=True)
    socratic_candidates = [s for s in raw_samples if s["domain"] == "chat"]
    
    cand_index = 0
    batch_size = TRANSFORM_BATCH_SIZE
    
    while stats["type_distribution"]["socratic"] < target_socratic and cand_index < len(socratic_candidates):
        batch = socratic_candidates[cand_index:cand_index+batch_size]
        cand_index += batch_size
        
        # PHASE 1: Parallel Transform
        transform_results = []
        with ThreadPoolExecutor(max_workers=TRANSFORM_CONCURRENCY) as executor:
            future_to_cand = {executor.submit(do_transform, cand): cand for cand in batch}
            for future in as_completed(future_to_cand):
                cand, t_data = future.result()
                stats["socratic_stats"]["source_examples_examined"] += 1
                if "error" in t_data:
                    reason = t_data["error"]
                    with open(rejections_file, "a", encoding="utf-8") as rf:
                        rf.write(json.dumps({"id": cand.get("id"), "rejection_reason": reason, "raw": t_data.get("raw")}) + "\n")
                    stats["socratic_stats"]["rejected_examples"] += 1
                    msg = f"  Rejected sample ({reason}) Total rejections: {stats['socratic_stats']['rejected_examples']}"
                    print(msg, flush=True)
                    with open(live_log, "a", encoding="utf-8") as lf:
                        lf.write(msg + "\n")
                else:
                    transform_results.append((cand, t_data))
                    
        # PHASE 2: Parallel Judge
        if not transform_results:
            continue
            
        with ThreadPoolExecutor(max_workers=TRANSFORM_CONCURRENCY) as executor:
            future_to_res = {executor.submit(do_judge, cand, t_data): (cand, t_data) for cand, t_data in transform_results}
            for future in as_completed(future_to_res):
                if stats["type_distribution"]["socratic"] >= target_socratic:
                    continue # Stop saving if target reached
                    
                cand, t_data, is_accepted, eval_data = future.result()
                if is_accepted:
                    domain = cand.get("domain", "chat")
                    final_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + t_data["messages"]
                    pilot_entry = {
                        "id": cand.get("id"),
                        "source_dataset": cand.get("source_dataset", "unknown"),
                        "domain": domain,
                        "type": "socratic",
                        "messages": final_messages,
                        "metadata": {
                            "strategy_used": t_data.get("strategy_used"),
                            "socratic_score": eval_data.get("socratic_score", 5),
                            "is_multiturn": t_data.get("is_multiturn", False)
                        }
                    }
                    with open(pilot_file, "a", encoding="utf-8") as pf:
                        pf.write(json.dumps(pilot_entry) + "\n")
                    
                    stats["type_distribution"]["socratic"] += 1
                    stats["socratic_stats"]["transformed_accepted_examples"] += 1
                    
                    asst_text = " ".join([m["content"] for m in pilot_entry["messages"] if m["role"] == "assistant"])
                    token_lengths.append(count_tokens(asst_text))
                    
                    if eval_data.get("has_answer_leakage", False):
                        leakage_count += 1
                    if eval_data.get("is_correct", True):
                        correctness_count += 1
                    if pilot_entry["metadata"].get("is_multiturn", False):
                        multiturn_count += 1
                        
                    msg = f"  Accepted {stats['type_distribution']['socratic']}/{target_socratic} Socratic samples..."
                    print(msg, flush=True)
                    with open(live_log, "a", encoding="utf-8") as lf:
                        lf.write(msg + "\n")
                else:
                    reason = eval_data.get("rejection_reason", "unknown")
                    with open(rejections_file, "a", encoding="utf-8") as rf:
                        rf.write(json.dumps({"id": cand.get("id"), "rejection_reason": reason, "raw": eval_data.get("raw")}) + "\n")
                    stats["socratic_stats"]["rejected_examples"] += 1
                    msg = f"  Rejected sample ({reason}) Total rejections: {stats['socratic_stats']['rejected_examples']}"
                    print(msg, flush=True)
                    with open(live_log, "a", encoding="utf-8") as lf:
                        lf.write(msg + "\n")
                        
    # Save final stats
    stats["total_pilot_samples"] = stats["type_distribution"]["socratic"] + stats["type_distribution"]["reasoning_replay"]
    total_accepted = stats["socratic_stats"]["transformed_accepted_examples"]
    if total_accepted > 0:
        stats["socratic_stats"]["rejection_rate_percent"] = round((stats["socratic_stats"]["rejected_examples"] / stats["socratic_stats"]["source_examples_examined"] * 100), 2) if stats["socratic_stats"]["source_examples_examined"] > 0 else 0
        stats["socratic_stats"]["leakage_rate_percent"] = round((leakage_count / total_accepted * 100), 2)
        stats["socratic_stats"]["correctness_rate_percent"] = round((correctness_count / total_accepted * 100), 2)
        stats["socratic_stats"]["multiturn_percent"] = round((multiturn_count / total_accepted * 100), 2)
        stats["socratic_stats"]["avg_token_length"] = round(sum(token_lengths) / len(token_lengths), 1) if token_lengths else 0

    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        
    print("\n--- PHASE 1.5 PILOT DATASET COMPLETE ---")
    print(json.dumps(stats, indent=2))
    print(f"Saved pilot dataset to {pilot_file}")

if __name__ == "__main__":
    main()
