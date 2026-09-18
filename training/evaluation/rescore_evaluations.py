import os
import json
from datetime import datetime
from tutoring_eval import evaluate_tutor_response

eval_dir = "/workspace/Maieutic/training/evaluation"

runs = [
    ("base", "BASE QWEN3-8B", "generated_responses_base.jsonl", "report_base.md", "92.0%", "75.6%"),
    ("sft", "SFT QWEN3-8B", "generated_responses_sft.jsonl", "report_sft.md", "72.0%", "75.2%")
]

for run_key, run_name, gen_file, report_file, gsm8k, mmlu in runs:
    gen_path = os.path.join(eval_dir, gen_file)
    if not os.path.exists(gen_path):
        print(f"Skipping {run_key}, file not found: {gen_path}")
        continue
        
    print(f"\n--- Rescoring {run_name} using corrected answer_leakage_prevention rubric ---")
    generations = []
    with open(gen_path, "r", encoding="utf-8") as f:
        for line in f:
            generations.append(json.loads(line))
            
    tutoring_scores = {
        "socratic_adherence": [],
        "answer_leakage_prevention": [],
        "decomposition_quality": [],
        "misconception_detection": [],
        "hint_quality": [],
        "correctness": []
    }
    
    evaluated_generations = []
    for i, gen in enumerate(generations):
        if (i + 1) % 10 == 0 or i == 0:
            print(f"  Judging {i+1}/{len(generations)}...")
        eval_json = evaluate_tutor_response(gen["prompt"], gen["generated_response"])
        if eval_json:
            for k in tutoring_scores.keys():
                if k in eval_json:
                    tutoring_scores[k].append(eval_json[k])
            gen["evaluation"] = eval_json
        else:
            gen["evaluation"] = None
        evaluated_generations.append(gen)
        
    avg_tutoring = {k: (sum(v)/len(v) if len(v) > 0 else "N/A") for k, v in tutoring_scores.items()}
    
    # Save raw rescored file
    raw_path = os.path.join(eval_dir, f"raw_eval_{run_key}.jsonl")
    with open(raw_path, "w", encoding="utf-8") as f:
        for g in evaluated_generations:
            f.write(json.dumps(g) + "\n")
            
    # Write updated report
    report_path = os.path.join(eval_dir, report_file)
    def format_score(score):
        return f"{score:.2f} / 5" if isinstance(score, float) else str(score)
        
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# MentorAI Phase 2 Evaluation Report\n\n")
        f.write(f"**Run:** {run_name}\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Metrics\n\n")
        f.write("| Metric | Score (out of 5 / %)| \n")
        f.write("| :--- | :---: |\n")
        f.write(f"| Socratic Adherence | {format_score(avg_tutoring['socratic_adherence'])} |\n")
        f.write(f"| Hint Quality | {format_score(avg_tutoring['hint_quality'])} |\n")
        f.write(f"| Answer Leakage Prevention | {format_score(avg_tutoring['answer_leakage_prevention'])} |\n")
        f.write(f"| Decomposition | {format_score(avg_tutoring['decomposition_quality'])} |\n")
        f.write(f"| Misconception Detection | {format_score(avg_tutoring['misconception_detection'])} |\n")
        f.write(f"| Correctness | {format_score(avg_tutoring['correctness'])} |\n")
        f.write(f"| GSM8K (Retention) | {gsm8k} |\n")
        f.write(f"| MMLU (Retention) | {mmlu} |\n\n")
        
    print(f"Rescoring complete for {run_name}! Report saved to {report_path}")
