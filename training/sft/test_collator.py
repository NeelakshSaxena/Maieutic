from transformers import AutoTokenizer
from completion_collator import DataCollatorForCompletionOnlyLM

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
collator = DataCollatorForCompletionOnlyLM("", tokenizer=tokenizer)

def run_test(name, text):
    print(f"\n--- Test: {name} ---")
    tokenized = tokenizer(text)
    batch = collator.torch_call([tokenized])
    labels = batch["labels"][0].tolist()
    input_ids = batch["input_ids"][0].tolist()
    
    supervised_tokens = [i for i, l in zip(input_ids, labels) if l != -100]
    supervised_text = tokenizer.decode(supervised_tokens)
    
    print(f"Supervised Tokens: {len(supervised_tokens)}")
    print(f"Supervised Text: {repr(supervised_text)}")
    
    assert "system" not in supervised_text, "FAILED: 'system' found in supervised text"
    assert "System" not in supervised_text, "FAILED: 'System' found in supervised text"
    assert "user" not in supervised_text, "FAILED: 'user' found in supervised text"
    assert "User" not in supervised_text, "FAILED: 'User' found in supervised text"
    
    return supervised_text

# 1. Single assistant turn
text1 = "<|im_start|>assistant\nAsst1<|im_end|>\n"
out1 = run_test("Single assistant turn", text1)
assert "Asst1" in out1

# 2. Two assistant turns
text2 = "<|im_start|>assistant\nAsst1<|im_end|>\n<|im_start|>assistant\nAsst2<|im_end|>\n"
out2 = run_test("Two assistant turns", text2)
assert "Asst1" in out2 and "Asst2" in out2

# 3. Three assistant turns with user turns between them.
text3 = "<|im_start|>assistant\nAsst1<|im_end|>\n<|im_start|>user\nUser1<|im_end|>\n<|im_start|>assistant\nAsst2<|im_end|>\n<|im_start|>user\nUser2<|im_end|>\n<|im_start|>assistant\nAsst3<|im_end|>\n"
out3 = run_test("Three assistant turns with user turns", text3)
assert "Asst1" in out3 and "Asst2" in out3 and "Asst3" in out3

# 4. System + user + assistant.
text4 = "<|im_start|>system\nSystem text here<|im_end|>\n<|im_start|>user\nUser text here<|im_end|>\n<|im_start|>assistant\nAsst text here<|im_end|>\n"
out4 = run_test("System + user + assistant", text4)
assert "Asst text here" in out4

# 5. Empty system/user content
text5 = "<|im_start|>system\n<|im_end|>\n<|im_start|>user\n<|im_end|>\n<|im_start|>assistant\nAsst text here<|im_end|>\n"
out5 = run_test("Empty system/user content", text5)
assert "Asst text here" in out5

print("\nALL TESTS PASSED!")
