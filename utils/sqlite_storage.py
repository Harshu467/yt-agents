"""
SQLite-backed video storage adapter.

This provides a zero-config database for metadata while still storing
video files on the local filesystem (in `Config.VIDEOS_DIR`). It's used
when no remote backend (S3 or Supabase) is configured.
"""
import os
import sqlite3
from datetime import datetime
from typing import Optional, Dict, List
from config import Config


class SQLiteStorage:
    def __init__(self, db_path: Optional[str] = None):
        self.videos_dir = Config.VIDEOS_DIR
        os.makedirs(self.videos_dir, exist_ok=True)
        self.db_path = db_path or os.path.join(self.videos_dir, "videos.db")
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._ensure_table()

    def _ensure_table(self):
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS videos (
                id TEXT PRIMARY KEY,
                filename TEXT,
                filepath TEXT,
                topic TEXT,
                duration REAL,
                created_at TEXT,
                status TEXT,
                file_size INTEGER,
                playable INTEGER,
                url TEXT,
                youtube_id TEXT
            )
            """
        )
        self._conn.commit()

    def save_video(self, video_data: bytes, topic: str, duration: float = 0) -> Dict:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic[:30] if c.isalnum() or c in '-_ ')
        filename = f"{safe_topic}_{timestamp}.mp4"
        filepath = os.path.join(self.videos_dir, filename)

        with open(filepath, 'wb') as f:
            f.write(video_data)

        video_id = timestamp
        created_at = datetime.now().isoformat()
        url = f"/api/videos/{video_id}"

        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO videos (id, filename, filepath, topic, duration, created_at, status, file_size, playable, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (video_id, filename, filepath, topic, duration, created_at, 'completed', len(video_data), 1, url)
        )
        self._conn.commit()

        return {
            'id': video_id,
            'filename': filename,
            'filepath': filepath,
            'topic': topic,
            'duration': duration,
            'created_at': created_at,
            'status': 'completed',
            'file_size': len(video_data),
            'playable': True,
            'url': url
        }

    def get_video_info(self, video_id: str) -> Optional[Dict]:
        cur = self._conn.cursor()
        cur.execute('SELECT * FROM videos WHERE id = ?', (video_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def get_all_videos(self) -> List[Dict]:
        cur = self._conn.cursor()
        cur.execute('SELECT * FROM videos ORDER BY created_at DESC')
        rows = cur.fetchall()
        return [dict(r) for r in rows]

    def get_video_file(self, video_id: str) -> Optional[str]:
        info = self.get_video_info(video_id)
        if info and os.path.exists(info['filepath']):
            return info['filepath']
        return None

    def delete_video(self, video_id: str) -> bool:
        info = self.get_video_info(video_id)
        if not info:
            return False
        try:
            if os.path.exists(info['filepath']):
                os.remove(info['filepath'])
        except Exception:
            pass
        cur = self._conn.cursor()
        cur.execute('DELETE FROM videos WHERE id = ?', (video_id,))
        self._conn.commit()
        return True

    def update_metadata(self, video_id: str, updates: Dict) -> Optional[Dict]:
        """Update metadata fields for a video and return the updated record."""
        if not updates:
            return self.get_video_info(video_id)
        keys = []
        values = []
        for k, v in updates.items():
            keys.append(f"{k} = ?")
            values.append(v)
        values.append(video_id)
        cur = self._conn.cursor()
        cur.execute(f"UPDATE videos SET {', '.join(keys)} WHERE id = ?", tuple(values))
        self._conn.commit()
        return self.get_video_info(video_id)

    def create_blank_video(self, topic: str, duration: int = 10) -> bytes:
        return (
            b'\x00\x00\x00\x20ftypisom\x00\x00\x00\x00'
            b'isomiso2avc1mp41\x00\x00\x00\x00'
            b'mdat' + b'\x00' * 100
        )


def create_sqlite_storage_if_configured() -> SQLiteStorage:
    # Always available as a local DB fallback
    return SQLiteStorage()
