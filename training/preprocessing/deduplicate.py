import os
import hashlib
from datasets import load_from_disk, concatenate_datasets

def get_content_hash(example):
    # Create a string representation of the messages to hash
    content_str = "".join([msg.get("content", "") for msg in example.get("messages", [])])
    return hashlib.md5(content_str.encode("utf-8")).hexdigest()

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    clean_dir = os.path.join(root_dir, "training", "datasets", "cleaned")
    dedup_dir = os.path.join(root_dir, "training", "datasets", "deduplicated")
    os.makedirs(dedup_dir, exist_ok=True)
    
    seen_hashes = set()
    
    for ds_folder in os.listdir(clean_dir):
        ds_path = os.path.join(clean_dir, ds_folder)
        try:
            print(f"Deduplicating {ds_folder}...")
            ds = load_from_disk(ds_path)
            
            def is_unique(example):
                h = get_content_hash(example)
                if h in seen_hashes:
                    return False
                seen_hashes.add(h)
                return True
                
            initial_count = len(ds)
            dedup_ds = ds.filter(is_unique)
            final_count = len(dedup_ds)
            
            print(f"Removed {initial_count - final_count} duplicates from {ds_folder} ({final_count} remaining)")
            
            save_path = os.path.join(dedup_dir, ds_folder)
            dedup_ds.save_to_disk(save_path)
        except Exception as e:
            print(f"Failed to deduplicate {ds_folder}: {e}")

if __name__ == "__main__":
    main()
