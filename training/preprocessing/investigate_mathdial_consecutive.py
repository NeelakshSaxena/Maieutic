import os
import json
from transformers import AutoTokenizer

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, "../.."))
    dataset_path = os.path.join(project_root, "training/datasets/socratic/socratic_phase1_5_v2_cleaned.jsonl")
    report_path = os.path.join(project_root, "mathdial_consecutive_investigation.md")
    
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
    
    affected_conversations = []
    total_mathdial = 0
    total_consecutive_assistant_pairs = 0
    total_consecutive_user_pairs = 0
    max_run_length = 0
    
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            if item.get("source_dataset") == "mathdial":
                total_mathdial += 1
                messages = item.get("messages", [])
                
                # Analyze runs
                has_consecutive = False
                current_run_role = None
                current_run_length = 0
                
                for msg in messages:
                    role = msg["role"]
                    if role == current_run_role:
                        current_run_length += 1
                        if current_run_length > max_run_length:
                            max_run_length = current_run_length
                        if role == "assistant":
                            total_consecutive_assistant_pairs += 1
                        elif role == "user":
                            total_consecutive_user_pairs += 1
                        has_consecutive = True
                    else:
                        current_run_role = role
                        current_run_length = 1
                        
                if has_consecutive:
                    affected_conversations.append(item)

    print(f"Total MathDial: {total_mathdial}")
    print(f"Affected: {len(affected_conversations)}")
    
    # Write report
    with open(report_path, "w", encoding="utf-8") as out:
        out.write("# MathDial Consecutive Roles Investigation\n\n")
        out.write("## Quantitative Analysis\n")
        out.write(f"- **Total MathDial Conversations:** {total_mathdial}\n")
        out.write(f"- **Conversations Affected:** {len(affected_conversations)} ({(len(affected_conversations)/total_mathdial)*100:.1f}%)\n")
        out.write(f"- **Total Consecutive Assistant Pairs:** {total_consecutive_assistant_pairs}\n")
        out.write(f"- **Total Consecutive User Pairs:** {total_consecutive_user_pairs}\n")
        out.write(f"- **Maximum Consecutive Run Length:** {max_run_length}\n\n")
        
        out.write("## 10 Representative Examples\n\n")
        
        for i, item in enumerate(affected_conversations[:10]):
            out.write(f"### Example {i+1} (ID: {item.get('id')})\n")
            out.write("#### Normalized Messages:\n")
            for msg in item["messages"]:
                out.write(f"**[{msg['role']}]**: {msg['content']}\n\n")
            out.write("#### Serialized:\n")
            out.write("```text\n")
            out.write(tokenizer.apply_chat_template(item["messages"], tokenize=False, add_generation_prompt=False))
            out.write("\n```\n\n")
            out.write("---\n\n")

if __name__ == "__main__":
    main()
