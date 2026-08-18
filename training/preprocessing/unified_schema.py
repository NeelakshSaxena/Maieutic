from pydantic import BaseModel, Field
from typing import List, Optional, Literal

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

class UnifiedSchema(BaseModel):
    id: str
    source_dataset: str
    domain: str
    messages: List[Message]
    metadata: Metadata
