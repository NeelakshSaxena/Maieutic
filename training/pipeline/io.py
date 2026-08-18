import json
import os
from typing import Iterator, Iterable
from datasets import Dataset

def load_jsonl(file_path: str) -> Iterator[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def save_jsonl(data: Iterable[dict], file_path: str, append: bool = False):
    mode = "a" if append else "w"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, mode, encoding="utf-8") as f:
        for record in data:
            f.write(json.dumps(record) + "\n")

def to_huggingface(jsonl_path: str) -> Dataset:
    return Dataset.from_json(jsonl_path)
