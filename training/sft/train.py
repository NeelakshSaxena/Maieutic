import os
import yaml
import torch
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth.chat_templates import get_chat_template

from dataset import load_and_format_dataset

def main():
    # Load config
    config_path = os.path.join(os.path.dirname(__file__), "../configs/qlora_8b.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    print(f"Loading base model {config['model_id']}...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = config["model_id"],
        max_seq_length = config["max_seq_length"],
        dtype = None, # Auto-detect
        load_in_4bit = config.get("use_4bit", True),
    )
    
    # Configure Qwen Chat template
    tokenizer = get_chat_template(
        tokenizer,
        chat_template = "qwen-2.5",
    )

    print("Setting up LoRA adapters...")
    model = FastLanguageModel.get_peft_model(
        model,
        r = config["r"],
        target_modules = config["target_modules"],
        lora_alpha = config["lora_alpha"],
        lora_dropout = config["lora_dropout"],
        bias = "none",
        use_gradient_checkpointing = "unsloth",
        random_state = 3407,
        use_rslora = False,
        loftq_config = None,
    )

    print("Loading dataset...")
    # Load dataset formatted with ChatML template and Socratic system prompts
    dataset_paths = [
        "../datasets/processed/lmsys_processed.jsonl",
        "../datasets/processed/NuminaMath_processed.jsonl"
    ]
    # Filter for real execution
    dataset_paths = [p for p in dataset_paths if os.path.exists(p)]
    
    dataset = load_and_format_dataset(dataset_paths, tokenizer=tokenizer)
    
    # Split for eval
    dataset = dataset.train_test_split(test_size=0.05)
    train_dataset = dataset["train"]
    eval_dataset = dataset["test"]

    print("Setting up Trainer...")
    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = train_dataset,
        eval_dataset = eval_dataset,
        dataset_text_field = "text",
        max_seq_length = config["max_seq_length"],
        dataset_num_proc = 2,
        packing = False, # Can be True for faster training
        args = TrainingArguments(
            per_device_train_batch_size = config["per_device_train_batch_size"],
            gradient_accumulation_steps = config["gradient_accumulation_steps"],
            warmup_ratio = config["warmup_ratio"],
            max_steps = config["max_steps"],
            learning_rate = float(config["learning_rate"]),
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = config["logging_steps"],
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = config["lr_scheduler_type"],
            seed = 3407,
            output_dir = config["output_dir"],
            report_to = "none", # Set to wandb for full run
            save_steps = config["save_steps"]
        ),
    )

    print("Starting training smoke test...")
    trainer_stats = trainer.train()

    print(f"Saving final adapter to {config['output_dir']}...")
    model.save_pretrained(config["output_dir"])
    tokenizer.save_pretrained(config["output_dir"])

if __name__ == "__main__":
    main()
