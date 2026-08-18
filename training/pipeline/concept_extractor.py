from abc import ABC, abstractmethod
from typing import List
from .schemas import ProcessedSample, Concept

class ConceptExtractor(ABC):
    @abstractmethod
    def extract(self, sample: ProcessedSample) -> List[Concept]:
        pass

class HeuristicConceptExtractor(ConceptExtractor):
    def __init__(self):
        # A simple dictionary-based lookup for basic technical concepts
        self.dictionary = {
            # Algorithms & Data Structures
            "binary search": "algorithm", "quick sort": "algorithm", "merge sort": "algorithm",
            "hash table": "data_structure", "array": "data_structure", "linked list": "data_structure",
            "binary tree": "data_structure", "graph": "data_structure", "stack": "data_structure",
            "queue": "data_structure", "dictionary": "data_structure", "list": "data_structure",
            # Programming Concepts
            "recursion": "programming_concept", "dynamic programming": "algorithm_paradigm",
            "time complexity": "theory", "space complexity": "theory", "o(log n)": "theory",
            "for loop": "programming_construct", "while loop": "programming_construct",
            "variable": "programming_construct", "function": "programming_construct",
            "class": "programming_construct", "object": "programming_construct",
            "inheritance": "programming_concept", "polymorphism": "programming_concept",
            "api": "concept", "json": "format", "http": "protocol", "database": "concept",
            "sql": "language", "nosql": "language", "html": "language", "css": "language",
            "javascript": "language", "python": "language", "react": "framework", "node.js": "framework",
            "machine learning": "concept", "neural network": "concept", "deep learning": "concept",
            # Math Concepts
            "algebra": "math", "calculus": "math", "geometry": "math", "probability": "math",
            "statistics": "math", "derivative": "math", "integral": "math", "matrix": "math",
            "vector": "math", "equation": "math", "fraction": "math", "theorem": "math"
        }
        
    def extract(self, sample: ProcessedSample) -> List[Concept]:
        concepts = []
        concept_id_counter = 1
        
        found_concepts = {}
        
        for chunk in sample.chunks:
            text_lower = chunk.text.lower()
            
            # Dictionary extraction
            for term, term_type in self.dictionary.items():
                if term in text_lower:
                    if term not in found_concepts:
                        found_concepts[term] = {
                            "name": term,
                            "type": term_type,
                            "chunk_ids": [],
                            "confidence": 0.90,
                            "source": "heuristic_dictionary"
                        }
                    if chunk.chunk_id not in found_concepts[term]["chunk_ids"]:
                        found_concepts[term]["chunk_ids"].append(chunk.chunk_id)
                        
            # Structural heading extraction
            if chunk.section:
                heading = chunk.section.lower().strip()
                if heading and len(heading) < 50:
                    if heading not in found_concepts:
                        found_concepts[heading] = {
                            "name": heading,
                            "type": "structural_heading",
                            "chunk_ids": [],
                            "confidence": 0.70,
                            "source": "heuristic_heading"
                        }
                    if chunk.chunk_id not in found_concepts[heading]["chunk_ids"]:
                        found_concepts[heading]["chunk_ids"].append(chunk.chunk_id)

        for term, data in found_concepts.items():
            concept = Concept(
                concept_id=f"{sample.sample_id}_concept_{concept_id_counter:03d}",
                name=data["name"],
                type=data["type"],
                description=f"Extracted from {data['source']}",
                chunk_ids=data["chunk_ids"],
                confidence=data["confidence"],
                source=data["source"]
            )
            concepts.append(concept)
            concept_id_counter += 1
            
        return concepts
