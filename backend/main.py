from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import uvicorn
from typing import Optional, List
from .services.transcription_service import TranscriptionService
from .services.command_parser import CommandParser, JiraAction
from .services.jira_client import JiraClient

# Load environment variables
load_dotenv()

# Import routers
from routes import auth, transcription, commands, jira

app = FastAPI(
    title="Jira Voice Assistant API",
    description="API for the Jira Voice Assistant application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize services
transcription_service = TranscriptionService()
command_parser = CommandParser()
jira_client = JiraClient()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(transcription.router, prefix="/api/transcribe", tags=["Transcription"])
app.include_router(commands.router, prefix="/api/commands", tags=["Commands"])
app.include_router(jira.router, prefix="/api/jira", tags=["Jira"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Jira Voice Assistant API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = "en-US"
):
    """
    Transcribe uploaded audio file
    """
    try:
        audio_data = await file.read()
        transcript = await transcription_service.transcribe_audio(audio_data, language)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/parse-command")
async def parse_command(
    transcript: str,
    project_key: Optional[str] = None
):
    """
    Parse transcribed text into Jira action
    """
    try:
        action = await command_parser.parse_command(transcript, project_key)
        return action.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/execute-action")
async def execute_action(action: JiraAction):
    """
    Execute parsed Jira action
    """
    try:
        result = await jira_client.execute_action(action)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jira/projects")
async def get_projects():
    """
    Get list of accessible Jira projects
    """
    try:
        projects = await jira_client.list_projects()
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/supported-languages")
async def get_supported_languages():
    """
    Get list of supported languages for transcription
    """
    return transcription_service.get_supported_languages()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 