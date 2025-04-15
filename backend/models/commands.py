from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CommandResponse(BaseModel):
    action: str
    details: Dict[str, Any]
    confidence: float

class CommandRequest(BaseModel):
    text: str
    project_key: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class TranscriptParseRequest(BaseModel):
    transcript: str
    project_key: Optional[str] = None

class TranscriptParseResponse(BaseModel):
    actions: List[CommandResponse]

class CommandExecutionResult(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None 