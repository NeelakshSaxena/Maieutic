import pytest
from training.pipeline.metadata import add_chunk_metadata
from training.pipeline.schemas import ProcessedSample, Chunk

def test_add_chunk_metadata():
    sample = ProcessedSample(
        sample_id="test_meta",
        source="test",
        domain="cs",
        messages=[],
        chunks=[
            Chunk(
                chunk_id="c1",
                text="This is a simple text with exactly ten words in it.",
                role="user",
                start_offset=0,
                end_offset=51
            ),
            Chunk(
                chunk_id="c2",
                text="```python\nprint('hello')\n```",
                role="assistant",
                start_offset=51,
                end_offset=80
            )
        ]
    )
    
    add_chunk_metadata(sample)
    
    assert sample.chunks[0].metadata["contains_code"] == False
    assert sample.chunks[0].metadata["contains_math"] == False
    assert sample.chunks[0].metadata["word_count"] == 11
    assert sample.chunks[0].language == "en"
    
    assert sample.chunks[1].metadata["contains_code"] == True
    assert sample.chunks[1].language == "python"
