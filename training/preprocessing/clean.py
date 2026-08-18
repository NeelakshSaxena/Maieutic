import os
import re
from datasets import load_from_disk

def is_socratic(example):
    """
    Heuristic filter to check if the example is suitable for Socratic tutoring.
    We want to remove obvious direct-answer examples if they are extremely short
    or just blurt out the answer immediately.
    """
    messages = example.get("messages", [])
    if not messages:
        return False
        
    # Find the first assistant response
    first_assistant_msg = None
    for msg in messages:
        if msg.get("role") == "assistant":
            first_assistant_msg = msg.get("content", "")
            break
            
    if not first_assistant_msg:
        # If there's no assistant response, it's not a useful training example
        return False
        
    content_lower = first_assistant_msg.lower()
    
    # Direct answer red flags in the first response
    red_flags = [
        "the answer is",
        "here is the solution",
        "here is the complete code",
        "here's the answer"
    ]
    
    # If the response is very short and contains a red flag, we drop it.
    if len(first_assistant_msg.split()) < 50 and any(flag in content_lower for flag in red_flags):
        return False
        
    return True

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    norm_dir = os.path.join(root_dir, "training", "datasets", "normalized")
    clean_dir = os.path.join(root_dir, "training", "datasets", "cleaned")
    os.makedirs(clean_dir, exist_ok=True)
    
    for ds_folder in os.listdir(norm_dir):
        ds_path = os.path.join(norm_dir, ds_folder)
        try:
            print(f"Cleaning {ds_folder}...")
            ds = load_from_disk(ds_path)
            
            initial_count = len(ds)
            cleaned_ds = ds.filter(is_socratic)
            final_count = len(cleaned_ds)
            
            print(f"Filtered {initial_count - final_count} examples from {ds_folder} ({final_count} remaining)")
            
            save_path = os.path.join(clean_dir, ds_folder)
            cleaned_ds.save_to_disk(save_path)
        except Exception as e:
            print(f"Failed to clean {ds_folder}: {e}")

if __name__ == "__main__":
    main()
