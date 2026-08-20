import os
import pandas as pd
from datasets import load_from_disk, concatenate_datasets

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dedup_dir = os.path.join(root_dir, "training", "datasets", "deduplicated")
    final_dir = os.path.join(root_dir, "training", "datasets", "final")
    os.makedirs(final_dir, exist_ok=True)
    
    datasets = []
    stats = []
    
    for ds_folder in os.listdir(dedup_dir):
        ds_path = os.path.join(dedup_dir, ds_folder)
        try:
            ds = load_from_disk(ds_path)
            datasets.append(ds)
            stats.append({
                "Dataset": ds_folder,
                "Samples": len(ds)
            })
        except Exception as e:
            print(f"Failed to load {ds_folder}: {e}")
            
    if not datasets:
        print("No datasets to process.")
        return
        
    combined_ds = concatenate_datasets(datasets)
    
    # Shuffle and split
    combined_ds = combined_ds.shuffle(seed=42)
    split_ds = combined_ds.train_test_split(test_size=0.1)
    
    print("Saving final datasets...")
    split_ds.save_to_disk(final_dir)
    
    # Export Phase 1 processed JSONL files for Phase 2 SFT training
    processed_dir = os.path.join(root_dir, "training", "datasets", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    import json
    # Group samples by source and save
    lmsys_samples = []
    numina_samples = []
    
    for sample in combined_ds:
        source = sample.get("source_dataset", "").lower()
        if "lmsys" in source or "wildchat" in source:
            lmsys_samples.append(sample)
        else:
            numina_samples.append(sample)
            
    lmsys_path = os.path.join(processed_dir, "lmsys_processed.jsonl")
    with open(lmsys_path, "w", encoding="utf-8") as f:
        for s in lmsys_samples:
            f.write(json.dumps(s) + "\n")
    print(f"Exported {len(lmsys_samples)} samples to {lmsys_path}")
    
    numina_path = os.path.join(processed_dir, "NuminaMath_processed.jsonl")
    with open(numina_path, "w", encoding="utf-8") as f:
        for s in numina_samples:
            f.write(json.dumps(s) + "\n")
    print(f"Exported {len(numina_samples)} samples to {numina_path}")
    
    # Generate report
    total_samples = len(combined_ds)
    df_stats = pd.DataFrame(stats)
    
    report_path = os.path.join(final_dir, "dataset_coverage_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Dataset Coverage Report\n\n")
        f.write("## Overview\n")
        f.write(f"Total Samples: {total_samples}\n")
        f.write(f"Train Split: {len(split_ds['train'])}\n")
        f.write(f"Validation Split: {len(split_ds['test'])}\n\n")
        f.write("## Source Distribution\n")
        f.write(df_stats.to_markdown(index=False))
        f.write("\n")
        
    print(f"Pipeline complete! Report generated at {report_path}")

if __name__ == "__main__":
    main()
