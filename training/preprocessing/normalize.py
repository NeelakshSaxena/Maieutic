import os
import json
from datasets import load_from_disk
from unified_schema import UnifiedSchema, Message, Metadata

def normalize_lmsys(example):
    messages = []
    # LMSYS conversations are typically lists of dicts with 'role' and 'content'
    # but sometimes role is 'human'/'gpt' or similar
    for msg in example.get("conversation", []):
        role = msg.get("role", "")
        if role in ["human", "user"]:
            role = "user"
        elif role in ["assistant", "gpt", "model"]:
            role = "assistant"
        else:
            role = "system"
        messages.append(Message(role=role, content=msg.get("content", "")))
        
    metadata = Metadata(
        language=example.get("language", "unknown"),
        subject=None,
        difficulty=None,
        quality_score=None,
        has_reasoning=False,
        has_final_answer=True,
        is_verified=False,
        original_id=example.get("conversation_id", "")
    )
    
    return UnifiedSchema(
        id=f"lmsys_{example.get('conversation_id', hash(str(example)))}",
        source_dataset="lmsys-chat-1m",
        domain="chat",
        messages=messages,
        metadata=metadata
    ).model_dump()

def normalize_wildchat(example):
    messages = []
    for msg in example.get("conversation", []):
        role = msg.get("role", "user")
        if role not in ["system", "user", "assistant"]:
            role = "user" if role == "human" else "assistant"
        messages.append(Message(role=role, content=msg.get("content", "")))
        
    metadata = Metadata(
        language=example.get("language", "unknown"),
        subject=None,
        difficulty=None,
        quality_score=None,
        has_reasoning=False,
        has_final_answer=True,
        is_verified=False,
        original_id=example.get("conversation_hash", "")
    )
    
    return UnifiedSchema(
        id=f"wildchat_{example.get('conversation_hash', hash(str(example)))}",
        source_dataset="WildChat",
        domain="chat",
        messages=messages,
        metadata=metadata
    ).model_dump()

def normalize_numinamath(example, source_name):
    # NuminaMath typically has 'problem' and 'solution'
    messages = [
        Message(role="user", content=example.get("problem", "")),
        Message(role="assistant", content=example.get("solution", ""))
    ]
    
    metadata = Metadata(
        language="en",
        subject="math",
        difficulty=None,
        quality_score=None,
        has_reasoning=True,
        has_final_answer=True,
        is_verified=True, # usually verified math data
        original_id=example.get("id", "")
    )
    
    return UnifiedSchema(
        id=f"{source_name.lower()}_{hash(example.get('problem', ''))}",
        source_dataset=source_name,
        domain="math",
        messages=messages,
        metadata=metadata
    ).model_dump()

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_dir = os.path.join(root_dir, "training", "datasets", "raw")
    norm_dir = os.path.join(root_dir, "training", "datasets", "normalized")
    os.makedirs(norm_dir, exist_ok=True)
    
    # Mapping of dataset folder names to normalization functions
    normalizers = {
        "lmsys_lmsys-chat-1m": normalize_lmsys,
        "allenai_WildChat": normalize_wildchat,
        "AI-MO_NuminaMath-CoT": lambda e: normalize_numinamath(e, "NuminaMath-CoT"),
        "AI-MO_NuminaMath-TIR": lambda e: normalize_numinamath(e, "NuminaMath-TIR"),
        "AI-MO_NuminaMath-1.5": lambda e: normalize_numinamath(e, "NuminaMath-1.5"),
    }
    
    for ds_folder in os.listdir(raw_dir):
        if ds_folder not in normalizers:
            continue
            
        ds_path = os.path.join(raw_dir, ds_folder)
        try:
            print(f"Normalizing {ds_folder}...")
            ds = load_from_disk(ds_path)
            norm_func = normalizers[ds_folder]
            
            # Map the function over the dataset
            normalized_ds = ds.map(norm_func, remove_columns=ds.column_names)
            
            save_path = os.path.join(norm_dir, ds_folder)
            normalized_ds.save_to_disk(save_path)
            print(f"Successfully normalized {ds_folder} to {save_path}")
        except Exception as e:
            print(f"Failed to normalize {ds_folder}: {e}")

if __name__ == "__main__":
    main()
