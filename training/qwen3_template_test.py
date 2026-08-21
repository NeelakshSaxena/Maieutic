import torch
from transformers import AutoTokenizer

model_id = "Qwen/Qwen3-8B"

print(f"Loading tokenizer for {model_id}...")
tokenizer = AutoTokenizer.from_pretrained(model_id)

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2+2?"},
    {"role": "assistant", "content": "The answer is 4."}
]

print("\n--- CASE A: enable_thinking=True ---")
try:
    prompt_true = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False, enable_thinking=True)
    print(prompt_true)
except Exception as e:
    print(f"Error: {e}")

print("\n--- CASE B: enable_thinking=False ---")
try:
    prompt_false = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False, enable_thinking=False)
    print(prompt_false)
except Exception as e:
    print(f"Error: {e}")

print("\n--- CASE C: Default (no thinking kwargs) ---")
try:
    prompt_default = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    print(prompt_default)
except Exception as e:
    print(f"Error: {e}")

print("\n--- CASE D: Training formatting with <think> populated ---")
# If we manually include <think> inside assistant role
messages_with_think = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2+2?"},
    {"role": "assistant", "content": "<think>\n2+2 is a basic arithmetic problem.\n</think>\nThe answer is 4."}
]
try:
    prompt_think = tokenizer.apply_chat_template(messages_with_think, tokenize=False, add_generation_prompt=False)
    print(prompt_think)
    
    print("\nToken IDs:")
    tokens = tokenizer(prompt_think, return_tensors="pt")["input_ids"][0]
    for i, token in enumerate(tokens):
        print(f"{token.item()}: {repr(tokenizer.decode([token.item()]))}")
except Exception as e:
    print(f"Error: {e}")

# Try to find unsloth chat template utils if installed to see how loss masking handles <think>
print("\n--- Investigating Assistant-Only Loss Masking ---")
try:
    from trl.trainer.utils import DataCollatorForCompletionOnlyLM
    
    # We want to know if DataCollatorForCompletionOnlyLM masks out <think> tags.
    # Usually it masks everything before the assistant header, but what about the think tags?
    
    response_template = "<|im_start|>assistant\n"
    collator = DataCollatorForCompletionOnlyLM(response_template, tokenizer=tokenizer)
    
    encoded = tokenizer(prompt_think, return_tensors="pt")
    # simulate a batch
    batch = [encoded["input_ids"][0]]
    collated = collator([{"input_ids": batch[0], "attention_mask": encoded["attention_mask"][0]}])
    
    labels = collated["labels"][0]
    
    print("Labels (showing what is trained on):")
    for tok, lab in zip(batch[0], labels):
        if lab.item() == -100:
            print(f"MASKED: {repr(tokenizer.decode([tok.item()]))}")
        else:
            print(f"TRAIN: {repr(tokenizer.decode([tok.item()]))}")
            
except Exception as e:
    print(f"Could not run data collator test: {e}")
