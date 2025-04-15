from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
import os
from jira import JIRA
from services.supabase import get_supabase_client

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Jira configuration
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

def get_jira_client(token: str):
    """
    Get authenticated Jira client using user's OAuth token
    """
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user(token)
        
        # Get user's Jira tokens from Supabase
        user_data = supabase.table("users").select("jira_access_token").eq("id", user.id).single().execute()
        
        if not user_data.data or not user_data.data.get("jira_access_token"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Jira authentication required"
            )
        
        # Initialize Jira client with user's OAuth token
        return JIRA(
            server=JIRA_URL,
            oauth={
                'access_token': user_data.data["jira_access_token"],
                'access_token_secret': user_data.data.get("jira_refresh_token"),
                'consumer_key': os.getenv("JIRA_CLIENT_ID"),
                'key_cert': None
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize Jira client: {str(e)}"
        )

@router.get("/projects")
async def get_projects(token: str = Depends(oauth2_scheme)):
    """
    Get list of accessible Jira projects
    """
    try:
        jira = get_jira_client(token)
        projects = jira.projects()
        return [{"key": p.key, "name": p.name, "description": p.description} for p in projects]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch projects: {str(e)}"
        )

@router.post("/issues")
async def create_issue(
    summary: str,
    description: str,
    project_key: str,
    issue_type: str = "Task",
    assignee: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """
    Create a new Jira issue
    """
    try:
        jira = get_jira_client(token)
        
        issue_dict = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
        }
        
        if assignee:
            issue_dict['assignee'] = {'name': assignee}
        
        new_issue = jira.create_issue(fields=issue_dict)
        
        return {
            "key": new_issue.key,
            "self": new_issue.self,
            "summary": new_issue.fields.summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create issue: {str(e)}"
        )

@router.post("/issues/{issue_key}/comment")
async def add_comment(
    issue_key: str,
    comment: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Add a comment to an existing Jira issue
    """
    try:
        jira = get_jira_client(token)
        issue = jira.issue(issue_key)
        new_comment = jira.add_comment(issue, comment)
        
        return {
            "id": new_comment.id,
            "body": new_comment.body,
            "created": new_comment.created
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add comment: {str(e)}"
        )

@router.get("/search")
async def search_issues(
    jql: str,
    token: str = Depends(oauth2_scheme)
):
    """
    Search for issues using JQL
    """
    try:
        jira = get_jira_client(token)
        issues = jira.search_issues(jql)
        
        return [{
            "key": issue.key,
            "summary": issue.fields.summary,
            "status": issue.fields.status.name,
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None
        } for issue in issues]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search issues: {str(e)}"
        ) 