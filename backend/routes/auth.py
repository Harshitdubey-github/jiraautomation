from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
import os
import requests
from services.supabase import get_supabase_client

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Jira OAuth configuration
JIRA_CLIENT_ID = os.getenv("JIRA_CLIENT_ID")
JIRA_CLIENT_SECRET = os.getenv("JIRA_CLIENT_SECRET")
JIRA_REDIRECT_URI = "http://localhost:8000/api/auth/callback"
JIRA_AUTH_URL = "https://auth.atlassian.com/authorize"
JIRA_TOKEN_URL = "https://auth.atlassian.com/oauth/token"

# Supabase client
supabase = get_supabase_client()

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None

@router.get("/login")
async def login():
    """
    Redirect to Jira OAuth login page
    """
    auth_url = f"{JIRA_AUTH_URL}?audience=api.atlassian.com&client_id={JIRA_CLIENT_ID}&scope=read%3Ajira-work%20write%3Ajira-work&redirect_uri={JIRA_REDIRECT_URI}&response_type=code&prompt=consent"
    return {"auth_url": auth_url}

@router.get("/callback")
async def callback(code: str):
    """
    Handle the OAuth callback from Jira
    """
    try:
        # Exchange code for access token
        token_response = requests.post(
            JIRA_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": JIRA_CLIENT_ID,
                "client_secret": JIRA_CLIENT_SECRET,
                "code": code,
                "redirect_uri": JIRA_REDIRECT_URI
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token from Jira"
            )
        
        token_data = token_response.json()
        
        # Get user info from Jira
        user_response = requests.get(
            "https://api.atlassian.com/me",
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Jira"
            )
        
        user_data = user_response.json()
        
        # Store user and token in Supabase
        user_id = user_data.get("account_id")
        email = user_data.get("email")
        name = user_data.get("name")
        
        # Check if user exists
        user_result = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if len(user_result.data) == 0:
            # Create new user
            supabase.table("users").insert({
                "id": user_id,
                "email": email,
                "name": name
            }).execute()
        
        # Store token
        supabase.table("tokens").upsert({
            "user_id": user_id,
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in")
        }).execute()
        
        # Generate session token
        session_token = supabase.auth.sign_in_with_password({
            "email": email,
            "password": user_id  # Using user_id as password for simplicity
        }).data.session.access_token
        
        return {
            "access_token": session_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email,
                "name": name
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login
    """
    # This is a simplified version - in a real app, you would validate credentials
    # For this prototype, we'll just return a token if the user exists
    try:
        user_result = supabase.table("users").select("*").eq("email", form_data.username).execute()
        
        if len(user_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate session token
        session_token = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        }).data.session.access_token
        
        return {"access_token": session_token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )

@router.get("/me", response_model=User)
async def read_users_me(token: str = Depends(oauth2_scheme)):
    """
    Get current user information
    """
    try:
        # Verify token with Supabase
        user = supabase.auth.get_user(token)
        
        # Get user data from database
        user_result = supabase.table("users").select("*").eq("id", user.user.id).execute()
        
        if len(user_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = user_result.data[0]
        
        return {
            "id": user_data["id"],
            "email": user_data["email"],
            "name": user_data.get("name")
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) 