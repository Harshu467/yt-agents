#!/usr/bin/env python3
"""
Create the Supabase videos table for storing video metadata.
Run this if you get "relation videos does not exist" error.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()


def create_table():
    """Create the videos table in Supabase"""
    
    print("📊 Supabase Videos Table Creator\n")
    print("=" * 60)
    
    # Check credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("\n❌ Missing Supabase credentials!")
        print("   Set SUPABASE_URL and SUPABASE_KEY first")
        print("\n   export SUPABASE_URL='https://your-project.supabase.co'")
        print("   export SUPABASE_KEY='your_service_role_key'")
        return False
    
    print("\n✓ Credentials found")
    print(f"  URL: {supabase_url}")
    print(f"  Key: {supabase_key[:20]}...")
    
    # Try to create storage
    try:
        from utils.supabase_storage import SupabaseStorage
        
        print("\n🔄 Initializing Supabase client...")
        storage = SupabaseStorage()
        print("✓ Client initialized")
        
        # Check if table exists
        print("\n🔍 Checking if videos table exists...")
        import requests
        
        url = f"{storage.rest_base}/videos?limit=0"
        resp = requests.head(url, headers=storage.headers, timeout=5)
        
        if resp.status_code == 200:
            print("✓ Videos table already exists!")
            print("\nYou're all set - no action needed.")
            return True
        
        # Table doesn't exist, show SQL to create it
        if resp.status_code == 404 or "does not exist" in resp.text.lower():
            print("❌ Videos table doesn't exist yet")
            print("\n📋 TABLE CREATION SQL:")
            print("=" * 60)
            
            sql = """CREATE TABLE IF NOT EXISTS public.videos (
  id text PRIMARY KEY,
  filename text,
  filepath text,
  topic text,
  duration real,
  file_size integer,
  created_at timestamptz DEFAULT now(),
  status text DEFAULT 'pending',
  playable boolean DEFAULT FALSE,
  url text,
  youtube_id text
);

CREATE INDEX IF NOT EXISTS idx_videos_created_at ON public.videos (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_videos_topic ON public.videos (topic);
CREATE INDEX IF NOT EXISTS idx_videos_youtube_id ON public.videos (youtube_id);"""
            
            print(sql)
            print("=" * 60)
            
            print("\n📚 SETUP STEPS:")
            print("   1. Open https://app.supabase.com")
            print("   2. Select your project")
            print("   3. Go to SQL Editor (left sidebar)")
            print("   4. Click 'New query'")
            print("   5. Copy and paste the SQL above")
            print("   6. Click 'Run' or press Cmd+Enter")
            print("   7. Come back and run this script again")
            
            return False
        
        else:
            print(f"⚠️  Unexpected response: {resp.status_code}")
            print(f"   {resp.text[:200]}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n📋 MANUAL SETUP:")
        print("   1. Open https://app.supabase.com")
        print("   2. SQL Editor → New query")
        print("   3. Paste the SQL shown above")
        print("   4. Run it")
        return False


def get_table_status():
    """Get current table creation status"""
    print("\n📊 CURRENT TABLE STATUS:")
    print("=" * 60)
    
    try:
        import requests
        from utils.supabase_storage import SupabaseStorage
        
        storage = SupabaseStorage()
        
        url = f"{storage.rest_base}/videos?limit=0&count=exact"
        resp = requests.head(url, headers=storage.headers, timeout=5)
        
        if resp.status_code == 200:
            print("✓ Videos table EXISTS and is ready to use!")
            print(f"  URL: {storage.supabase_url}")
            print(f"  Bucket: {storage.bucket}")
            return True
        elif resp.status_code == 404:
            print("❌ Videos table does NOT exist yet")
            print("   Run the SQL provided above to create it")
            return False
        else:
            print(f"⚠️  Status unclear: {resp.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return None


if __name__ == "__main__":
    success = create_table()
    
    if success is True:
        print("\n✅ All set! You can now upload videos to Supabase.")
    elif success is False and "--status" not in sys.argv:
        print("\n💡 After creating the table in SQL Editor, run:")
        print("   python3 scripts/setup_supabase_table.py --status")
    
    if "--status" in sys.argv:
        get_table_status()
    
    sys.exit(0)
