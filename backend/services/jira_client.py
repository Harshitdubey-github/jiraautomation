from typing import List, Dict, Any, Optional
from jira import JIRA
import os
from .command_parser import JiraAction

class JiraClient:
    def __init__(self):
        self.server_url = os.getenv("JIRA_SERVER_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        
        if not all([self.server_url, self.email, self.api_token]):
            raise ValueError("Missing required Jira credentials")
            
        self.client = JIRA(
            server=self.server_url,
            basic_auth=(self.email, self.api_token)
        )
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get list of accessible Jira projects
        """
        try:
            projects = self.client.projects()
            return [
                {
                    "id": project.id,
                    "key": project.key,
                    "name": project.name,
                    "description": getattr(project, "description", None)
                }
                for project in projects
            ]
        except Exception as e:
            raise Exception(f"Failed to fetch projects: {str(e)}")
    
    async def execute_action(self, action: JiraAction) -> Dict[str, Any]:
        """
        Execute a Jira action and return the result
        """
        try:
            if action.action_type == "create":
                return await self._create_issue(action)
            elif action.action_type == "update":
                return await self._update_issue(action)
            elif action.action_type == "comment":
                return await self._add_comment(action)
            elif action.action_type == "search":
                return await self._search_issues(action)
            else:
                raise ValueError(f"Unsupported action type: {action.action_type}")
                
        except Exception as e:
            raise Exception(f"Failed to execute action: {str(e)}")
    
    async def _create_issue(self, action: JiraAction) -> Dict[str, Any]:
        """
        Create a new Jira issue
        """
        if not action.project_key:
            raise ValueError("Project key is required for creating issues")
            
        issue_dict = {
            "project": {"key": action.project_key},
            "summary": action.summary,
            "description": action.description,
            "issuetype": {"name": "Task"}
        }
        
        if action.fields:
            issue_dict.update(action.fields)
            
        new_issue = self.client.create_issue(fields=issue_dict)
        return {
            "key": new_issue.key,
            "self": new_issue.self,
            "id": new_issue.id
        }
    
    async def _update_issue(self, action: JiraAction) -> Dict[str, Any]:
        """
        Update an existing Jira issue
        """
        if not action.issue_key:
            raise ValueError("Issue key is required for updates")
            
        issue = self.client.issue(action.issue_key)
        
        if action.fields:
            issue.update(fields=action.fields)
            
        return {
            "key": issue.key,
            "self": issue.self,
            "id": issue.id
        }
    
    async def _add_comment(self, action: JiraAction) -> Dict[str, Any]:
        """
        Add a comment to a Jira issue
        """
        if not action.issue_key:
            raise ValueError("Issue key is required for adding comments")
            
        if not action.comment:
            raise ValueError("Comment text is required")
            
        issue = self.client.issue(action.issue_key)
        comment = issue.add_comment(action.comment)
        
        return {
            "id": comment.id,
            "body": comment.body,
            "created": comment.created
        }
    
    async def _search_issues(self, action: JiraAction) -> List[Dict[str, Any]]:
        """
        Search for Jira issues using JQL
        """
        if not action.jql:
            raise ValueError("JQL query is required for search")
            
        issues = self.client.search_issues(action.jql)
        return [
            {
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": issue.fields.status.name,
                "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None
            }
            for issue in issues
        ] 