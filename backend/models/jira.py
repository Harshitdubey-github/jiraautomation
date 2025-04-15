from pydantic import BaseModel
from typing import Optional, List

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
    id: Optional[str] = None
    body: str
    author: Optional[str] = None
    created: Optional[str] = None
    task_id: Optional[str] = None

class TaskUpdate(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assignee: Optional[str] = None

class TaskCreate(BaseModel):
    project_key: str
    summary: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    issue_type: str = "Task"

class TaskSearchResult(BaseModel):
    total: int
    issues: List[Task]

class ProjectList(BaseModel):
    projects: List[Project] 