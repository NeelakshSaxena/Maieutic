import os
import argparse
from datetime import datetime
from training.pipeline.parser import parse_hf_dataset
from training.pipeline.chunker import MarkdownChunker
from training.pipeline.metadata import add_chunk_metadata
from training.pipeline.concept_extractor import HeuristicConceptExtractor
from training.pipeline.kg_generator import RelationshipGenerator
from training.pipeline.validator import PipelineValidator
from training.pipeline.io import save_jsonl
from training.pipeline.schemas import PipelineMetadata

def main():
    parser = argparse.ArgumentParser(description="Run Phase 1 Data Pipeline")
    parser.add_argument("--input_dataset", type=str, required=True, help="Path to normalized HF dataset")
    parser.add_argument("--output_file", type=str, required=True, help="Path to output JSONL file")
    parser.add_argument("--limit", type=int, default=None, help="Number of samples to process (for testing)")
    args = parser.parse_args()
    
    chunker = MarkdownChunker(max_tokens=512)
    concept_extractor = HeuristicConceptExtractor()
    kg_generator = RelationshipGenerator()
    validator = PipelineValidator()
    
    processed_records = []
    
    total_samples = 0
    valid_samples = 0
    samples_with_concepts = 0
    samples_with_rels = 0
    total_tokens = 0
    total_concepts = 0
    samples_with_multiple_concepts = 0
    
    print(f"Reading dataset from {args.input_dataset}...")
    sample_iterator = parse_hf_dataset(args.input_dataset)
    
    for i, sample in enumerate(sample_iterator):
        if args.limit and i >= args.limit:
            break
            
        total_samples += 1
        
        # 1. Chunker
        chunks = []
        for msg_index, msg in enumerate(sample.messages):
            if msg.content.strip():
                msg_chunks = chunker.chunk_message(msg, sample.sample_id, msg_index)
                chunks.extend(msg_chunks)
        sample.chunks = chunks
        
        # 2. Metadata
        add_chunk_metadata(sample)
        
        # 3. Concept Extraction
        sample.concepts = concept_extractor.extract(sample)
        
        # 4. KG Generation
        sample.relationships = kg_generator.generate(sample)
        
        # Pipeline Metadata
        sample.pipeline_metadata = PipelineMetadata(
            pipeline_version="1.0.0",
            concept_extractor="heuristic-v1",
            chunker="markdown-aware-v1",
            processed_at=datetime.utcnow().isoformat()
        )
        
        # 5. Validation
        if validator.validate(sample):
            valid_samples += 1
            processed_records.append(sample.model_dump())
            
            # Metrics accumulation
            sample_tokens = sum(c.token_count for c in sample.chunks if c.token_count)
            total_tokens += sample_tokens
            
            if sample.concepts:
                samples_with_concepts += 1
                total_concepts += len(sample.concepts)
                if len(sample.concepts) >= 2:
                    samples_with_multiple_concepts += 1
                
            if sample.relationships:
                samples_with_rels += 1
        else:
            print(f"Sample {sample.sample_id} failed validation.")
            
        if len(processed_records) >= 1000:
            save_jsonl(processed_records, args.output_file, append=True)
            processed_records = []
            
    if processed_records:
        save_jsonl(processed_records, args.output_file, append=True)
        
    print("\n--- Pipeline Metrics ---")
    print(f"Total Samples Processed: {total_samples}")
    print(f"Valid Samples (Validity): {valid_samples / max(1, total_samples) * 100:.2f}%")
    print(f"Coverage (% with >=1 concept): {samples_with_concepts / max(1, valid_samples) * 100:.2f}%")
    
    density = (total_concepts / max(1, total_tokens)) * 1000
    print(f"Density (Concepts / 1000 tokens): {density:.2f}")
    
    rel_coverage = 0
    if samples_with_multiple_concepts > 0:
        rel_coverage = (samples_with_rels / samples_with_multiple_concepts) * 100
    print(f"Relationship Coverage: {rel_coverage:.2f}%")
    
    print(f"Output saved to {args.output_file}")

if __name__ == "__main__":
    main()
