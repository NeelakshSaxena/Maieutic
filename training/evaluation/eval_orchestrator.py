import os
import json
import argparse
import pandas as pd
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B", help="Base model or adapter path")
    parser.add_argument("--is-base", action="store_true", help="Set if evaluating a base model (no adapter)")
    return parser.parse_args()

def generate_responses(model, tokenizer, benchmark_path):
    print(f"Loading benchmark from {benchmark_path}...")
    samples = []
    with open(benchmark_path, "r", encoding="utf-8") as f:
        for line in f:
            samples.append(json.loads(line))
            
    print(f"Generating responses for {len(samples)} samples...")
    results = []
    
    for i, sample in enumerate(samples):
        print(f"  Generating {i+1}/{len(samples)}...")
        messages = sample.get("messages", [])
        
        system_msg = {"role": "system", "content": "You are MentorAI, an expert Socratic tutor. You must never give the student the direct answer. Instead, ask guiding questions, provide hints, and help them arrive at the answer themselves."}
        
        user_msg = next((m for m in messages if m["role"] == "user"), None)
        if not user_msg:
            continue
            
        chat = [system_msg, user_msg]
        
        inputs = tokenizer.apply_chat_template(
            chat,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        ).to("cuda")
        
        outputs = model.generate(input_ids=inputs, max_new_tokens=512, use_cache=True, pad_token_id=tokenizer.eos_token_id)
        
        new_tokens = outputs[0][inputs.shape[1]:]
        generated_text = tokenizer.decode(new_tokens, skip_special_tokens=True)
        
        results.append({
            "id": sample["id"],
            "domain": sample.get("domain", "unknown"),
            "prompt": user_msg["content"],
            "generated_response": generated_text
        })
        
    return results

def main():
    args = parse_args()
    
    run_name = "BASE QWEN3-8B" if args.is_base else "SFT QWEN3-8B"
    print(f"Starting Phase 2 Evaluation for: {run_name}")
    
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    eval_dir = os.path.join(root_dir, "training", "evaluation")
    benchmark_path = os.path.join(eval_dir, "mentorai_benchmark.jsonl")
    
    if not os.path.exists(benchmark_path):
        print("Error: mentorai_benchmark.jsonl not found. Run create_fixed_benchmark.py first.")
        return
        
    generations_file = os.path.join(eval_dir, f"generated_responses_{'base' if args.is_base else 'sft'}.jsonl")
    
    if os.path.exists(generations_file) and sum(1 for _ in open(generations_file, "r", encoding="utf-8")) == 100:
        print(f"Loading previously generated responses from {generations_file}")
        generations = []
        with open(generations_file, "r", encoding="utf-8") as f:
            for line in f:
                generations.append(json.loads(line))
    else:
        print(f"Loading Model: {args.model}")
        from unsloth import FastLanguageModel
        from unsloth.chat_templates import get_chat_template
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name = args.model,
            max_seq_length = 4096,
            dtype = None,
            load_in_4bit = True,
        )
        tokenizer = get_chat_template(tokenizer, chat_template="qwen-3")
        FastLanguageModel.for_inference(model)
        
        # 1. Generate responses
        generations = generate_responses(model, tokenizer, benchmark_path)
        
        with open(generations_file, "w", encoding="utf-8") as f:
            for g in generations:
                f.write(json.dumps(g) + "\n")
        print(f"Saved generated responses to {generations_file}")
        
        import torch
        del model
        del tokenizer
        torch.cuda.empty_cache()
        import gc
        gc.collect()
    
    # 2. Run LLM Judge
    print("\nRunning LLM Judge for Tutoring Metrics...")
    from tutoring_eval import evaluate_tutor_response
    
    tutoring_scores = {
        "socratic_adherence": [],
        "answer_leakage": [],
        "decomposition_quality": [],
        "misconception_detection": [],
        "hint_quality": [],
        "correctness": []
    }
    
    evaluated_generations = []
    
    for i, gen in enumerate(generations):
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
        
    # Calculate averages, handling N/A properly
    avg_tutoring = {k: (sum(v)/len(v) if len(v) > 0 else "N/A") for k, v in tutoring_scores.items()}
    
    # Save raw outputs
    out_jsonl = os.path.join(eval_dir, f"raw_eval_{'base' if args.is_base else 'sft'}.jsonl")
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for g in evaluated_generations:
            f.write(json.dumps(g) + "\n")
    print(f"\nRaw generated responses and judge scores saved to {out_jsonl}")
    
    # 3. Run Capability Benchmarks (GSM8K, MMLU)
    print("\nRunning Capability Benchmarks...")
    from benchmark import run_capability_benchmark
    cap_metrics = run_capability_benchmark(args.model, args.is_base)
    gsm8k_score = f"{cap_metrics.get('gsm8k', 0.0)*100:.1f}%" if cap_metrics else "N/A"
    mmlu_score = f"{cap_metrics.get('mmlu', 0.0)*100:.1f}%" if cap_metrics else "N/A"
    
    # 4. Generate Report
    report_path = os.path.join(eval_dir, f"report_{'base' if args.is_base else 'sft'}.md")
    
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
        f.write(f"| Answer Leakage | {format_score(avg_tutoring['answer_leakage'])} |\n")
        f.write(f"| Decomposition | {format_score(avg_tutoring['decomposition_quality'])} |\n")
        f.write(f"| Misconception Detection | {format_score(avg_tutoring['misconception_detection'])} |\n")
        f.write(f"| Correctness | {format_score(avg_tutoring['correctness'])} |\n")
        f.write(f"| GSM8K (Retention) | {gsm8k_score} |\n")
        f.write(f"| MMLU (Retention) | {mmlu_score} |\n\n")
        
    print(f"\nEvaluation Complete! Report saved to {report_path}")

if __name__ == "__main__":
    main()
