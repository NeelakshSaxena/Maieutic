import torch
from transformers import DataCollatorForLanguageModeling
import warnings

class DataCollatorForCompletionOnlyLM(DataCollatorForLanguageModeling):
    """
    Role-aware completion collator for ChatML formatted datasets.
    
    LOSS BOUNDARY DECISION:
    - We want the model to learn to generate the assistant's response AND the stop token `<|im_end|>`.
    - During inference, the prompt ends with `<|im_start|>assistant\n`, so the model never generates these tokens. Thus, they are MASKED.
    - The `\n` after `<|im_end|>` is also MASKED since it's structural padding.
    - All `system` and `user` content and their control tokens are MASKED.
    
    Supervised (LOSS computed): 
      - The actual assistant response text.
      - The closing `<|im_end|>` token.
      
    Masked (-100):
      - `<|im_start|>`
      - `system`, `user`, `assistant` role tokens
      - The `\n` following the role token
      - The text content of `system` and `user` turns
      - The closing `<|im_end|>` for `system` and `user` turns
      - Any `\n` outside the assistant's content block.
    """
    def __init__(self, response_template, tokenizer, *args, mlm=False, ignore_index=-100, **kwargs):
        super().__init__(tokenizer, *args, mlm=mlm, **kwargs)
        self.ignore_index = ignore_index
        
        # Determine token IDs for Qwen3 ChatML
        self.im_start_id = tokenizer.encode("<|im_start|>", add_special_tokens=False)[0]
        self.im_end_id = tokenizer.encode("<|im_end|>", add_special_tokens=False)[0]
        self.assistant_id = tokenizer.encode("assistant", add_special_tokens=False)[0]
        self.nl_id = tokenizer.encode("\n", add_special_tokens=False)[0]

    def torch_call(self, examples):
        batch = super().torch_call(examples)
        
        for i in range(len(batch["input_ids"])):
            input_ids = batch["input_ids"][i].tolist()
            labels = input_ids.copy()
            
            # Start by masking everything
            for j in range(len(labels)):
                labels[j] = self.ignore_index
                
            in_assistant = False
            
            j = 0
            while j < len(input_ids):
                # Detect start of a turn
                if input_ids[j] == self.im_start_id:
                    # Look ahead to see if it's the assistant
                    if j + 2 < len(input_ids) and input_ids[j+1] == self.assistant_id and input_ids[j+2] == self.nl_id:
                        in_assistant = True
                        j += 3 # skip <|im_start|>assistant\n
                        continue
                    else:
                        in_assistant = False
                
                # If we hit an im_end, we unmask it if we were in assistant, then leave assistant mode
                if input_ids[j] == self.im_end_id:
                    if in_assistant:
                        labels[j] = input_ids[j]
                    in_assistant = False
                    j += 1
                    continue
                    
                if in_assistant:
                    labels[j] = input_ids[j]
                    
                j += 1
                
            batch["labels"][i] = torch.tensor(labels, dtype=torch.int64)
            
            # Sanity check: If no assistant tokens were found, warn
            if all(lbl == self.ignore_index for lbl in labels):
                warnings.warn("Could not find any assistant turns in sequence. Ignoring loss.")
                
        return batch
