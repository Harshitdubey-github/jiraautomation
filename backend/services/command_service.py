import os
import json
import aiohttp
from typing import List, Optional, Dict, Any
from ..models.commands import CommandResponse, TranscriptParseResponse
from ..services.jira_service import JiraService

class CommandService:
    def __init__(self, token: str):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.jira_service = JiraService(token)

    async def parse_command(
        self,
        text: str,
        project_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> CommandResponse:
        """
        Parse a command from transcribed text using OpenAI
        """
        # Construct the prompt for OpenAI
        prompt = self._build_command_prompt(text, project_key, context)
        
        # Call OpenAI API
        response = await self._call_openai(prompt)
        
        # Parse the response
        try:
            parsed_response = json.loads(response)
            return CommandResponse(**parsed_response)
        except json.JSONDecodeError:
            raise Exception("Failed to parse OpenAI response as JSON")

    async def execute_command(self, command: CommandResponse) -> Dict[str, Any]:
        """
        Execute a parsed command using the Jira service
        """
        action = command.action
        details = command.details
        
        if action == "query_tasks":
            return await self.jira_service.get_tasks(
                project_key=details.get("project_key"),
                status=details.get("status"),
                assignee=details.get("assignee")
            )
        
        elif action == "update_comment":
            return await self.jira_service.add_comment(
                task_id=details.get("task_id"),
                body=details.get("comment")
            )
        
        elif action == "create_issue":
            return await self.jira_service.create_task(details)
        
        elif action == "update_task":
            return await self.jira_service.update_task(
                task_id=details.get("task_id"),
                task=details
            )
        
        else:
            raise ValueError(f"Unknown action: {action}")

    async def parse_transcript(
        self,
        transcript: str,
        project_key: Optional[str] = None
    ) -> TranscriptParseResponse:
        """
        Parse a Teams meeting transcript for actions using OpenAI
        """
        # Construct the prompt for OpenAI
        prompt = self._build_transcript_prompt(transcript, project_key)
        
        # Call OpenAI API
        response = await self._call_openai(prompt)
        
        # Parse the response
        try:
            parsed_response = json.loads(response)
            return TranscriptParseResponse(actions=parsed_response)
        except json.JSONDecodeError:
            raise Exception("Failed to parse OpenAI response as JSON")

    async def _call_openai(self, prompt: str) -> str:
        """
        Call the OpenAI API with the given prompt
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/chat/completions"
            
            data = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that parses commands for Jira task management."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
            
            async with session.post(url, headers=self.headers, json=data) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {error_text}")
                
                result = await response.json()
                return result["choices"][0]["message"]["content"]

    def _build_command_prompt(
        self,
        text: str,
        project_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a prompt for OpenAI to parse a command
        """
        prompt = f"""
        Parse the following command for Jira task management:
        
        Command: {text}
        """
        
        if project_key:
            prompt += f"\nProject: {project_key}"
        
        if context:
            prompt += f"\nContext: {json.dumps(context, indent=2)}"
        
        prompt += """
        
        Return a JSON object with the following structure:
        {
            "action": "query_tasks|update_comment|create_issue|update_task",
            "details": {
                // Action-specific details
            },
            "confidence": 0.95
        }
        
        For query_tasks, details should include: project_key, status (optional), assignee (optional)
        For update_comment, details should include: task_id, comment
        For create_issue, details should include: project_key, summary, description (optional), assignee (optional)
        For update_task, details should include: task_id, summary (optional), description (optional), status (optional), assignee (optional)
        """
        
        return prompt

    def _build_transcript_prompt(
        self,
        transcript: str,
        project_key: Optional[str] = None
    ) -> str:
        """
        Build a prompt for OpenAI to parse a Teams meeting transcript
        """
        prompt = f"""
        Parse the following Teams meeting transcript for Jira task management actions:
        
        Transcript:
        {transcript}
        """
        
        if project_key:
            prompt += f"\nProject: {project_key}"
        
        prompt += """
        
        Return a JSON array of action objects with the following structure:
        [
            {
                "action": "query_tasks|update_comment|create_issue|update_task",
                "details": {
                    // Action-specific details
                },
                "confidence": 0.95
            }
        ]
        
        For query_tasks, details should include: project_key, status (optional), assignee (optional)
        For update_comment, details should include: task_id, comment
        For create_issue, details should include: project_key, summary, description (optional), assignee (optional)
        For update_task, details should include: task_id, summary (optional), description (optional), status (optional), assignee (optional)
        """
        
        return prompt 