#!/usr/bin/env python3
"""
Validate Supabase configuration and connectivity
"""
import os
import sys
from pathlib import Path
import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()


def validate_supabase():
    """Test Supabase configuration"""
    print("🔍 Supabase Configuration Validator\n")
    print("=" * 60)
    
    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    print("\n1️⃣  Environment Variables:")
    print(f"   SUPABASE_URL: {'✓' if supabase_url else '❌ NOT SET'}")
    if supabase_url:
        print(f"      → {supabase_url}")
    print(f"   SUPABASE_KEY: {'✓' if supabase_key else '❌ NOT SET'}")
    if supabase_key:
        print(f"      → {supabase_key[:20]}..." if len(supabase_key) > 20 else f"      → {supabase_key}")
    
    if not supabase_url or not supabase_key:
        print("\n❌ Missing Supabase credentials!")
        print("\n📋 Setup Instructions:")
        print("   1. Go to https://app.supabase.com")
        print("   2. Create a project or select existing one")
        print("   3. Get credentials from Settings → API")
        print("   4. Set environment variables:")
        print("      export SUPABASE_URL='https://xyz.supabase.co'")
        print("      export SUPABASE_KEY='service_role_key'")
        print("   5. Add to .env file:")
        print("      SUPABASE_URL=https://xyz.supabase.co")
        print("      SUPABASE_KEY=service_role_key")
        return False
    
    print("\n2️⃣  Connection Test:")
    try:
        from utils.supabase_storage import SupabaseStorage
        
        storage = SupabaseStorage()
        print("   ✓ Supabase client initialized")
        
        print("\n3️⃣  API Connectivity Tests:")
        
        # First, check if videos table exists with better error handling
        print("   Checking if 'videos' table exists...")
        try:
            url = f"{storage.rest_base}/videos?limit=1"
            resp = requests.get(url, headers=storage.headers, timeout=10)
            
            if resp.status_code == 200:
                print(f"   ✓ Videos table exists and is accessible")
            elif resp.status_code == 404:
                print(f"   ❌ Videos table not found (404)")
                print("\n   📋 CREATE TABLE in SQL EDITOR:")
                print("      1. Go to https://app.supabase.com → SQL Editor")
                print("      2. Run this SQL:\n")
                print("""      CREATE TABLE IF NOT EXISTS public.videos (
        id text PRIMARY KEY,
        filename text,
        filepath text,
        topic text,
        duration real,
        created_at timestamptz DEFAULT now(),
        status text,
        file_size integer,
        playable boolean,
        url text,
        youtube_id text
      );""")
                return False
            elif resp.status_code == 401:
                print(f"   ❌ Authentication failed (401)")
                print("   Check your SUPABASE_KEY is valid")
                return False
            elif resp.status_code == 403:
                print(f"   ❌ Permission denied (403)")
                print("   Check RLS policies on videos table")
                return False
            else:
                error_text = resp.text.lower() if hasattr(resp, 'text') else str(resp)
                if "schema_migrations" in error_text:
                    print(f"   ⚠️  Videos table doesn't exist yet")
                    print("   Run the SQL above to create it")
                    return False
                else:
                    print(f"   ⚠️  Unexpected response ({resp.status_code})")
                    print(f"   Error: {resp.text[:100]}")
                    return False
        except requests.exceptions.Timeout:
            print(f"   ⚠️  Request timeout - Supabase may be slow")
            print("   Try again in a moment")
            return False
        except Exception as e:
            error_str = str(e).lower()
            if "schema_migrations" in error_str or "does not exist" in error_str:
                print(f"   ❌ Videos table doesn't exist")
                print("   Run the SQL above to create it")
                return False
            else:
                print(f"   ⚠️  Error checking table: {str(e)}")
                return False
        
        # Run storage validation
        print("\n   Running storage validation...")
        validation = storage.validate_configuration()
        
        print(f"   Storage API: {validation.get('storage_api', 'Unknown')}")
        
        if validation.get("errors"):
            print("\n❌ Errors:")
            for error in validation["errors"]:
                print(f"   • {error}")
        
        if validation.get("warnings"):
            print("\n⚠️  Warnings:")
            for warning in validation["warnings"]:
                print(f"   • {warning}")
        
        if not validation.get("errors"):
            print("\n✅ Configuration Valid!")
            return True
        else:
            print("\n❌ Configuration has errors")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("\n📋 Troubleshooting:")
        print("   • Check your credentials are correct")
        print("   • Verify Supabase project exists")
        print("   • Check SUPABASE_URL format (should be https://xyz.supabase.co)")
        print("   • Verify SUPABASE_KEY is the service role key")
        return False


def setup_instructions():
    """Print detailed setup instructions"""
    print("\n" + "=" * 60)
    print("📚 Detailed Setup Instructions")
    print("=" * 60)
    
    print("""
1. CREATE SUPABASE PROJECT:
   • Visit https://app.supabase.com
   • Click "New Project"
   • Fill in project details and create

2. GET API CREDENTIALS:
   • Go to Settings → API (left sidebar)
   • Copy "Project URL" → SUPABASE_URL
   • Copy "service_role" key → SUPABASE_KEY

3. CREATE STORAGE BUCKET:
   • Go to Storage → Buckets
   • Click "New bucket"
   • Name it "videos"
   • Set it to Public (or configure RLS policies)

4. CREATE VIDEOS TABLE:
   • Go to SQL Editor
   • Create new query
   • Paste this SQL:

   CREATE TABLE public.videos (
     id TEXT PRIMARY KEY,
     filename TEXT NOT NULL,
     filepath TEXT NOT NULL,
     topic TEXT,
     duration FLOAT,
     file_size INTEGER,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     status TEXT DEFAULT 'pending',
     playable BOOLEAN DEFAULT FALSE,
     url TEXT
   );

5. SET ENVIRONMENT VARIABLES:
   • Create/edit .env file in project root
   • Add:
     SUPABASE_URL=https://your-project.supabase.co
     SUPABASE_KEY=your_service_role_key

6. TEST:
   • Run: python3 scripts/validate_supabase.py
   • Should show ✓ for all tests
""")


if __name__ == "__main__":
    success = validate_supabase()
    
    if not success and "--setup" not in sys.argv:
        print("\n💡 For detailed setup instructions, run:")
        print("   python3 scripts/validate_supabase.py --setup")
    elif "--setup" in sys.argv:
        setup_instructions()
    
    sys.exit(0 if success else 1)
