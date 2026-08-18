from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class Metadata(BaseModel):
    language: str
    subject: Optional[str] = None
    difficulty: Optional[str] = None
    quality_score: Optional[float] = None
    has_reasoning: bool
    has_final_answer: bool
    is_verified: bool
    original_id: Optional[str] = None

class Chunk(BaseModel):
    chunk_id: str
    text: str
    role: Literal["system", "user", "assistant"]
    section: Optional[str] = None
    start_offset: int
    end_offset: int
    token_count: Optional[int] = None
    language: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Concept(BaseModel):
    concept_id: str
    name: str
    type: str
    description: Optional[str] = None
    chunk_ids: List[str] = Field(default_factory=list)
    confidence: float
    source: str

class Relationship(BaseModel):
    source_concept_id: str
    target_concept_id: str
    relation: Literal["prerequisite", "depends_on", "part_of", "related_to", "sequence_before", "example_of", "definition_of", "application_of"]
    confidence: float

class PipelineMetadata(BaseModel):
    pipeline_version: str
    concept_extractor: str
    chunker: str
    processed_at: str

class ProcessedSample(BaseModel):
    sample_id: str
    source: str
    domain: str
    messages: List[Message]
    chunks: List[Chunk] = Field(default_factory=list)
    concepts: List[Concept] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    pipeline_metadata: Optional[PipelineMetadata] = None
