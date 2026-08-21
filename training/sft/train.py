import os
import yaml
import torch
import argparse
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth.chat_templates import get_chat_template

from dotenv import load_dotenv
load_dotenv()

from dataset import load_and_format_dataset
from transformers import TrainerCallback
import json
import time

class MonitorCallback(TrainerCallback):
    def __init__(self):
        self.metrics_dir = os.path.join(os.path.dirname(__file__), "../outputs/monitor")
        os.makedirs(self.metrics_dir, exist_ok=True)
        self.metrics_file = os.path.join(self.metrics_dir, "metrics.jsonl")
        
    def _write_metric(self, status, state, metrics=None):
        record = {
            "step": state.global_step,
            "epoch": state.epoch if state.epoch else 0.0,
            "status": status,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        if metrics:
            record["loss"] = metrics.get("loss", 0.0)
            record["learning_rate"] = metrics.get("learning_rate", 0.0)
            # Add speed metrics if available (usually only at end or if logged)
        
        with open(self.metrics_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def on_train_begin(self, args, state, control, **kwargs):
        self._write_metric("TRAINING", state)

    def on_log(self, args, state, control, logs=None, **kwargs):
        self._write_metric("TRAINING", state, logs)

    def on_save(self, args, state, control, **kwargs):
        self._write_metric("CHECKPOINTING", state)

    def on_train_end(self, args, state, control, **kwargs):
        self._write_metric("COMPLETED", state)


from dataset import load_and_format_dataset

def parse_args():
    parser = argparse.ArgumentParser(description="Maieutic SFT Training")
    parser.add_argument("--smoke-test", action="store_true", help="Run 10 steps for testing")
    parser.add_argument("--full-run", action="store_true", help="Run full training based on YAML")
    return parser.parse_args()

def main():
    args = parse_args()
    
    if not args.smoke_test and not args.full_run:
        print("Warning: Neither --smoke-test nor --full-run specified. Defaulting to --smoke-test.")
        args.smoke_test = True

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
        chat_template = "qwen-3",
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
    dataset_paths = [os.path.join(os.path.dirname(__file__), p) for p in dataset_paths if os.path.exists(os.path.join(os.path.dirname(__file__), p))]
    
    if not dataset_paths:
        print("Warning: No valid dataset paths found! (Mocking data for smoke test purposes only)")
        # If no dataset, we will just pass in empty to let the trainer fail or warn.
        
    dataset = load_and_format_dataset(dataset_paths, tokenizer=tokenizer)
    
    # Split for eval
    dataset = dataset.train_test_split(test_size=0.05)
    train_dataset = dataset["train"]
    eval_dataset = dataset["test"]

    # Configure overrides based on run mode
    max_steps = 10 if args.smoke_test else config.get("max_steps", -1)
    num_train_epochs = 1 if args.full_run and max_steps == -1 else config.get("num_train_epochs", 1)
    
    report_to = "wandb" if (args.full_run and "WANDB_API_KEY" in os.environ) else "none"

    from completion_collator import DataCollatorForCompletionOnlyLM
    response_template = "<|im_start|>assistant\n"
    collator = DataCollatorForCompletionOnlyLM(response_template, tokenizer=tokenizer)

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
        data_collator = collator,
        args = TrainingArguments(
            per_device_train_batch_size = config["per_device_train_batch_size"],
            gradient_accumulation_steps = config["gradient_accumulation_steps"],
            warmup_ratio = config["warmup_ratio"],
            max_steps = max_steps,
            num_train_epochs = num_train_epochs if max_steps == -1 else 0.0,
            learning_rate = float(config["learning_rate"]),
            fp16 = not torch.cuda.is_bf16_supported(),
            bf16 = torch.cuda.is_bf16_supported(),
            logging_steps = config["logging_steps"],
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = config["lr_scheduler_type"],
            seed = 3407,
            output_dir = config["output_dir"],
            report_to = report_to,
            save_steps = config["save_steps"]
        ),
        callbacks=[MonitorCallback()],
    )

    print(f"Starting training ({'SMOKE TEST' if args.smoke_test else 'FULL RUN'})...")
    trainer_stats = trainer.train()

    print(f"Saving final adapter to {config['output_dir']}...")
    model.save_pretrained(config["output_dir"])
    tokenizer.save_pretrained(config["output_dir"])

    if args.full_run and os.environ.get("HF_TOKEN") and config.get("push_to_hub"):
        print(f"Pushing to Hub: {config['push_to_hub']}...")
        model.push_to_hub(config["push_to_hub"])
        tokenizer.push_to_hub(config["push_to_hub"])

if __name__ == "__main__":
    main()
