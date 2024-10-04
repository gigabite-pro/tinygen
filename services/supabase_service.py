from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_to_supabase(repo_url, prompt, diff):
    response = (
        supabase.table("tinygen")
        .insert({"repo_url": repo_url, "prompt": prompt, "diff": diff})
        .execute()
    )
    return response
