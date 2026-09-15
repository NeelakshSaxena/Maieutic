import os
import json
from datasets import load_dataset
from transformers import AutoTokenizer

def print_example(source_name, raw_item, normalized_item, tokenizer):
    print("="*60)
    print(f"SOURCE: {source_name}")
    print("="*60)
    print("RAW:")
    print(json.dumps(raw_item, indent=2))
    print("-" * 30)
    print("NORMALIZED MESSAGES:")
    for m in normalized_item["messages"]:
        print(f"[{m['role']}]: {m['content']}")
    print("-" * 30)
    print("SERIALIZED:")
    print(tokenizer.apply_chat_template(normalized_item["messages"], tokenize=False, add_generation_prompt=False))
    print("="*60 + "\n")

def check_consecutive_roles(dataset_path):
    print("Counting consecutive same-role messages by source...")
    counts = {"mathdial": 0, "socrateach": 0, "eedi": 0, "lmsys": 0}
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            src = item.get("source_dataset", "unknown")
            messages = item.get("messages", [])
            has_consecutive = False
            for i in range(2, len(messages)): # skip system prompt at index 0 usually
                if messages[i]["role"] == messages[i-1]["role"]:
                    has_consecutive = True
                    break
            if has_consecutive:
                counts[src] = counts.get(src, 0) + 1
    
    print("Conversations with consecutive same-role messages:")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print("\n")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../.."))
    dataset_path = os.path.join(project_root, "training/datasets/socratic/socratic_phase1_5_v2_cleaned.jsonl")
    
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
    
    check_consecutive_roles(dataset_path)
    
    # We will import the format functions from build_pilot_dataset to see what they produce
    sys.path.append(os.path.join(project_root, "training/preprocessing"))
    import build_pilot_dataset as builder
    
    print("Fetching raw MathDial examples...")
    ds_mathdial = load_dataset("eth-nlped/mathdial", split="train", streaming=True)
    count = 0
    for item in ds_mathdial:
        formatted = builder.format_mathdial(item, count)
        print_example("MathDial", item, formatted, tokenizer)
        count += 1
        if count >= 3:
            break
            
    print("Fetching raw Eedi examples...")
    ds_eedi = load_dataset("Eedi/Question-Anchored-Tutoring-Dialogues-2k", "anchored-dialogues", split="train", streaming=True)
    eedi_convos = {}
    for item in ds_eedi:
        iid = item.get("InterventionId")
        if not iid: continue
        if iid not in eedi_convos:
            eedi_convos[iid] = []
        eedi_convos[iid].append({
            "role": "assistant" if item.get("IsTutor") else "user",
            "content": item.get("MessageString", ""),
            "seq": item.get("MessageSequence", 0),
            "raw_item": item # store just one for the raw dump
        })
        if len(eedi_convos) > 3:
            break
            
    count = 0
    for iid, msgs in list(eedi_convos.items())[:3]:
        msgs.sort(key=lambda x: x["seq"])
        final_msgs = [{"role": "system", "content": builder.SYSTEM_PROMPT}]
        for m in msgs:
            final_msgs.append({"role": m["role"], "content": m["content"]})
        formatted = {"messages": final_msgs}
        print_example("Eedi", msgs[0]["raw_item"], formatted, tokenizer)
        
    print("Fetching raw SocraTeach examples...")
    ds_socra = load_dataset("meric533/socrateach-sft", split="train", streaming=True)
    count = 0
    for item in ds_socra:
        formatted = builder.format_socrateach(item, count)
        print_example("SocraTeach", item, formatted, tokenizer)
        count += 1
        if count >= 3:
            break

if __name__ == "__main__":
    import sys
    main()
