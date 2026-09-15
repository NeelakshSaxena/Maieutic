import os
import sys

# Set Hugging Face cache to project root to avoid global cache clutter
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../.."))
os.environ["HF_HOME"] = os.path.join(project_root, ".hf_cache")

import json
import random
from datasets import load_dataset

SYSTEM_PROMPT = "You are Maieutic, an expert Socratic tutor. You must never give the student the direct answer. Instead, ask guiding questions, provide hints, and help them arrive at the answer themselves."

def format_socrateach(item, idx):
    # meric533/socrateach-sft already has standard 'messages' format
    messages = item.get("messages", [])
    if not messages and "dialogue" in item:
        messages = item["dialogue"]
        
    final_messages = []
    # Ensure system prompt is set to Maieutic
    has_system = False
    for m in messages:
        if m.get("role") == "system":
            final_messages.append({"role": "system", "content": SYSTEM_PROMPT})
            has_system = True
        else:
            final_messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})
            
    if not has_system:
        final_messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
        
    return {
        "id": f"socrateach_{idx}",
        "source_dataset": "socrateach",
        "domain": "math",
        "type": "socratic",
        "messages": final_messages,
        "metadata": {
            "strategy_used": "socratic",
            "is_multiturn": len(final_messages) > 3
        }
    }

def format_mathdial(item, idx):
    # MathDial format
    raw_dialogue = item.get("conversation", item.get("dialogue", item.get("conversations", item.get("turns", item.get("messages", [])))))
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if isinstance(raw_dialogue, str):
        # MathDial uses |EOM| delimiter
        if "|EOM|" in raw_dialogue:
            turns = raw_dialogue.split("|EOM|")
            for turn in turns:
                turn = turn.strip()
                if not turn: continue
                if turn.startswith("Teacher:"):
                    messages.append({"role": "assistant", "content": turn[len("Teacher:"):].strip()})
                elif turn.startswith("Student:"):
                    messages.append({"role": "user", "content": turn[len("Student:"):].strip()})
                else:
                    # Strict alternation based on previous role
                    last_role = messages[-1]["role"]
                    role = "user" if last_role in ["system", "assistant"] else "assistant"
                    
                    # MathDial often prepends the student's name (e.g., 'Steven: '). We'll strip it if it exists.
                    if ":" in turn[:20]:
                        turn = turn.split(":", 1)[1].strip()
                        
                    messages.append({"role": role, "content": turn})
            raw_dialogue = [] # Done processing
        else:
            try:
                raw_dialogue = json.loads(raw_dialogue)
            except json.JSONDecodeError:
                raw_dialogue = [raw_dialogue]
                
    # Fallback for other standard structures if it wasn't the |EOM| string
    for turn in raw_dialogue:
        if isinstance(turn, dict):
            role = turn.get("speaker", turn.get("role", "unknown"))
            # normalize roles
            if role.lower() in ["teacher", "tutor", "assistant"]:
                role = "assistant"
            elif role.lower() in ["student", "user"]:
                role = "user"
            content = turn.get("text", turn.get("content", turn.get("utterance", "")))
            messages.append({"role": role, "content": content})
        elif isinstance(turn, str):
             # If it's just strings, alternate user/assistant based on previous role
             last_role = messages[-1]["role"]
             role = "user" if last_role in ["system", "assistant"] else "assistant"
             
             if ":" in turn[:20]:
                 turn = turn.split(":", 1)[1].strip()
                 
             messages.append({"role": role, "content": turn})

    # MathDial specific normalizations
    norm_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in messages[1:]:
        role = msg["role"]
        content = msg["content"].strip()
        
        # 1. Remove empty messages (e.g. "(focus)")
        if not content or content in ["(focus)", "(generic)", "(probing)", "(telling)"]:
            continue
            
        # 2 & 3. Remove exact duplicate adjacent AND merge remaining consecutive
        if norm_messages[-1]["role"] == role:
            if norm_messages[-1]["content"].strip() == content:
                continue # Skip exact duplicate
            else:
                norm_messages[-1]["content"] += "\n" + content
        else:
            norm_messages.append({"role": role, "content": content})

    return {
        "id": f"mathdial_{item.get('qid', idx)}",
        "source_dataset": "mathdial",
        "domain": "math",
        "type": "socratic",
        "messages": norm_messages,
        "metadata": {
            "strategy_used": "probing_focus",
            "scenario": item.get("scenario", ""),
            "is_multiturn": len(messages) > 3
        }
    }



def format_lmsys(item, idx):
    messages = []
    # LMSYS format: list of dicts with role and content
    for msg in item.get("conversation", []):
        role = msg.get("role", "")
        if role in ["human", "user"]:
            role = "user"
        elif role in ["assistant", "gpt", "model"]:
            role = "assistant"
        else:
            role = "system"
        messages.append({"role": role, "content": msg.get("content", "")})
    
    # Prepend system prompt
    final_messages = [{"role": "system", "content": "You are a helpful assistant."}]
    final_messages.extend(messages)
    
    return {
        "id": f"lmsys_{item.get('conversation_id', idx)}",
        "source_dataset": "lmsys",
        "domain": "chat",
        "type": "reasoning_replay",
        "messages": final_messages,
        "metadata": {
            "strategy_used": "reasoning_replay",
            "is_multiturn": len(final_messages) > 3
        }
    }


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../.."))
    socratic_dir = os.path.join(project_root, "training", "datasets", "socratic")
    os.makedirs(socratic_dir, exist_ok=True)
    
    pilot_file = os.path.join(socratic_dir, "socratic_phase1_5_v2.jsonl")
    
    print("--- Phase 1.5 Real-Data Dataset Builder ---")
    
    final_dataset = []
    
    # 1. Load SocraTeach (~7,500 examples)
    print("Loading SocraTeach-SFT (meric533/socrateach-sft)...")
    try:
        ds_socra = load_dataset("meric533/socrateach-sft", split="train", streaming=True)
        count = 0
        for item in ds_socra:
            if count >= 7500:
                break
            formatted = format_socrateach(item, count)
            # Only keep Socratic ones (not replay)
            if len(formatted["messages"]) > 2: 
                final_dataset.append(formatted)
                count += 1
        print(f"Loaded {count} SocraTeach examples.")
    except Exception as e:
        print(f"Failed to load SocraTeach: {e}")

    # 2. Load MathDial (~2,500 examples)
    print("Loading MathDial (eth-nlped/mathdial)...")
    try:
        ds_mathdial = load_dataset("eth-nlped/mathdial", split="train", streaming=True)
        count = 0
        for item in ds_mathdial:
            if count >= 2500:
                break
            formatted = format_mathdial(item, count)
            if len(formatted["messages"]) > 2:
                final_dataset.append(formatted)
                count += 1
        print(f"Loaded {count} MathDial examples.")
    except Exception as e:
        print(f"Failed to load MathDial: {e}")

    # 3. Load Eedi (2,000 examples)
    print("Loading Eedi (Eedi/Question-Anchored-Tutoring-Dialogues-2k)...")
    try:
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
                "seq": item.get("MessageSequence", 0)
            })
            
        count = 0
        for iid, msgs in eedi_convos.items():
            if count >= 2000:
                break
            
            # Sort messages by sequence correctly
            msgs.sort(key=lambda x: x["seq"])
            
            final_msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in msgs:
                if final_msgs[-1]["role"] == m["role"]:
                    # Merge consecutive same-role messages
                    final_msgs[-1]["content"] += "\n" + m["content"]
                else:
                    final_msgs.append({"role": m["role"], "content": m["content"]})
                
            if len(final_msgs) > 3: # at least system + 3 turns
                final_dataset.append({
                    "id": f"eedi_{iid}",
                    "source_dataset": "eedi",
                    "domain": "math",
                    "type": "socratic",
                    "messages": final_msgs,
                    "metadata": {
                        "strategy_used": "talk_moves",
                        "is_multiturn": True
                    }
                })
                count += 1
        print(f"Loaded {count} Eedi examples.")
    except Exception as e:
        print(f"Failed to load Eedi: {e}")

    # 4. Load General/Reasoning Replay (to achieve 75/25 split)
    print("Loading General Reasoning Replay...")
    target_replay = len(final_dataset) // 3  # If tutoring is 75%, general is 25%. So general = tutoring / 3.
    
    # Direct LMSYS streaming for reconstruction (replaces old processed file dependency temporarily)
    print("Loading lmsys-chat-1m (streaming fallback)...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        hf_token = os.environ.get("HF_TOKEN")
        
        # Pass split directly without filtering by language to keep it simple, or filter for English
        ds_lmsys = load_dataset("lmsys/lmsys-chat-1m", split="train", streaming=True, token=hf_token)
        replay_count = 0
        for item in ds_lmsys:
            # Simple language filter if available (often LMSYS has a 'language' column)
            if item.get("language") and item.get("language") != "English":
                continue
                
            if replay_count >= target_replay:
                break
            
            formatted = format_lmsys(item, replay_count)
            # Ensure it has an assistant response
            if any(m["role"] == "assistant" for m in formatted["messages"]):
                final_dataset.append(formatted)
                replay_count += 1
                
        print(f"Loaded {replay_count} General Reasoning Replay examples.")
    except Exception as e:
        print(f"Failed to load LMSYS streaming: {e}")

    # Shuffle dataset
    random.shuffle(final_dataset)

    # Save to file
    with open(pilot_file, "w", encoding="utf-8") as f:
        for item in final_dataset:
            f.write(json.dumps(item) + "\n")
            
    print(f"\nPhase 1.5 dataset built with {len(final_dataset)} examples.")
    print(f"Saved to: {pilot_file}")

if __name__ == "__main__":
    main()
