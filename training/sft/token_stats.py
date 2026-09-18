import os
from transformers import AutoTokenizer
from dataset import load_and_format_dataset

def main():
    print("Loading tokenizer Qwen/Qwen3-8B...")
    # Make sure we use the HF_TOKEN from environment
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
    
    print("Loading dataset...")
    file_paths = [
        "training/datasets/processed/lmsys_processed.jsonl",
        "training/datasets/processed/NuminaMath_processed.jsonl"
    ]
    ds = load_and_format_dataset(file_paths, tokenizer=tokenizer)
    
    print(f"Loaded {len(ds)} samples. Calculating token statistics...")
    
    def count_tokens(example):
        return {"token_count": len(tokenizer.encode(example["text"]))}
        
    ds = ds.map(count_tokens, num_proc=4)
    
    total_tokens = sum(ds["token_count"])
    max_tokens = max(ds["token_count"])
    min_tokens = min(ds["token_count"])
    avg_tokens = total_tokens / len(ds)
    
    print(f"Total samples: {len(ds)}")
    print(f"Total tokens: {total_tokens:,}")
    print(f"Max tokens in a sample: {max_tokens:,}")
    print(f"Min tokens in a sample: {min_tokens:,}")
    print(f"Average tokens per sample: {avg_tokens:,.2f}")
    
    # Save the stats to final report
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    report_path = os.path.join(root_dir, "training", "datasets", "final", "dataset_coverage_report.md")
    
    with open(report_path, "a", encoding="utf-8") as f:
        f.write("## Token Statistics (Qwen/Qwen3-8B)\n")
        f.write(f"- **Total Tokens:** {total_tokens:,}\n")
        f.write(f"- **Max Tokens:** {max_tokens:,}\n")
        f.write(f"- **Avg Tokens:** {avg_tokens:,.2f}\n")

if __name__ == "__main__":
    main()
