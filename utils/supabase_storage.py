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
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set for SupabaseStorage")

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
        resp = requests.put(url, data=data, headers=headers)
        return resp.status_code in (200, 201)

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
        resp = requests.post(url, headers=headers, json=record)
        if resp.status_code in (200, 201):
            data = resp.json()
            return data[0] if isinstance(data, list) and data else data
        else:
            print(f"⚠️  Supabase insert failed: {resp.status_code} {resp.text}")
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
            raise RuntimeError("Failed to upload video to Supabase storage")

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


def create_supabase_storage_if_configured() -> Optional[SupabaseStorage]:
    if os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY'):
        try:
            return SupabaseStorage()
        except Exception as e:
            print(f"⚠️  Could not initialize SupabaseStorage: {e}")
    return None
