import pytest
from training.pipeline.kg_generator import RelationshipGenerator
from training.pipeline.schemas import ProcessedSample, Chunk, Concept

def test_relationship_generator():
    generator = RelationshipGenerator()
    
    sample = ProcessedSample(
        sample_id="test_rels",
        source="test",
        domain="cs",
        messages=[],
        chunks=[
            Chunk(
                chunk_id="c1",
                text="binary search requires an array that is sorted.",
                role="user",
                start_offset=0,
                end_offset=50,
            )
        ],
        concepts=[
            Concept(concept_id="c_1", name="binary search", type="algorithm", chunk_ids=["c1"], confidence=1.0, source="test"),
            Concept(concept_id="c_2", name="array", type="data_structure", chunk_ids=["c1"], confidence=1.0, source="test"),
        ]
    )
    
    rels = generator.generate(sample)
    
    assert len(rels) >= 1
    # Check ontology relation
    assert any(r.source_concept_id == "c_1" and r.target_concept_id == "c_2" and r.relation == "prerequisite" for r in rels)
    # Check pattern relation: binary search requires an array
    assert any(r.source_concept_id == "c_1" and r.target_concept_id == "c_2" and r.relation == "depends_on" for r in rels)
