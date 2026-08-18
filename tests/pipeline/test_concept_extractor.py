import pytest
from training.pipeline.concept_extractor import HeuristicConceptExtractor
from training.pipeline.schemas import ProcessedSample, Chunk

def test_heuristic_concept_extractor():
    extractor = HeuristicConceptExtractor()
    
    sample = ProcessedSample(
        sample_id="test_concepts",
        source="test",
        domain="cs",
        messages=[],
        chunks=[
            Chunk(
                chunk_id="c1",
                text="We are discussing binary search and time complexity.",
                role="user",
                start_offset=0,
                end_offset=50,
                section="Binary Search Algorithm"
            )
        ]
    )
    
    concepts = extractor.extract(sample)
    
    assert len(concepts) > 0
    names = [c.name for c in concepts]
    assert "binary search" in names
    assert "time complexity" in names
    assert "binary search algorithm" in names
    
    for c in concepts:
        assert c.confidence > 0
        assert "c1" in c.chunk_ids
