import os
from transformers import AutoTokenizer
from unsloth.chat_templates import get_chat_template

def main():
    print("--- Qwen3 Chat Template & Reasoning Tag Analysis ---")
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
    
    print("\n1. Raw Tokenizer Default Chat Template:")
    print(tokenizer.chat_template)
    
    # Test get_chat_template from unsloth
    tokenizer_unsloth = get_chat_template(tokenizer, chat_template="qwen-3")
    
    print("\n2. Unsloth Patched 'qwen-3' Chat Template:")
    print(tokenizer_unsloth.chat_template)
    
    messages = [
        {"role": "system", "content": "You are MentorAI, an expert Socratic tutor."},
        {"role": "user", "content": "How do I implement binary search?"},
        {"role": "assistant", "content": "Let's break this down into steps. What is the first step when searching a sorted array?"}
    ]
    
    formatted_train = tokenizer_unsloth.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    formatted_infer = tokenizer_unsloth.apply_chat_template(messages[:2], tokenize=False, add_generation_prompt=True)
    
    print("\n3. Formatted Training String (add_generation_prompt=False):")
    print(repr(formatted_train))
    
    print("\n4. Formatted Inference String (add_generation_prompt=True):")
    print(repr(formatted_infer))

if __name__ == "__main__":
    main()
