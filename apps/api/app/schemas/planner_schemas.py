from pydantic import BaseModel
from typing import List

class Concept(BaseModel):
    id: str
    name: str
    description: str

class Dependency(BaseModel):
    prerequisite_id: str
    concept_id: str

class Checkpoint(BaseModel):
    id: str
    concept_id: str
    task: str
    success_criteria: str

class LearningPlan(BaseModel):
    learning_objectives: str
    concepts: List[Concept]
    dependencies: List[Dependency]
    checkpoints: List[Checkpoint]
