import torch
from unsloth import FastLanguageModel

def main():
    print("Loading model and adapter from outputs/experiment_02_real_socratic_data...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = "/workspace/Maieutic/outputs/experiment_02_real_socratic_data",
        max_seq_length = 2048,
        dtype = None,
        load_in_4bit = True,
    )
    
    FastLanguageModel.for_inference(model)

    # ChatML template is baked into the saved tokenizer
    messages = [
        {"role": "system", "content": "You are MentorAI, an expert Socratic tutor."},
        {"role": "user", "content": "I'm having trouble understanding how a linked list works."},
    ]
    
    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to("cuda")

    print("\nRunning inference test...")
    outputs = model.generate(input_ids=inputs, max_new_tokens=256, use_cache=True, temperature=0.7, top_p=0.9)
    response = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    
    print("\n--- RESPONSE ---")
    print(response)
    print("----------------\n")
    print("Sanity check passed!")

if __name__ == "__main__":
    main()
