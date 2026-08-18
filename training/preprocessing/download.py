import os
import sys
from datasets import load_dataset
from dotenv import load_dotenv

def check_auth():
    load_dotenv()
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("ERROR: HF_TOKEN environment variable is missing.", file=sys.stderr)
        print("Please configure Hugging Face authentication (HF_TOKEN) in your .env file or environment.", file=sys.stderr)
        sys.exit(1)
    return hf_token

DATASETS_TO_DOWNLOAD = [
    {"name": "lmsys/lmsys-chat-1m", "split": "train", "samples": 5000},
    {"name": "allenai/WildChat", "split": "train", "samples": 5000},
    {"name": "AI-MO/NuminaMath-CoT", "split": "train", "samples": 5000},
    {"name": "AI-MO/NuminaMath-TIR", "split": "train", "samples": 2000},
    {"name": "AI-MO/NuminaMath-1.5", "split": "train", "samples": 5000},
]

def main():
    hf_token = check_auth()
    
    # Store everything in the project root under training/datasets/raw/
    # We will enforce this by setting the cache_dir to a local directory
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cache_dir = os.path.join(root_dir, ".cache", "huggingface")
    raw_dir = os.path.join(root_dir, "training", "datasets", "raw")
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(raw_dir, exist_ok=True)
    
    for ds_info in DATASETS_TO_DOWNLOAD:
        ds_name = ds_info["name"]
        split = ds_info["split"]
        samples = ds_info["samples"]
        print(f"Downloading {ds_name} (subset: {samples} samples)...")
        try:
            # We use streaming=False, but to avoid downloading the whole dataset we could try streaming=True
            # and then taking `samples` and saving to disk, which saves huge amounts of time and space.
            ds = load_dataset(ds_name, split=split, streaming=True, token=hf_token, cache_dir=cache_dir)
            ds_subset = ds.take(samples)
            
            # Convert iterable dataset to list of dicts to save locally
            data = list(ds_subset)
            
            # Reconstruct as a regular Dataset to save to disk
            from datasets import Dataset
            regular_ds = Dataset.from_list(data)
            
            # Save to raw_dir
            save_path = os.path.join(raw_dir, ds_name.replace("/", "_"))
            regular_ds.save_to_disk(save_path)
            print(f"Successfully saved {ds_name} to {save_path}")
            
        except Exception as e:
            print(f"ERROR: Failed to download {ds_name}: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
