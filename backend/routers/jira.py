from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from ..services.jira_service import JiraService
from ..auth.jwt_bearer import JWTBearer

router = APIRouter()
jwt_bearer = JWTBearer()

class Project(BaseModel):
    id: str
    key: str
    name: str
    description: Optional[str] = None

class Task(BaseModel):
    id: str
    key: str
    summary: str
    description: Optional[str] = None
    status: str
    assignee: Optional[str] = None

class Comment(BaseModel):
    body: str
    task_id: str

@router.get("/projects", response_model=List[Project])
async def get_projects(token: str = Depends(jwt_bearer)):
    """Get list of Jira projects the user has access to"""
    try:
        jira_service = JiraService(token)
        projects = await jira_service.get_projects()
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks", response_model=List[Task])
async def get_tasks(
    project_key: str,
    status: Optional[str] = None,
    assignee: Optional[str] = None,
    token: str = Depends(jwt_bearer)
):
    """Get tasks from a specific project with optional filters"""
    try:
        jira_service = JiraService(token)
        tasks = await jira_service.get_tasks(project_key, status, assignee)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/{task_id}/comments")
async def add_comment(
    task_id: str,
    comment: Comment,
    token: str = Depends(jwt_bearer)
):
    """Add a comment to a specific task"""
    try:
        jira_service = JiraService(token)
        result = await jira_service.add_comment(task_id, comment.body)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks")
async def create_task(
    task: Task,
    token: str = Depends(jwt_bearer)
):
    """Create a new task in the specified project"""
    try:
        jira_service = JiraService(token)
        result = await jira_service.create_task(task)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tasks/{task_id}")
async def update_task(
    task_id: str,
    task: Task,
    token: str = Depends(jwt_bearer)
):
    """Update an existing task"""
    try:
        jira_service = JiraService(token)
        result = await jira_service.update_task(task_id, task)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 