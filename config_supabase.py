import os
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

def config_supabase():
    # Configuração do Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)

    return supabase