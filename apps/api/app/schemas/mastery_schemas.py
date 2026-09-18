from pydantic import BaseModel, Field
from typing import List, Dict

class ConceptMasteryState(BaseModel):
    concept_id: str
    historical_mastery: float = 0.0
    attempts: int = 0
    misconceptions_observed: List[str] = []
    evidence_history: List[float] = []

class StudentProfile(BaseModel):
    student_id: str
    mastery_by_concept: Dict[str, ConceptMasteryState] = Field(default_factory=dict)
