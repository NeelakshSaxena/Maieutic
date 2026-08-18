from typing import Iterator
from datasets import load_from_disk
from .schemas import ProcessedSample, Message

def parse_hf_dataset(dataset_path: str) -> Iterator[ProcessedSample]:
    """
    Reads a normalized HuggingFace dataset from Phase 0 and yields ProcessedSample objects.
    Phase 0 schema had: id, source_dataset, domain, messages, metadata.
    """
    dataset = load_from_disk(dataset_path)
    
    for row in dataset:
        messages = [
            Message(role=msg["role"], content=msg["content"])
            for msg in row.get("messages", [])
        ]
        
        sample = ProcessedSample(
            sample_id=row["id"],
            source=row["source_dataset"],
            domain=row["domain"],
            messages=messages,
            chunks=[],
            concepts=[],
            relationships=[],
            pipeline_metadata=None
        )
        yield sample
