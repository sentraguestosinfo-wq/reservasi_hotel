from supabase import create_client, Client
import sys

# SUPABASE CONFIG (REST API MODE)
SUPABASE_URL = "https://relkgipocdukdusakdtv.supabase.co"
SUPABASE_KEY = "sb_secret_qc2aaevA7-UEx_YNS93uVQ__JwiQVP4" 

print(f"Testing connection to Supabase REST API: {SUPABASE_URL}")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Test connection by selecting 1 row from bookings
    response = supabase.table('bookings').select("count", count='exact').limit(1).execute()
    
    print("Connection successful!")
    print(f"Bookings count: {response.count}")
    
except Exception as e:
    print(f"Connection failed: {e}")
