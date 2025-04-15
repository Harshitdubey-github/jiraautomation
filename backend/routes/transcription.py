from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
import os
import asyncio
from deepgram import Deepgram
from services.supabase import get_supabase_client

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize Deepgram client
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
deepgram = Deepgram(DEEPGRAM_API_KEY)

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme)
):
    """
    Transcribe audio file using Deepgram
    """
    try:
        # Verify user is authenticated
        supabase = get_supabase_client()
        user = supabase.auth.get_user(token)
        
        # Read audio file
        audio_data = await file.read()
        
        # Configure transcription options
        source = {"buffer": audio_data, "mimetype": file.content_type}
        options = {
            "smart_format": True,
            "model": "nova",
            "language": "en-US"
        }
        
        # Send to Deepgram for transcription
        response = await deepgram.transcription.prerecorded(source, options)
        
        # Extract transcription text
        transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
        
        return {
            "transcript": transcript,
            "confidence": response["results"]["channels"][0]["alternatives"][0]["confidence"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription error: {str(e)}"
        )

@router.post("/parse-teams-transcript")
async def parse_teams_transcript(
    transcript: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Parse Teams meeting transcript to extract action items
    """
    try:
        # Verify user is authenticated
        supabase = get_supabase_client()
        user = supabase.auth.get_user(token)
        
        # TODO: Implement OpenAI integration for parsing Teams transcripts
        # For now, return a mock response
        return {
            "action_items": [
                {
                    "text": "Follow up with the team about the project timeline",
                    "assignee": "John Doe",
                    "due_date": "2024-03-20"
                }
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcript parsing error: {str(e)}"
        ) 