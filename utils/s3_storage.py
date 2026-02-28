"""
S3 + Postgres-backed video storage adapter

Environment variables required for activation:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_REGION (optional)
- AWS_S3_BUCKET
- DATABASE_URL (Postgres connection URL)

This adapter uploads video objects to S3 and stores metadata in Postgres.
"""
import os
import io
from datetime import datetime
from typing import Optional, Dict, List

import boto3
import psycopg2
import psycopg2.extras


class S3PostgresStorage:
    def __init__(self):
        self.bucket = os.getenv('AWS_S3_BUCKET')
        self.region = os.getenv('AWS_REGION') or None
        self.database_url = os.getenv('DATABASE_URL')

        if not self.bucket or not self.database_url:
            raise RuntimeError('AWS_S3_BUCKET and DATABASE_URL environment variables are required for S3PostgresStorage')

        # Initialize S3 client
        session = boto3.session.Session()
        self.s3 = session.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=self.region
        )

        # Initialize Postgres connection
        self.conn = psycopg2.connect(self.database_url)
        self._ensure_table()

    def _ensure_table(self):
        with self.conn.cursor() as cur:
            cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS videos (
                    id TEXT PRIMARY KEY,
                    filename TEXT,
                    filepath TEXT,
                    topic TEXT,
                    duration REAL,
                    created_at TIMESTAMP,
                    status TEXT,
                    file_size INTEGER,
                    playable BOOLEAN,
                    url TEXT
                );
                '''
            )
            self.conn.commit()

    def save_video(self, video_data: bytes, topic: str, duration: float = 0) -> Dict:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_topic = ''.join(c for c in topic[:30] if c.isalnum() or c in '-_ ')
        filename = f"{safe_topic}_{timestamp}.mp4"
        key = filename

        # Upload to S3
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=video_data, ContentType='video/mp4')

        # Presigned URL (1 hour)
        url = self.s3.generate_presigned_url('get_object', Params={'Bucket': self.bucket, 'Key': key}, ExpiresIn=3600)

        # Insert metadata into Postgres
        video_id = timestamp
        created_at = datetime.utcnow()
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                '''INSERT INTO videos (id, filename, filepath, topic, duration, created_at, status, file_size, playable, url)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   ON CONFLICT (id) DO NOTHING
                   RETURNING *;''',
                (video_id, filename, key, topic, duration, created_at, 'completed', len(video_data), True, url)
            )
            row = cur.fetchone()
            self.conn.commit()

        return dict(row) if row else {
            'id': video_id,
            'filename': filename,
            'filepath': key,
            'topic': topic,
            'duration': duration,
            'created_at': created_at.isoformat(),
            'status': 'completed',
            'file_size': len(video_data),
            'playable': True,
            'url': url
        }

    def get_video_info(self, video_id: str) -> Optional[Dict]:
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('SELECT * FROM videos WHERE id = %s;', (video_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_all_videos(self) -> List[Dict]:
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute('SELECT * FROM videos ORDER BY created_at DESC;')
            return list(cur.fetchall())

    def get_video_file(self, video_id: str) -> Optional[str]:
        info = self.get_video_info(video_id)
        if not info:
            return None
        key = info.get('filepath') or info.get('filename')
        url = self.s3.generate_presigned_url('get_object', Params={'Bucket': self.bucket, 'Key': key}, ExpiresIn=3600)
        return url

    def delete_video(self, video_id: str) -> bool:
        info = self.get_video_info(video_id)
        if not info:
            return False
        key = info.get('filepath') or info.get('filename')
        self.s3.delete_object(Bucket=self.bucket, Key=key)
        with self.conn.cursor() as cur:
            cur.execute('DELETE FROM videos WHERE id = %s;', (video_id,))
            self.conn.commit()
        return True

    def update_metadata(self, video_id: str, updates: Dict) -> Optional[Dict]:
        """Update metadata fields in Postgres for a given video id."""
        if not updates:
            return self.get_video_info(video_id)
        fields = []
        values = []
        for k, v in updates.items():
            fields.append(f"{k} = %s")
            values.append(v)
        values.append(video_id)
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"UPDATE videos SET {', '.join(fields)} WHERE id = %s RETURNING *;", tuple(values))
            row = cur.fetchone()
            self.conn.commit()
            return dict(row) if row else None

    def create_blank_video(self, topic: str, duration: int = 10) -> bytes:
        return (
            b'\x00\x00\x00\x20ftypisom\x00\x00\x00\x00'
            b'isomiso2avc1mp41\x00\x00\x00\x00'
            b'mdat' + b'\x00' * 100
        )


def create_s3_storage_if_configured() -> Optional[S3PostgresStorage]:
    if os.getenv('AWS_S3_BUCKET') and os.getenv('DATABASE_URL'):
        try:
            return S3PostgresStorage()
        except Exception as e:
            print(f"⚠️  Could not initialize S3PostgresStorage: {e}")
    return None
