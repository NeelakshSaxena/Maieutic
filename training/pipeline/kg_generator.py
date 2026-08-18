from typing import List
from .schemas import ProcessedSample, Relationship, Concept
import re

class RelationshipGenerator:
    def __init__(self):
        # A static ontology of guaranteed relationships
        self.ontology = {
            "binary search": {"array": "prerequisite", "time complexity": "related_to"},
            "quick sort": {"array": "prerequisite", "recursion": "prerequisite"},
            "merge sort": {"array": "prerequisite", "recursion": "prerequisite"},
            "dynamic programming": {"recursion": "prerequisite"},
            "hash table": {"array": "prerequisite"},
            "react": {"javascript": "depends_on", "html": "depends_on"},
            "node.js": {"javascript": "depends_on"},
            "deep learning": {"machine learning": "part_of", "neural network": "depends_on"},
            "calculus": {"algebra": "prerequisite", "geometry": "prerequisite"},
            "derivative": {"calculus": "part_of"},
            "integral": {"calculus": "part_of"},
            "python": {"list": "related_to", "dictionary": "related_to", "function": "part_of", "class": "part_of", "variable": "part_of"},
            "javascript": {"function": "part_of", "variable": "part_of", "object": "related_to", "array": "related_to"},
            "html": {"css": "related_to"},
            "css": {"html": "depends_on"}
        }

    def generate(self, sample: ProcessedSample) -> List[Relationship]:
        relationships = []
        
        # 1. Ontology-based extraction (if both concepts are present)
        concept_names = {c.name: c for c in sample.concepts}
        
        for source_name, source_concept in concept_names.items():
            if source_name in self.ontology:
                for target_name, rel_type in self.ontology[source_name].items():
                    if target_name in concept_names:
                        relationships.append(Relationship(
                            source_concept_id=source_concept.concept_id,
                            target_concept_id=concept_names[target_name].concept_id,
                            relation=rel_type,
                            confidence=0.95
                        ))
                        
        # 2. Pattern-based heuristic extraction across chunks
        # e.g., "X requires Y"
        for chunk in sample.chunks:
            text = chunk.text.lower()
            
            # Find concepts in this chunk
            chunk_concepts = [c for c in sample.concepts if chunk.chunk_id in c.chunk_ids]
            
            for c1 in chunk_concepts:
                for c2 in chunk_concepts:
                    if c1.concept_id == c2.concept_id:
                        continue
                        
                    # Pattern: "[c2] requires [c1]" -> c1 is prerequisite for c2
                    if re.search(rf'{re.escape(c2.name)}\s+(?:requires|needs|depends on)(?:\s+\w+){{0,2}}\s+{re.escape(c1.name)}', text):
                        relationships.append(Relationship(
                            source_concept_id=c2.concept_id,
                            target_concept_id=c1.concept_id,
                            relation="depends_on",
                            confidence=0.85
                        ))

        # Deduplicate relationships
        unique_rels = {}
        for r in relationships:
            key = (r.source_concept_id, r.target_concept_id, r.relation)
            if key not in unique_rels or r.confidence > unique_rels[key].confidence:
                unique_rels[key] = r
                
        return list(unique_rels.values())
