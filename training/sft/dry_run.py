import os
import yaml
import torch
from unsloth import FastLanguageModel
from transformers import AutoTokenizer
from dataset import load_and_format_dataset
from completion_collator import DataCollatorForCompletionOnlyLM

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "../configs/qlora_8b_exp2.yaml")
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    print("==================================================")
    print("TRAINING CONFIGURATION DRY RUN")
    print("==================================================")
    print(f"1. Model: {config['model_id']}")
    print(f"2. Dataset path: {config['dataset_paths']}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(config["model_id"])
    
    # Load dataset
    dataset_paths = [os.path.join(script_dir, p) for p in config["dataset_paths"]]
    dataset = load_and_format_dataset(dataset_paths, tokenizer=tokenizer)
    total_count = len(dataset)
    print(f"3. Dataset count: {total_count}")
    
    dataset = dataset.train_test_split(test_size=0.05)
    train_count = len(dataset["train"])
    eval_count = len(dataset["test"])
    print(f"4. Train/validation split: {train_count} train / {eval_count} val")
    print(f"5. Random seed: 3407 (hardcoded in train.py)")
    print(f"6. Sequence length: {config['max_seq_length']}")
    print(f"7. Batch size: {config['per_device_train_batch_size']}")
    print(f"8. Gradient accumulation: {config['gradient_accumulation_steps']}")
    eff_batch = config['per_device_train_batch_size'] * config['gradient_accumulation_steps']
    print(f"9. Effective batch size: {eff_batch} per GPU")
    print(f"10. Learning rate: {config['learning_rate']}")
    print(f"11. LR scheduler: {config['lr_scheduler_type']}")
    print(f"12. Warmup ratio: {config['warmup_ratio']}")
    print(f"13. Number of epochs: {config.get('num_train_epochs', 1)}")
    print(f"14. Max steps: {config.get('max_steps', -1)}")
    print(f"15. Optimizer: adamw_8bit (hardcoded in train.py)")
    print(f"16. Weight decay: 0.01 (hardcoded in train.py)")
    print(f"17. Gradient checkpointing: unsloth (hardcoded in train.py)")
    print(f"18. Precision / 4-bit: bf16={config.get('bf16')}, use_4bit={config.get('use_4bit')}")
    print(f"19. LoRA rank: {config['r']}")
    print(f"20. LoRA alpha: {config['lora_alpha']}")
    print(f"21. LoRA dropout: {config['lora_dropout']}")
    print(f"22. LoRA target modules: {config['target_modules']}")
    print(f"23. Output directory: {config['output_dir']}")
    print(f"24. Save strategy: save_steps={config['save_steps']}")
    print(f"25. Logging steps: {config['logging_steps']}")
    
    # Serialize one example
    example_text = dataset["train"][0]["text"]
    has_system = "You are Maieutic, an expert Socratic tutor" in example_text
    print(f"26. System prompt included: {has_system}")
    print("27. Exact serialization format:")
    print("```text")
    print(example_text[:500] + "\n... [truncated]")
    print("```")
    
    # Check collator and masking
    response_template = "<|im_start|>assistant\\n"
    collator = DataCollatorForCompletionOnlyLM(response_template, tokenizer=tokenizer)
    
    # Tokenize the example
    tokenized = tokenizer(example_text)
    
    # Test collator on this one example
    batch = collator.torch_call([tokenized])
    labels = batch["labels"][0].tolist()
    input_ids = batch["input_ids"][0].tolist()
    
    unmasked_tokens = []
    for idx, lbl in zip(input_ids, labels):
        if lbl != -100:
            unmasked_tokens.append(idx)
            
    unmasked_text = tokenizer.decode(unmasked_tokens)
    
    print("28. What contributes to loss (UNMASKED text decoded):")
    print("```text")
    print(unmasked_text[:1000] + ("\n... [truncated]" if len(unmasked_text)>1000 else ""))
    print("```")
    
    print(f"29. User/system tokens masked? If multi-turn, are subsequent user messages masked?")
    
    # Real Batch Test
    print("\n==================================================")
    print("REAL BATCH DRY RUN VALIDATION")
    print("==================================================")
    
    # We create a dummy subset to batch (e.g. 8 examples)
    subset = dataset["train"].select(range(min(8, len(dataset["train"]))))
    
    # Format them exactly as SFTTrainer's dataloader would
    batch_features = [{"input_ids": tokenizer(item["text"])["input_ids"]} for item in subset]
    
    real_batch = collator.torch_call(batch_features)
    
    real_input_ids = real_batch["input_ids"]
    real_labels = real_batch["labels"]
    
    print(f"Batch shape: {real_input_ids.shape}")
    seq_lengths = [len(x) for x in real_input_ids]
    print(f"Min/Max sequence length: {min(seq_lengths)} / {max(seq_lengths)}")
    
    total_tokens = real_labels.numel()
    supervised_tokens = (real_labels != -100).sum().item()
    
    print(f"Total tokens: {total_tokens}")
    print(f"Supervised token count: {supervised_tokens}")
    print(f"Percentage supervised: {(supervised_tokens / total_tokens) * 100:.2f}%")
    
    sup_per_example = [(lbl != -100).sum().item() for lbl in real_labels]
    print(f"Supervised tokens per example: {sup_per_example}")
    zeros = sum(1 for x in sup_per_example if x == 0)
    print(f"Examples with zero supervised tokens: {zeros}")
    
    print("\nCONCLUSION: ")
    if "user" in unmasked_text and "<|im_start|>user" in unmasked_text:
        print("COLLATOR BLOCKED: User tokens still leaking!")
    elif zeros > 0:
        print("COLLATOR BLOCKED: Zero supervised tokens found in a real batch!")
    else:
        print("COLLATOR VALIDATED")

if __name__ == "__main__":
    main()
