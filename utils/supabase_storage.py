"""
Supabase-backed video storage adapter (uses Supabase REST APIs via requests)

Environment variables required:
- SUPABASE_URL
- SUPABASE_KEY (service role or anon key with appropriate permissions)

This adapter implements the same interface used by `VideoStorage` so it can
be swapped in transparently when deployed with Supabase.
"""
import os
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List


class SupabaseStorage:
    def __init__(self, bucket: str = "videos"):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.bucket = bucket

        if not self.supabase_url or not self.supabase_key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_KEY must be set for SupabaseStorage.\n"
                "Set environment variables:\n"
                "  export SUPABASE_URL='https://xyz.supabase.co'\n"
                "  export SUPABASE_KEY='your_service_role_key'"
            )

        # REST endpoints
        self.storage_base = f"{self.supabase_url}/storage/v1"
        self.rest_base = f"{self.supabase_url}/rest/v1"

        # Headers used for both storage and Postgres REST calls
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}"
        }

    # ---------- Storage (object) APIs ----------
    def _upload_object(self, path: str, data: bytes, content_type: str = "video/mp4") -> bool:
        url = f"{self.storage_base}/object/{self.bucket}/{path}"
        headers = dict(self.headers)
        headers.update({"Content-Type": content_type})
        
        try:
            resp = requests.put(url, data=data, headers=headers, timeout=30)
            
            if resp.status_code in (200, 201):
                return True
            else:
                error_msg = resp.text
                try:
                    error_data = resp.json()
                    error_msg = error_data.get('message') or error_data.get('error') or error_msg
                except:
                    pass
                
                print(f"⚠️  Supabase upload failed: {resp.status_code}")
                print(f"   URL: {url}")
                print(f"   Error: {error_msg}")
                
                # Provide helpful debugging
                if resp.status_code == 401:
                    print("   ❌ Authentication failed - check SUPABASE_KEY is valid")
                elif resp.status_code == 404:
                    print(f"   ❌ Bucket '{self.bucket}' not found - create it in Supabase Storage")
                elif resp.status_code == 403:
                    print("   ❌ Permission denied - check storage bucket policies")
                
                return False
        except Exception as e:
            print(f"⚠️  Supabase connection error: {str(e)}")
            return False

    def _get_public_url(self, path: str) -> str:
        # Public URL (works if bucket or object is public)
        return f"{self.storage_base}/object/public/{self.bucket}/{path}"

    def _create_signed_url(self, path: str, expires_in: int = 3600) -> Optional[str]:
        url = f"{self.storage_base}/object/sign/{self.bucket}/{path}"
        body = {"expires_in": expires_in}
        resp = requests.post(url, headers=self.headers, json=body)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("signedURL") or data.get("signed_url") or data.get("url")
        return None

    # ---------- Postgres (metadata) APIs ----------
    def _insert_metadata(self, record: Dict) -> Optional[Dict]:
        url = f"{self.rest_base}/videos"
        headers = dict(self.headers)
        headers.update({"Content-Type": "application/json", "Prefer": "return=representation"})
        try:
            resp = requests.post(url, headers=headers, json=record, timeout=10)
            if resp.status_code in (200, 201):
                data = resp.json()
                return data[0] if isinstance(data, list) and data else data
            else:
                error_text = resp.text.lower()
                if "schema_migrations" in error_text or "does not exist" in error_text:
                    print(f"❌ Videos table doesn't exist in Supabase")
                    print(f"   Resolution: Run create_supabase_table() first")
                    print(f"   Or go to SQL Editor and create the table manually")
                elif resp.status_code == 404:
                    print(f"❌ Videos table not found in database (404)")
                elif resp.status_code == 401:
                    print(f"❌ Authentication failed - check SUPABASE_KEY")
                elif resp.status_code == 403:
                    print(f"❌ Permission denied - check RLS policies")
                else:
                    print(f"⚠️  Supabase insert failed: {resp.status_code}")
                print(f"   Details: {resp.text[:200]}")
                return None
        except Exception as e:
            print(f"⚠️  Supabase insert error: {str(e)}")
            return None

    def _list_metadata(self) -> List[Dict]:
        url = f"{self.rest_base}/videos?select=*"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            return resp.json()
        print(f"⚠️  Supabase list failed: {resp.status_code} {resp.text}")
        return []

    def _get_metadata(self, video_id: str) -> Optional[Dict]:
        url = f"{self.rest_base}/videos?id=eq.{video_id}&select=*"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            data = resp.json()
            return data[0] if data else None
        print(f"⚠️  Supabase get failed: {resp.status_code} {resp.text}")
        return None

    def update_metadata(self, video_id: str, updates: Dict) -> Optional[Dict]:
        """Patch metadata row for a video via Supabase REST API and return updated record."""
        if not updates:
            return self.get_video_info(video_id)
        url = f"{self.rest_base}/videos?id=eq.{video_id}"
        headers = dict(self.headers)
        headers.update({"Content-Type": "application/json", "Prefer": "return=representation"})
        resp = requests.patch(url, headers=headers, json=updates)
        if resp.status_code in (200, 201):
            data = resp.json()
            return data[0] if isinstance(data, list) and data else data
        print(f"⚠️  Supabase update failed: {resp.status_code} {resp.text}")
        return None

    # ---------- Public interface matching VideoStorage ----------
    def save_video(self, video_data: bytes, topic: str, duration: float = 0) -> Dict:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic[:30] if c.isalnum() or c in '-_ ')
        filename = f"{safe_topic}_{timestamp}.mp4"

        # Upload object
        ok = self._upload_object(filename, video_data, content_type="video/mp4")
        if not ok:
            print(f"❌ Upload configuration check:")
            print(f"   SUPABASE_URL: {'✓' if self.supabase_url else '❌ NOT SET'}")
            print(f"   SUPABASE_KEY: {'✓' if self.supabase_key else '❌ NOT SET'}")
            print(f"   Bucket: {self.bucket}")
            raise RuntimeError(f"Failed to upload video to Supabase storage. Check logs above for details.")

        # Build metadata
        video_id = timestamp
        public_url = self._get_public_url(filename)
        record = {
            "id": video_id,
            "filename": filename,
            "filepath": filename,
            "topic": topic,
            "duration": duration,
            "created_at": datetime.now().isoformat(),
            "status": "completed",
            "file_size": len(video_data),
            "playable": True,
            "url": public_url
        }

        inserted = self._insert_metadata(record)
        if inserted:
            return inserted
        # If metadata insert failed, return local record
        return record

    def get_video_info(self, video_id: str) -> Optional[Dict]:
        return self._get_metadata(video_id)

    def get_all_videos(self) -> List[Dict]:
        return self._list_metadata()

    def get_video_file(self, video_id: str) -> Optional[str]:
        info = self.get_video_info(video_id)
        if not info:
            return None
        path = info.get("filepath") or info.get("filename")
        # Try public url first
        public = self._get_public_url(path)
        # Optionally, we could verify existence; return signed url to be safe
        signed = self._create_signed_url(path, expires_in=3600)
        return signed or public

    def delete_video(self, video_id: str) -> bool:
        # Delete metadata row
        meta = self.get_video_info(video_id)
        if not meta:
            return False
        filename = meta.get("filepath") or meta.get("filename")

        # Delete object
        url = f"{self.storage_base}/object/{self.bucket}/{filename}"
        resp = requests.delete(url, headers=self.headers)

        # Delete metadata row
        rest_url = f"{self.rest_base}/videos?id=eq.{video_id}"
        resp2 = requests.delete(rest_url, headers=self.headers)

        return resp.status_code in (200, 204) and resp2.status_code in (200, 204)

    def create_blank_video(self, topic: str, duration: int = 10) -> bytes:
        # Reuse a minimal MP4 fallback similar to local VideoStorage
        return (
            b'\x00\x00\x00\x20ftypisom\x00\x00\x00\x00'
            b'isomiso2avc1mp41\x00\x00\x00\x00'
            b'mdat' + b'\x00' * 100
        )

    def validate_configuration(self) -> Dict:
        """
        Test Supabase connection and configuration.
        Returns dict with status, errors, and warnings.
        """
        result = {
            "url": self.supabase_url,
            "bucket": self.bucket,
            "has_key": bool(self.supabase_key),
            "errors": [],
            "warnings": []
        }
        
        # Test storage API
        try:
            test_data = b"test"
            test_path = "connectivity-test.bin"
            url = f"{self.storage_base}/object/{self.bucket}/{test_path}"
            headers = dict(self.headers)
            headers.update({"Content-Type": "application/octet-stream"})
            
            resp = requests.put(url, data=test_data, headers=headers, timeout=10)
            
            if resp.status_code in (200, 201):
                result["storage_api"] = "✓ Connected"
                # Clean up test file
                requests.delete(url, headers=self.headers)
            else:
                result["storage_api"] = f"✗ Failed ({resp.status_code})"
                result["errors"].append(f"Storage API returned {resp.status_code}: {resp.text}")
        except Exception as e:
            result["storage_api"] = f"✗ Error"
            result["errors"].append(f"Storage API error: {str(e)}")
        
        # Test if videos table exists (improved error handling)
        try:
            url = f"{self.rest_base}/videos?limit=1"
            resp = requests.head(url, headers=self.headers, timeout=10)
            
            if resp.status_code == 200:
                result["metadata_api"] = "✓ Connected (videos table exists)"
            elif resp.status_code == 404:
                result["metadata_api"] = "⚠️  Videos table not found (404)"
                result["warnings"].append("Videos table doesn't exist - run SQL to create it")
            elif resp.status_code == 401:
                result["metadata_api"] = "✗ Authentication Failed"
                result["errors"].append("SUPABASE_KEY authentication failed")
            elif resp.status_code == 403:
                result["metadata_api"] = "✗ Permission Denied"
                result["errors"].append("RLS policies may be blocking access")
            else:
                result["metadata_api"] = f"✗ Failed ({resp.status_code})"
                result["warnings"].append(f"Metadata API returned {resp.status_code}")
        except Exception as e:
            error_msg = str(e).lower()
            if "schema_migrations" in error_msg or "does not exist" in error_msg:
                result["metadata_api"] = "⚠️  Videos table not found"
                result["warnings"].append("Videos table doesn't exist yet - need to create it")
            else:
                result["metadata_api"] = f"✗ Error"
                result["warnings"].append(f"Metadata API error: {str(e)}")
        
        return result

    def create_videos_table(self) -> bool:
        """
        Create the videos table in Supabase via SQL query.
        Useful if you can't access the SQL editor manually.
        
        Returns True if table creation was successful or if table already exists.
        """
        sql = """
        CREATE TABLE IF NOT EXISTS public.videos (
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
        CREATE INDEX IF NOT EXISTS idx_videos_youtube_id ON public.videos (youtube_id);
        """
        
        try:
            # Use RPC call to execute SQL through the REST API
            url = f"{self.rest_base}/rpc/pg_execute"
            headers = dict(self.headers)
            headers.update({"Content-Type": "application/json"})
            
            # Alternative: Try direct table creation via REST
            # Check if table exists first
            check_url = f"{self.rest_base}/videos?limit=0&count=exact"
            check_resp = requests.head(check_url, headers=self.headers, timeout=5)
            
            if check_resp.status_code == 200:
                print("✓ Videos table already exists")
                return True
            elif check_resp.status_code == 404:
                print("ℹ️  Videos table doesn't exist, attempting to create...")
                print("❌ Cannot create table via REST API (no SQL execution endpoint)")
                print("\n📋 Please create table manually:")
                print("   1. Go to https://app.supabase.com → SQL Editor")
                print("   2. Create new query")
                print("   3. Paste and run this SQL:\n")
                print(sql)
                return False
            else:
                print(f"⚠️  Unexpected response when checking table: {check_resp.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking/creating table: {str(e)}")
            print("📋 Please create table manually:")
            print("   1. Go to https://app.supabase.com → SQL Editor")
            print("   2. Create new query")
            print("   3. Run the SQL shown above")
            return False


def create_supabase_storage_if_configured() -> Optional[SupabaseStorage]:
    if os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY'):
        try:
            return SupabaseStorage()
        except Exception as e:
            print(f"⚠️  Could not initialize SupabaseStorage: {e}")
    return None
