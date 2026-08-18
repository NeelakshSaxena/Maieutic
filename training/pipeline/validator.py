from typing import Dict, Any
from .schemas import ProcessedSample
from pydantic import ValidationError

class PipelineValidator:
    def validate(self, record: ProcessedSample) -> bool:
        try:
            # Re-validate against Pydantic schema
            dump = record.model_dump()
            ProcessedSample.model_validate(dump)
            
            # Additional constraint checks
            if not record.sample_id:
                return False
                
            # If there are messages, there should generally be chunks, but maybe not if messages are empty.
            if record.messages and not record.chunks:
                # If there was textual content, chunker should have produced chunks
                if any(m.content.strip() for m in record.messages):
                    return False
                    
            return True
        except ValidationError:
            return False
