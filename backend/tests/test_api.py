from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest
from main import app

client = TestClient(app)

# Mock responses
MOCK_PROJECTS = [
    {"id": "1", "key": "PROJ1", "name": "Project 1"},
    {"id": "2", "key": "PROJ2", "name": "Project 2"}
]

MOCK_TRANSCRIPT = "This is a test transcript"

MOCK_PARSED_COMMAND = {
    "action_type": "create",
    "project_key": "PROJ1",
    "summary": "Test task",
    "description": "Test description"
}

MOCK_EXECUTION_RESULT = {
    "success": True,
    "issue_key": "PROJ1-123"
}

@pytest.fixture
def mock_deepgram():
    with patch('main.transcription_service') as mock:
        mock.transcribe.return_value = MOCK_TRANSCRIPT
        yield mock

@pytest.fixture
def mock_openai():
    with patch('main.command_parser') as mock:
        mock.parse_command.return_value = MOCK_PARSED_COMMAND
        yield mock

@pytest.fixture
def mock_jira():
    with patch('main.jira_client') as mock:
        mock.execute_action.return_value = MOCK_EXECUTION_RESULT
        mock.get_projects.return_value = MOCK_PROJECTS
        yield mock

def test_transcribe_endpoint(mock_deepgram):
    # Create a mock audio file
    audio_content = b"mock audio content"
    files = {"file": ("test.wav", audio_content, "audio/wav")}
    
    response = client.post("/api/transcribe", files=files)
    
    assert response.status_code == 200
    assert response.json() == {"transcript": MOCK_TRANSCRIPT}
    mock_deepgram.transcribe.assert_called_once()

def test_parse_command_endpoint(mock_openai):
    response = client.post(
        "/api/parse-command",
        json={"transcript": MOCK_TRANSCRIPT, "project_key": "PROJ1"}
    )
    
    assert response.status_code == 200
    assert response.json() == MOCK_PARSED_COMMAND
    mock_openai.parse_command.assert_called_once_with(MOCK_TRANSCRIPT, "PROJ1")

def test_execute_action_endpoint(mock_jira):
    response = client.post(
        "/api/execute-action",
        json=MOCK_PARSED_COMMAND
    )
    
    assert response.status_code == 200
    assert response.json() == MOCK_EXECUTION_RESULT
    mock_jira.execute_action.assert_called_once_with(MOCK_PARSED_COMMAND)

def test_get_projects_endpoint(mock_jira):
    response = client.get("/api/jira/projects")
    
    assert response.status_code == 200
    assert response.json() == MOCK_PROJECTS
    mock_jira.get_projects.assert_called_once()

def test_transcribe_endpoint_error(mock_deepgram):
    mock_deepgram.transcribe.side_effect = Exception("Transcription failed")
    
    audio_content = b"mock audio content"
    files = {"file": ("test.wav", audio_content, "audio/wav")}
    
    response = client.post("/api/transcribe", files=files)
    
    assert response.status_code == 500
    assert "Transcription failed" in response.json()["detail"]

def test_parse_command_endpoint_error(mock_openai):
    mock_openai.parse_command.side_effect = Exception("Parsing failed")
    
    response = client.post(
        "/api/parse-command",
        json={"transcript": MOCK_TRANSCRIPT, "project_key": "PROJ1"}
    )
    
    assert response.status_code == 500
    assert "Parsing failed" in response.json()["detail"]

def test_execute_action_endpoint_error(mock_jira):
    mock_jira.execute_action.side_effect = Exception("Execution failed")
    
    response = client.post(
        "/api/execute-action",
        json=MOCK_PARSED_COMMAND
    )
    
    assert response.status_code == 500
    assert "Execution failed" in response.json()["detail"]

def test_get_projects_endpoint_error(mock_jira):
    mock_jira.get_projects.side_effect = Exception("Failed to fetch projects")
    
    response = client.get("/api/jira/projects")
    
    assert response.status_code == 500
    assert "Failed to fetch projects" in response.json()["detail"] 