from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, List
import os
from ..services.transcription import TranscriptionService
from ..services.command_parser import CommandParser, JiraAction
from ..services.jira_client import JiraClient

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize services
transcription_service = TranscriptionService()
command_parser = CommandParser()
jira_client = JiraClient()

@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str = "en-US"
):
    """
    Transcribe uploaded audio file
    """
    try:
        audio_data = await audio_file.read()
        transcript = await transcription_service.transcribe_audio(audio_data, language)
        return {"transcript": transcript}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse-command")
async def parse_command(
    transcript: str,
    project_key: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """
    Parse transcribed command into Jira action
    """
    try:
        action = await command_parser.parse_command(transcript, project_key)
        return {"action": action.dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/process-teams-transcript")
async def process_teams_transcript(
    transcript: str,
    project_key: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """
    Process Teams meeting transcript and extract Jira actions
    """
    try:
        cleaned_transcript = await transcription_service.process_teams_transcript(transcript)
        actions = await command_parser.parse_teams_transcript(cleaned_transcript, project_key)
        return {"actions": [action.dict() for action in actions]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/execute-action")
async def execute_action(
    action: JiraAction,
    token: str = Depends(oauth2_scheme)
):
    """
    Execute a parsed Jira action
    """
    try:
        result = await jira_client.execute_action(action)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects")
async def get_projects(token: str = Depends(oauth2_scheme)):
    """
    Get list of accessible Jira projects
    """
    try:
        projects = await jira_client.get_projects()
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_issues(
    jql: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Search Jira issues using JQL
    """
    try:
        issues = await jira_client.search_issues(jql)
        return {"issues": issues}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 