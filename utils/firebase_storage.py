"""
Firebase Storage + Firestore adapter

Requires service account JSON file and environment vars:
- `GOOGLE_APPLICATION_CREDENTIALS` pointing to service account JSON file
- `FIREBASE_STORAGE_BUCKET` (e.g., "my-project.appspot.com")
This adapter uses `google-cloud-storage` and `google-cloud-firestore`.
If those libraries are not installed, the factory will return None.
"""
import os
from datetime import datetime
from typing import Optional, Dict, List

try:
    from google.cloud import storage as gcs
    from google.cloud import firestore
except Exception:
    gcs = None
    firestore = None


class FirebaseStorage:
    def __init__(self):
        if gcs is None or firestore is None:
            raise RuntimeError("google-cloud libraries not available")

        self.bucket_name = os.getenv('FIREBASE_STORAGE_BUCKET')
        if not self.bucket_name:
            raise RuntimeError('FIREBASE_STORAGE_BUCKET must be set')

        # Initialize clients (uses GOOGLE_APPLICATION_CREDENTIALS env)
        self.gcs_client = gcs.Client()
        self.bucket = self.gcs_client.bucket(self.bucket_name)
        self.fs = firestore.Client()
        self.collection = self.fs.collection('videos')

    def save_video(self, video_data: bytes, topic: str, duration: float = 0) -> Dict:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_topic = ''.join(c for c in topic[:30] if c.isalnum() or c in '-_ ')
        filename = f"{safe_topic}_{timestamp}.mp4"

        blob = self.bucket.blob(filename)
        blob.upload_from_string(video_data, content_type='video/mp4')

        # Make object private by default; generate signed URL on retrieval
        video_id = timestamp
        record = {
            'id': video_id,
            'filename': filename,
            'filepath': filename,
            'topic': topic,
            'duration': duration,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'completed',
            'file_size': len(video_data),
            'playable': True,
            'url': f"/api/videos/{video_id}"
        }

        # Store metadata in Firestore
        doc_ref = self.collection.document(video_id)
        doc_ref.set(record)
        return record

    def get_video_info(self, video_id: str) -> Optional[Dict]:
        doc = self.collection.document(video_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def get_all_videos(self) -> List[Dict]:
        docs = self.collection.order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        return [d.to_dict() for d in docs]

    def get_video_file(self, video_id: str) -> Optional[str]:
        info = self.get_video_info(video_id)
        if not info:
            return None
        filename = info.get('filepath') or info.get('filename')
        blob = self.bucket.blob(filename)
        # Generate signed URL (1 hour)
        url = blob.generate_signed_url(expiration=3600)
        return url

    def delete_video(self, video_id: str) -> bool:
        info = self.get_video_info(video_id)
        if not info:
            return False
        filename = info.get('filepath') or info.get('filename')
        blob = self.bucket.blob(filename)
        blob.delete()
        self.collection.document(video_id).delete()
        return True

    def update_metadata(self, video_id: str, updates: Dict) -> Optional[Dict]:
        doc_ref = self.collection.document(video_id)
        doc_ref.update(updates)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None

    def create_blank_video(self, topic: str, duration: int = 10) -> bytes:
        return (
            b'\x00\x00\x00\x20ftypisom\x00\x00\x00\x00'
            b'isomiso2avc1mp41\x00\x00\x00\x00'
            b'mdat' + b'\x00' * 100
        )


def create_firebase_storage_if_configured() -> Optional[FirebaseStorage]:
    # Only initialize if env vars present and libraries available
    if os.getenv('FIREBASE_STORAGE_BUCKET') and (gcs is not None and firestore is not None):
        try:
            store = FirebaseStorage()
            # quick write test to detect billing/permission issues
            try:
                test_blob = store.bucket.blob("__ytagents_test.txt")
                test_blob.upload_from_string(b"ok", content_type="text/plain")
                test_blob.delete()
            except Exception as exc:
                # if upload fails (e.g. 403 billing), warn and disable firebase
                print("⚠️  Firebase write test failed; disabling Firebase backend")
                print(f"   error: {exc}")
                return None
            return store
        except Exception as e:
            print(f"⚠️  Could not initialize FirebaseStorage: {e}")
    return None
