import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Ini dia client-nya. Langsung kita buat di sini.
# Variabel 'supabase' ini yang nanti di-export.
supabase: Client = create_client(url, key)