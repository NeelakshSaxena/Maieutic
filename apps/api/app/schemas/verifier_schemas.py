from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import List

class VerificationStatus(str, Enum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    INCOMPLETE = "incomplete"
    OFF_TOPIC = "off_topic"

class CriterionEvaluation(BaseModel):
    criterion: str
    met: bool
    evidence: str

class Misconception(BaseModel):
    name: str
    description: str
    evidence: str

class VerificationResult(BaseModel):
    is_correct: bool
    status: VerificationStatus
    criteria_evaluation: List[CriterionEvaluation]
    misconceptions: List[Misconception]
    mastery_score: float = Field(ge=0.0, le=1.0)
    explanation: str

    @model_validator(mode="after")
    def validate_consistency(self):
        if self.is_correct != (self.status == VerificationStatus.CORRECT):
            raise ValueError(
                "is_correct must be True exactly when status is VerificationStatus.CORRECT"
            )
        return self
