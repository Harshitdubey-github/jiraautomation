from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from ..models.user import User, UserCreate, UserUpdate
from ..utils.supabase import get_supabase_client
from ..services.jira import JiraService
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
jira_service = JiraService()

@router.get("/jira/login")
async def jira_login():
    """Redirect to Jira OAuth login page"""
    client_id = os.getenv("JIRA_CLIENT_ID")
    redirect_uri = os.getenv("JIRA_REDIRECT_URI")
    
    auth_url = f"https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id={client_id}&scope=read%3Ajira-work%20write%3Ajira-work&redirect_uri={redirect_uri}&response_type=code&prompt=consent"
    return {"auth_url": auth_url}

@router.get("/jira/callback")
async def jira_callback(code: str, user_id: str):
    """Handle Jira OAuth callback"""
    try:
        tokens = await jira_service.exchange_code_for_tokens(code, user_id)
        return {"message": "Jira authentication successful", "tokens": tokens}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/jira/refresh")
async def refresh_jira_token(user_id: str):
    """Refresh Jira access token"""
    try:
        supabase = get_supabase_client()
        user = supabase.table("users").select("*").eq("id", user_id).single().execute()
        
        if not user.data or not user.data["jira_refresh_token"]:
            raise HTTPException(status_code=400, detail="No refresh token available")
            
        tokens = await jira_service.refresh_access_token(user_id, user.data["jira_refresh_token"])
        return {"message": "Token refreshed successfully", "tokens": tokens}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user information"""
    try:
        supabase = get_supabase_client()
        user = supabase.auth.get_user(token)
        
        # Check and refresh Jira token if necessary
        if user.data.get("jira_access_token"):
            try:
                jira_token = await jira_service.check_token_expiry(user.data["id"])
                user.data["jira_access_token"] = jira_token
            except Exception as e:
                # If token refresh fails, remove the token
                user.data["jira_access_token"] = None
                user.data["jira_refresh_token"] = None
                user.data["jira_token_expires_at"] = None
                
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials") 