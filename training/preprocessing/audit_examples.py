import os
import json
import random
from collections import defaultdict
from transformers import AutoTokenizer

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../.."))
    dataset_path = os.path.join(project_root, "training/datasets/socratic/socratic_phase1_5_v2_cleaned.jsonl")
    
    # Write to project root temporarily, we can create the artifact from it later
    output_md = os.path.join(project_root, "behavioral_audit.md")
    
    print("Loading Qwen3 tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
    
    # Read the dataset
    data_by_source = defaultdict(list)
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            src = item.get("source_dataset", "unknown")
            data_by_source[src].append(item)
            
    print(f"Loaded {sum(len(v) for v in data_by_source.values())} total examples from {list(data_by_source.keys())}.")
    
    # Stratified Sampling Strategy
    random.seed(42)
    audit_samples = []
    
    # We want 10 examples from each source (SocraTeach, MathDial, Eedi, LMSYS)
    for src in ["socrateach", "mathdial", "eedi", "lmsys"]:
        items = data_by_source.get(src, [])
        if not items:
            continue
            
        # Stratify if possible
        if src in ["socrateach", "mathdial", "eedi"]:
            multi_turn = [x for x in items if x.get("metadata", {}).get("is_multiturn", False) or len(x.get("messages", [])) > 3]
            single_turn = [x for x in items if not (x.get("metadata", {}).get("is_multiturn", False) or len(x.get("messages", [])) > 3)]
            
            samples = []
            if len(multi_turn) >= 7 and len(single_turn) >= 3:
                samples.extend(random.sample(multi_turn, 7))
                samples.extend(random.sample(single_turn, 3))
            else:
                samples = random.sample(items, min(10, len(items)))
                
        elif src == "lmsys":
            # For LMSYS, we want to see a mix, but mainly reasoning_replay
            samples = random.sample(items, min(10, len(items)))
            
        audit_samples.extend(samples)
        
    print(f"Selected {len(audit_samples)} samples for audit.")
    
    with open(output_md, "w", encoding="utf-8") as f:
        f.write("# Phase 1.5 Behavioral Audit\n\n")
        f.write("This document contains stratified samples from the `socratic_phase1_5_v2_cleaned.jsonl` dataset.\n\n")
        
        for item in audit_samples:
            src = item.get("source_dataset", "unknown")
            item_type = item.get("type", "unknown")
            item_id = item.get("id", "unknown")
            metadata = item.get("metadata", {})
            strategy = metadata.get("strategy_used", "none")
            
            f.write(f"## SOURCE: {src}\n")
            f.write(f"**TYPE**: {item_type} / {strategy}\n")
            f.write(f"**ID**: `{item_id}`\n\n")
            
            f.write("### MESSAGES:\n")
            messages = item.get("messages", [])
            for msg in messages:
                role = msg.get("role", "").upper()
                content = msg.get("content", "").strip()
                f.write(f"**{role}**: {content}\n\n")
                
            f.write("### QWEN3 SERIALIZATION:\n")
            f.write("```text\n")
            chat_text = "".join([f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in messages])
            f.write(chat_text)
            f.write("```\n\n")
            
            f.write("### AUDIT FLAGS:\n")
            # Generate dummy flags as diagnostic placeholders for manual review
            is_multiturn = len(messages) > 3
            last_assistant = next((m["content"] for m in reversed(messages) if m["role"] == "assistant"), "")
            
            flags = []
            flags.append("✓ Multi-turn" if is_multiturn else "✗ Single-turn")
            
            if src == "lmsys":
                looks_like_tutor = "?" in last_assistant and "think" in last_assistant.lower()
                flags.append("⚠ WARNING: Might be accidental tutoring" if looks_like_tutor else "✓ Looks like capability retention")
            else:
                generic_question = last_assistant.lower() in ["what do you think?", "how would you do it?"]
                flags.append("⚠ WARNING: Generic question" if generic_question else "✓ Context-specific (heuristically)")
                flags.append("[ ] Useful next step (MANUAL CHECK)")
                flags.append("[ ] No unnecessary answer leakage (MANUAL CHECK)")
                flags.append("[ ] Appropriate correction (MANUAL CHECK)")
                
            for flag in flags:
                f.write(f"- {flag}\n")
                
            f.write("\n---\n\n")
            
    print(f"Successfully generated {output_md}")

if __name__ == "__main__":
    main()
