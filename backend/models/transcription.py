from pydantic import BaseModel
from typing import Optional, List

class TranscriptionResponse(BaseModel):
    text: str
    confidence: float
    language: str

class TranscriptionRequest(BaseModel):
    language: str = "en"
    model: str = "nova"
    encoding: Optional[str] = None
    sample_rate: Optional[int] = None

class TranscriptionResult(BaseModel):
    transcript: str
    confidence: float
    words: Optional[List[dict]] = None
    timestamps: Optional[List[dict]] = None

class StreamingTranscriptionResponse(BaseModel):
    is_final: bool
    channel: TranscriptionResult 