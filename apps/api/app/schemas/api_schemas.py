from pydantic import BaseModel
from typing import Optional, Any, Dict

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

class ChatResponse(BaseModel):
    type: str # correct, incorrect, incomplete, off_topic, completed, new_plan, error
    message: Optional[str] = None
    next_checkpoint: Optional[Dict[str, Any]] = None
    hint: Optional[Dict[str, Any]] = None
    verification: Optional[Dict[str, Any]] = None
