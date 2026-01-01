from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ygzsdqixeadyrvhyhtab.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_AzkQm28ZN06J8P_7GnefFA_nLsGjWYa")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)