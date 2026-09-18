from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
print("Vocab size:", len(tokenizer))
for text in ["<|im_start|>", "<|im_end|>", "system", "user", "assistant", "\n", "<|im_start|>assistant\n"]:
    ids = tokenizer.encode(text, add_special_tokens=False)
    decoded = [tokenizer.decode([i]) for i in ids]
    print(f"'{text}' -> {ids} -> {decoded}")

text2 = "<|im_start|>system\nSys<|im_end|>\n<|im_start|>user\nUser<|im_end|>\n<|im_start|>assistant\nAsst<|im_end|>\n"
ids2 = tokenizer.encode(text2, add_special_tokens=False)
print(f"Full text -> {ids2}")
for idx in ids2:
    print(f"{idx}: '{tokenizer.decode([idx])}'")
