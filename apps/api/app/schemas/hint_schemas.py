from enum import Enum
from pydantic import BaseModel, Field

class HintLevel(str, Enum):
    LEVEL_1 = "1"
    LEVEL_2 = "2"
    LEVEL_3 = "3"
    LEVEL_4 = "4"

class HintResult(BaseModel):
    level_used: HintLevel
    hint_text: str = Field(description="The actual hint presented to the student")
    target: str = Field(description="Identifies what specific misconception or missing criterion the hint is trying to address")
    rationale: str = Field(description="Why this hint is appropriate for the student's current state")
    was_answer_revealed: bool = Field(description="Whether the generated hint directly revealed the final answer")
