from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Supabase URL and key must be set in environment variables")

supabase = create_client(supabase_url, supabase_key)

def get_supabase_client():
    return supabase 