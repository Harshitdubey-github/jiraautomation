from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from ..services.command_service import CommandService
from ..auth.jwt_bearer import JWTBearer

router = APIRouter()
jwt_bearer = JWTBearer()

class CommandRequest(BaseModel):
    text: str
    project_key: Optional[str] = None
    context: Optional[dict] = None

class CommandResponse(BaseModel):
    action: str
    details: dict
    confidence: float

class TranscriptParseRequest(BaseModel):
    transcript: str
    project_key: Optional[str] = None

class TranscriptParseResponse(BaseModel):
    actions: List[CommandResponse]

@router.post("/parse", response_model=CommandResponse)
async def parse_command(
    request: CommandRequest,
    token: str = Depends(jwt_bearer)
):
    """
    Parse a command from transcribed text
    """
    try:
        command_service = CommandService(token)
        result = await command_service.parse_command(
            request.text,
            request.project_key,
            request.context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
async def execute_command(
    command: CommandResponse,
    token: str = Depends(jwt_bearer)
):
    """
    Execute a parsed command
    """
    try:
        command_service = CommandService(token)
        result = await command_service.execute_command(command)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parse/transcript", response_model=TranscriptParseResponse)
async def parse_transcript(
    request: TranscriptParseRequest,
    token: str = Depends(jwt_bearer)
):
    """
    Parse a Teams meeting transcript for actions
    """
    try:
        command_service = CommandService(token)
        result = await command_service.parse_transcript(
            request.transcript,
            request.project_key
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 