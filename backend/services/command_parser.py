from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import openai
import os
import json

class JiraAction(BaseModel):
    action_type: str  # create, comment, update, search
    project_key: Optional[str] = None
    issue_key: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    comment: Optional[str] = None
    issue_type: Optional[str] = None
    fields: Optional[Dict[str, Any]] = None
    jql: Optional[str] = None

class CommandParser:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing OpenAI API key")
        openai.api_key = self.api_key
        
        self.system_prompt = """You are a command parser for a voice-enabled Jira assistant.
Convert natural language commands into structured Jira actions.
Available actions:
1. create - Create a new issue
2. comment - Add a comment to an issue
3. update - Update an existing issue
4. search - Search for issues using JQL

Example commands and their parsed actions:
"Create a new task in PROJECT-1 called Implement login page"
{
    "action_type": "create",
    "project_key": "PROJECT-1",
    "summary": "Implement login page",
    "issue_type": "Task"
}

"Add a comment to PROJ-123 saying the bug is fixed"
{
    "action_type": "comment",
    "issue_key": "PROJ-123",
    "comment": "The bug is fixed"
}

"Update PROJ-456 status to In Progress"
{
    "action_type": "update",
    "issue_key": "PROJ-456",
    "fields": {"status": "In Progress"}
}

"Find all high priority bugs in PROJECT-1"
{
    "action_type": "search",
    "jql": "project = PROJECT-1 AND type = Bug AND priority = High"
}"""

    async def parse_command(self, transcript: str, project_key: Optional[str] = None) -> JiraAction:
        """
        Parse a transcribed command into a Jira action
        """
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Parse this command: {transcript}"}
            ]
            
            if project_key:
                messages[1]["content"] += f"\nProject context: {project_key}"
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                temperature=0.1
            )
            
            action_json = json.loads(response.choices[0].message.content)
            return JiraAction(**action_json)
            
        except Exception as e:
            raise Exception(f"Failed to parse command: {str(e)}")
    
    async def parse_teams_transcript(self, transcript: str, project_key: Optional[str] = None) -> List[JiraAction]:
        """
        Parse a Teams meeting transcript into multiple Jira actions
        """
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"""Parse this Teams transcript into Jira actions.
Each line should be treated as a separate command.
Transcript:
{transcript}"""}
            ]
            
            if project_key:
                messages[1]["content"] += f"\nProject context: {project_key}"
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                temperature=0.1
            )
            
            actions_json = json.loads(response.choices[0].message.content)
            return [JiraAction(**action) for action in actions_json]
            
        except Exception as e:
            raise Exception(f"Failed to parse Teams transcript: {str(e)}") 