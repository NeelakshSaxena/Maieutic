import os
import json
from unsloth import FastLanguageModel
import lm_eval
from lm_eval.models.huggingface import HFLM

def run_capability_benchmark(model_path, is_base_model=False):
    """
    Runs GSM8K and MMLU benchmarks using lm-evaluation-harness Python API.
    We load the model using Unsloth to safely utilize 4-bit quantization and prevent OOM.
    """
    print(f"Running capability benchmark on: {model_path}")
    
    # 1. Load model via Unsloth (handles 4-bit safely)
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = model_path,
        max_seq_length = 4096,
        dtype = None,
        load_in_4bit = True,
    )
    FastLanguageModel.for_inference(model)
    
    # 2. Wrap model for lm_eval
    lm_eval_model = HFLM(
        pretrained=model,
        tokenizer=tokenizer,
        batch_size=2
    )
    
    # 3. Run evaluation
    results = lm_eval.simple_evaluate(
        model=lm_eval_model,
        tasks=["gsm8k", "mmlu"],
        limit=50
    )
    
    # 4. Parse results
    metrics = {}
    if "results" in results:
        for task, task_metrics in results["results"].items():
            if "exact_match,strict-match" in task_metrics:
                acc = task_metrics["exact_match,strict-match"]
            elif "acc,none" in task_metrics:
                acc = task_metrics["acc,none"]
            else:
                acc = list(task_metrics.values())[0] # Fallback
            metrics[task] = acc
            
    # Cleanup memory
    import torch
    del lm_eval_model
    del model
    del tokenizer
    torch.cuda.empty_cache()
    
    return metrics

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        model = sys.argv[1]
        is_base = "--base" in sys.argv
        print(run_capability_benchmark(model, is_base))
    else:
        print("Usage: python benchmark.py <model_path> [--base]")
