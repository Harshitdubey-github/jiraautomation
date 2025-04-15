from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: str
    email: str
    jira_access_token: Optional[str] = None
    jira_refresh_token: Optional[str] = None
    jira_token_expires_at: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    jira_access_token: Optional[str] = None
    jira_refresh_token: Optional[str] = None
    jira_token_expires_at: Optional[int] = None 