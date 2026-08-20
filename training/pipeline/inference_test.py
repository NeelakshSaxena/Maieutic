import os
from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template

def main():
    # Resolve path relative to script location so it works from anywhere
    adapter_path = os.path.join(os.path.dirname(__file__), "../../outputs/qwen-8b-socratic-v1")
    
    if not os.path.exists(adapter_path):
        print(f"Error: Adapter path {adapter_path} not found. Run the 10-step smoke test first.")
        return
        
    print(f"Loading model with adapter from {adapter_path}...")
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = adapter_path,
        max_seq_length = 4096,
        dtype = None,
        load_in_4bit = True,
    )
    
    tokenizer = get_chat_template(
        tokenizer,
        chat_template = "qwen-3",
    )
    
    FastLanguageModel.for_inference(model)

    messages = [
        {"role": "system", "content": "You are Maieutic, an expert Socratic tutor. You must never give the student the direct answer. Instead, ask guiding questions, provide hints, and help them arrive at the answer themselves."},
        {"role": "user", "content": "How do I implement binary search in python?"}
    ]
    
    print("\nPreparing input...")
    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to("cuda")
    
    print("Generating response...")
    outputs = model.generate(input_ids=inputs, max_new_tokens=256, use_cache=True)
    
    # decode the output
    decoded_output = tokenizer.batch_decode(outputs)
    print("\n--- Model Output ---")
    print(decoded_output[0])
    print("--------------------")

if __name__ == "__main__":
    main()
