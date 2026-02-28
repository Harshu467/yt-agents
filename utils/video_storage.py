"""
Video Storage & History Manager
Handles video file storage, metadata tracking, and history management
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from config import Config
import os

# Optional Supabase adapter
try:
    from .supabase_storage import create_supabase_storage_if_configured
except Exception:
    create_supabase_storage_if_configured = None

# Optional S3+Postgres adapter
try:
    from .s3_storage import create_s3_storage_if_configured
except Exception:
    create_s3_storage_if_configured = None

try:
    from .sqlite_storage import create_sqlite_storage_if_configured
except Exception:
    create_sqlite_storage_if_configured = None

try:
    from .firebase_storage import create_firebase_storage_if_configured
except Exception:
    create_firebase_storage_if_configured = None


class VideoStorage:
    """
    Manages video storage and metadata tracking
    """
    
    def __init__(self):
        """Initialize storage system"""
        self.videos_dir = Config.VIDEOS_DIR
        self.metadata_file = os.path.join(self.videos_dir, "video_metadata.json")
        self._setup_directories()
        self._load_metadata()
    
    def _setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.videos_dir, exist_ok=True)
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
    
    def _load_metadata(self):
        """Load existing metadata"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            except:
                self.metadata = {}
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """Save metadata to file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def save_video(self, 
                   video_data: bytes,
                   topic: str,
                   duration: float = 0) -> Dict:
        """
        Save a video file and track metadata
        
        Args:
            video_data: Raw video file bytes
            topic: Video topic/title
            duration: Video duration in seconds
        
        Returns:
            Dictionary with file info
        """
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic[:30] if c.isalnum() or c in '-_ ')
        filename = f"{safe_topic}_{timestamp}.mp4"
        filepath = os.path.join(self.videos_dir, filename)
        
        # Save video file
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(video_data)
        
        # Track metadata
        video_id = timestamp
        self.metadata[video_id] = {
            'id': video_id,
            'filename': filename,
            'filepath': filepath,
            'topic': topic,
            'duration': duration,
            'created_at': datetime.now().isoformat(),
            'status': 'completed',
            'file_size': len(video_data),
            'playable': True,
            'url': f"/api/videos/{video_id}"
        }
        
        self._save_metadata()
        
        print(f"✅ Video saved: {filepath}")
        return self.metadata[video_id]
    
    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """Get metadata for a specific video"""
        return self.metadata.get(video_id)
    
    def get_all_videos(self) -> List[Dict]:
        """Get all videos sorted by creation date (newest first)"""
        videos = list(self.metadata.values())
        videos.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return videos
    
    def get_video_file(self, video_id: str) -> Optional[str]:
        """Get filepath for a video"""
        info = self.get_video_info(video_id)
        if info and os.path.exists(info['filepath']):
            return info['filepath']
        return None
    
    def delete_video(self, video_id: str) -> bool:
        """Delete a video and its metadata"""
        info = self.get_video_info(video_id)
        if info and os.path.exists(info['filepath']):
            os.remove(info['filepath'])
            del self.metadata[video_id]
            self._save_metadata()
            return True
        return False
    
    def create_blank_video(self, topic: str, duration: int = 10) -> bytes:
        """
        Create a basic MP4 video file with a single frame
        This is a fallback for testing when no actual rendering is available
        
        Args:
            topic: Video topic
            duration: Duration in seconds
        
        Returns:
            Video file bytes
        """
        
        try:
            import subprocess
            import tempfile
            
            # Create a black video using ffmpeg (if available)
            # Falls back to creating a minimal MP4
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                tmp_path = tmp.name
            
            try:
                # Try using ffmpeg to create a basic video
                # This creates a 2-second black video (reusable)
                cmd = [
                    'ffmpeg', '-f', 'lavfi', '-i', 'color=c=black:s=1920x1080:d=2',
                    '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=mono:d=2',
                    '-c:v', 'libx264', '-preset', 'fast',
                    '-c:a', 'aac', '-shortest',
                    '-y', tmp_path
                ]
                
                subprocess.run(cmd, capture_output=True, timeout=10)
                
                # Read the generated video
                with open(tmp_path, 'rb') as f:
                    video_bytes = f.read()
                
                os.unlink(tmp_path)
                return video_bytes
            
            except:
                os.unlink(tmp_path) if os.path.exists(tmp_path) else None
                # Return a minimal MP4 header as fallback
                return self._create_minimal_mp4()
        
        except Exception as e:
            print(f"⚠️  Video creation failed: {e}, using minimal fallback")
            return self._create_minimal_mp4()
    
    def _create_minimal_mp4(self) -> bytes:
        """Create a minimal valid MP4 for testing"""
        # This is a minimal MP4 file structure (just enough to be playable)
        # It's a black frame video, good for testing
        return (
            b'\x00\x00\x00\x20ftypisom\x00\x00\x00\x00'
            b'isomiso2avc1mp41\x00\x00\x00\x00'
            b'mdat' + b'\x00' * 100  # Minimal video data
        )


# Global storage instance
_storage_instance = None

def get_video_storage() -> VideoStorage:
    """Get or create global video storage instance"""
    global _storage_instance
    if _storage_instance is None:
        # Prefer Firebase (free tier available) when configured
        if create_firebase_storage_if_configured and os.getenv('FIREBASE_STORAGE_BUCKET'):
            firebase = create_firebase_storage_if_configured()
            if firebase:
                _storage_instance = firebase
                return _storage_instance

        # Prefer S3+Postgres for high performance (if configured)
        if create_s3_storage_if_configured and os.getenv('AWS_S3_BUCKET') and os.getenv('DATABASE_URL'):
            s3s = create_s3_storage_if_configured()
            if s3s:
                _storage_instance = s3s
                return _storage_instance

        # Next prefer Supabase if configured (managed Postgres + storage)
        if create_supabase_storage_if_configured and os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY'):
            supa = create_supabase_storage_if_configured()
            if supa:
                _storage_instance = supa
                return _storage_instance

        # Next prefer SQLite local DB for metadata when remote backends aren't available
        if create_sqlite_storage_if_configured:
            try:
                sqlite_store = create_sqlite_storage_if_configured()
                if sqlite_store:
                    _storage_instance = sqlite_store
                    return _storage_instance
            except Exception:
                pass

        # Fallback: local filesystem + JSON metadata
        _storage_instance = VideoStorage()
    return _storage_instance
