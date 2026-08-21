import torch
import warnings
from transformers import DataCollatorForLanguageModeling

class DataCollatorForCompletionOnlyLM(DataCollatorForLanguageModeling):
    def __init__(self, response_template, tokenizer, *args, mlm=False, ignore_index=-100, **kwargs):
        super().__init__(tokenizer, *args, mlm=mlm, **kwargs)
        self.response_template = response_template
        if isinstance(response_template, str):
            self.response_token_ids = self.tokenizer.encode(self.response_template, add_special_tokens=False)
        else:
            self.response_token_ids = response_template
        self.ignore_index = ignore_index

    def torch_call(self, examples):
        batch = super().torch_call(examples)
        
        for i in range(len(batch["input_ids"])):
            input_ids = batch["input_ids"][i].tolist()
            response_token_ids = self.response_token_ids
            
            # Find the start of the response
            match_idx = -1
            for j in range(len(input_ids) - len(response_token_ids) + 1):
                if input_ids[j:j+len(response_token_ids)] == response_token_ids:
                    match_idx = j + len(response_token_ids)
                    break
            
            if match_idx == -1:
                warnings.warn(f"Could not find response template {self.response_template} in sequence. Ignoring loss.")
                batch["labels"][i, :] = self.ignore_index
            else:
                batch["labels"][i, :match_idx] = self.ignore_index
                
        return batch
