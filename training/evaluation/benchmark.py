import os
import json
import subprocess
import tempfile

def run_capability_benchmark(model_path, is_base_model=False):
    """
    Runs GSM8K and MMLU benchmarks using lm-evaluation-harness.
    We use a small limit (e.g. 50 shots) for quick retention checking.
    """
    print(f"Running capability benchmark on: {model_path}")
    
    # We will use the CLI of lm_eval to generate the output and parse it
    # We restrict to small tasks
    tasks = "gsm8k,mmlu"
    limit = 50
    
    # Temporary output dir for lm-eval
    with tempfile.TemporaryDirectory() as tmpdir:
        # Build command
        # If it's a LoRA adapter, we need to pass peft=model_path, pretrained=base_model
        # But wait, inference_test.py merged them or loaded them natively.
        # lm-eval supports peft via `pretrained=base_model,peft=model_path`
        if is_base_model:
            model_args = f"pretrained={model_path}"
        else:
            # We assume model_path is the peft adapter and the base model is Qwen/Qwen3-8B
            model_args = f"pretrained=Qwen/Qwen3-8B,peft={model_path},dtype=bfloat16"
            
        cmd = [
            "lm_eval",
            "--model", "hf",
            "--model_args", model_args,
            "--tasks", tasks,
            "--limit", str(limit),
            "--device", "cuda:0",
            "--batch_size", "4",
            "--output_path", tmpdir
        ]
        
        print(f"Executing: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Find the result json in tmpdir
            results_file = None
            for root, dirs, files in os.walk(tmpdir):
                for f in files:
                    if f.endswith(".json") and not f.startswith("samples_"):
                        results_file = os.path.join(root, f)
                        break
                        
            if not results_file:
                print("Failed to find lm_eval results JSON.")
                return None
                
            with open(results_file, "r") as f:
                res_data = json.load(f)
                
            # Parse accuracy
            metrics = {}
            if "results" in res_data:
                for task, task_metrics in res_data["results"].items():
                    if "exact_match,strict-match" in task_metrics:
                        acc = task_metrics["exact_match,strict-match"]
                    elif "acc,none" in task_metrics:
                        acc = task_metrics["acc,none"]
                    else:
                        acc = list(task_metrics.values())[0] # Fallback
                    metrics[task] = acc
            return metrics
            
        except subprocess.CalledProcessError as e:
            print(f"lm_eval failed: {e.stderr}")
            return None
            
if __name__ == "__main__":
    # Test script
    import sys
    if len(sys.argv) > 1:
        model = sys.argv[1]
        is_base = "--base" in sys.argv
        print(run_capability_benchmark(model, is_base))
    else:
        print("Usage: python benchmark.py <model_path> [--base]")
