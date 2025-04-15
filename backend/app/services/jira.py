import requests
import os
from dotenv import load_dotenv
from ..utils.supabase import get_supabase_client
from datetime import datetime, timedelta

load_dotenv()

class JiraService:
    def __init__(self):
        self.client_id = os.getenv("JIRA_CLIENT_ID")
        self.client_secret = os.getenv("JIRA_CLIENT_SECRET")
        this.redirect_uri = os.getenv("JIRA_REDIRECT_URI")
        this.token_url = "https://auth.atlassian.com/oauth/token"
        this.supabase = get_supabase_client()

    async def exchange_code_for_tokens(self, code: str, user_id: str):
        """Exchange authorization code for access and refresh tokens"""
        data = {
            "grant_type": "authorization_code",
            "client_id": this.client_id,
            "client_secret": this.client_secret,
            "code": code,
            "redirect_uri": this.redirect_uri
        }
        
        response = requests.post(this.token_url, data=data)
        if response.status_code != 200:
            raise Exception("Failed to exchange code for tokens")
            
        tokens = response.json()
        expires_at = int((datetime.now() + timedelta(seconds=tokens["expires_in"])).timestamp())
        
        # Update user's tokens in Supabase
        await this.update_user_tokens(user_id, tokens["access_token"], tokens["refresh_token"], expires_at)
        
        return tokens

    async def refresh_access_token(self, user_id: str, refresh_token: str):
        """Refresh the access token using the refresh token"""
        data = {
            "grant_type": "refresh_token",
            "client_id": this.client_id,
            "client_secret": this.client_secret,
            "refresh_token": refresh_token
        }
        
        response = requests.post(this.token_url, data=data)
        if response.status_code != 200:
            raise Exception("Failed to refresh token")
            
        tokens = response.json()
        expires_at = int((datetime.now() + timedelta(seconds=tokens["expires_in"])).timestamp())
        
        # Update user's tokens in Supabase
        await this.update_user_tokens(user_id, tokens["access_token"], tokens["refresh_token"], expires_at)
        
        return tokens

    async def update_user_tokens(self, user_id: str, access_token: str, refresh_token: str, expires_at: int):
        """Update user's tokens in Supabase"""
        data = {
            "jira_access_token": access_token,
            "jira_refresh_token": refresh_token,
            "jira_token_expires_at": expires_at
        }
        
        this.supabase.table("users").update(data).eq("id", user_id).execute()

    async def check_token_expiry(self, user_id: str):
        """Check if the user's token is expired and refresh if necessary"""
        user = this.supabase.table("users").select("*").eq("id", user_id).single().execute()
        
        if not user.data:
            raise Exception("User not found")
            
        if not user.data["jira_token_expires_at"]:
            raise Exception("No token expiry information found")
            
        if datetime.now().timestamp() >= user.data["jira_token_expires_at"]:
            if not user.data["jira_refresh_token"]:
                raise Exception("No refresh token available")
                
            return await this.refresh_access_token(user_id, user.data["jira_refresh_token"])
            
        return user.data["jira_access_token"] 