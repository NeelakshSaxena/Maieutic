import pytest
from datasets import Dataset
from training.pipeline.schemas import ProcessedSample
from training.pipeline.parser import parse_hf_dataset

def test_parse_hf_dataset(tmp_path):
    mock_data = {
        "id": ["mock_1"],
        "source_dataset": ["test_source"],
        "domain": ["test_domain"],
        "messages": [
            [
                {"role": "user", "content": "What is binary search?"},
                {"role": "assistant", "content": "It's a search algorithm."}
            ]
        ],
        "metadata": [
            {
                "language": "en",
                "has_reasoning": False,
                "has_final_answer": True,
                "is_verified": False
            }
        ]
    }
    
    dataset = Dataset.from_dict(mock_data)
    dataset_path = str(tmp_path / "mock_dataset")
    dataset.save_to_disk(dataset_path)
    
    samples = list(parse_hf_dataset(dataset_path))
    
    assert len(samples) == 1
    sample = samples[0]
    
    assert isinstance(sample, ProcessedSample)
    assert sample.sample_id == "mock_1"
    assert sample.source == "test_source"
    assert sample.domain == "test_domain"
    assert len(sample.messages) == 2
    assert sample.messages[0].role == "user"
    assert sample.messages[0].content == "What is binary search?"
    assert sample.chunks == []
    
    dumped = sample.model_dump()
    assert dumped["sample_id"] == "mock_1"
