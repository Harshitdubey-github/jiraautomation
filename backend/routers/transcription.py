from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import Optional
from pydantic import BaseModel
from ..services.transcription_service import TranscriptionService
from ..auth.jwt_bearer import JWTBearer

router = APIRouter()
jwt_bearer = JWTBearer()

class TranscriptionResponse(BaseModel):
    text: str
    confidence: float
    language: str

@router.post("/audio", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = "en",
    token: str = Depends(jwt_bearer)
):
    """
    Transcribe audio file using Deepgram
    """
    try:
        if not file.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=400,
                detail="File must be an audio file"
            )

        transcription_service = TranscriptionService()
        result = await transcription_service.transcribe(file, language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def transcribe_stream(
    audio_chunk: bytes,
    language: Optional[str] = "en",
    token: str = Depends(jwt_bearer)
):
    """
    Transcribe streaming audio data
    """
    try:
        transcription_service = TranscriptionService()
        result = await transcription_service.transcribe_stream(audio_chunk, language)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 