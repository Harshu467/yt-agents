"""
10. Scheduler & Upload Agent
Uploads videos to YouTube using YouTube API (completely free)
"""
import os
import pickle
from typing import Optional, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from config import Config
from datetime import datetime, timedelta


class UploadAgent:
    """
    Uploads videos to YouTube using official API:
    - Completely free (YouTube API has free tier)
    - Sets title, description, tags
    - Sets thumbnail
    - Schedules publication
    - Adds to playlists
    
    Requires OAuth setup (one-time)
    """
    
    # YouTube API scopes
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, client_secrets_file: str = "client_secrets.json"):
        """
        Initialize YouTube API client
        
        Args:
            client_secrets_file: Path to OAuth credentials file
        """
        self.client_secrets_file = client_secrets_file
        self.youtube = None
        self._authenticate()
    
    def _authenticate(self) -> bool:
        """
        Authenticate with YouTube API using OAuth
        First time will open browser for authorization
        """
        
        print("🔐 Authenticating with YouTube API...")
        
        # Token file stores user's access and refresh tokens
        token_file = "youtube_token.pickle"
        credentials = None
        
        # Load existing token
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                credentials = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                print("  Refreshing token...")
                credentials.refresh(Request())
            else:
                print("  Opening browser for authorization...")
                print("  (Set up OAuth at: https://console.cloud.google.com)")
                
                if not os.path.exists(self.client_secrets_file):
                    print(f"❌ ERROR: {self.client_secrets_file} not found!")
                    print("Get it from Google Cloud Console:")
                    print("1. Go to https://console.cloud.google.com")
                    print("2. Create OAuth 2.0 credentials (Desktop)")
                    print("3. Download and save as client_secrets.json")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secrets_file,
                        self.SCOPES
                    )
                    credentials = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"❌ Auth error: {str(e)}")
                    return False
        
        # Save credentials for next time
        with open(token_file, 'wb') as token:
            pickle.dump(credentials, token)
        
        # Build YouTube service
        try:
            self.youtube = build('youtube', 'v3', credentials=credentials)
            print("✅ YouTube API authenticated")
            return True
        except Exception as e:
            print(f"❌ YouTube API error: {str(e)}")
            return False
    
    def upload_video(
        self,
        video_file: str,
        title: str,
        description: str,
        tags: list = None,
        thumbnail_file: str = None,
        category_id: str = "27",  # Education
        privacy_status: str = "private",  # private, unlisted, public
        publish_at: Optional[datetime] = None
    ) -> Optional[str]:
        """
        Upload video to YouTube
        
        Args:
            video_file: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            thumbnail_file: Path to custom thumbnail
            category_id: YouTube category ID (27=Education)
            privacy_status: private/unlisted/public
            publish_at: Schedule publication time (datetime)
        
        Returns:
            Video ID if successful, None otherwise
        """
        
        if not self.youtube:
            print("❌ Not authenticated with YouTube")
            return None
        
        if not os.path.exists(video_file):
            print(f"❌ Video file not found: {video_file}")
            return None
        
        print(f"📤 Uploading: {title}")
        
        try:
            # Video metadata
            body = {
                'snippet': {
                    'title': title[:100],  # Max 100 chars
                    'description': description[:5000],  # Max 5000 chars
                    'tags': tags[:30] if tags else [],  # Max 30 tags
                    'categoryId': category_id,
                    'defaultLanguage': 'en',
                    'defaultAudioLanguage': 'en'
                },
                'status': {
                    'privacyStatus': privacy_status
                }
            }
            
            # Schedule publication if provided
            if publish_at:
                body['status']['publishAt'] = publish_at.isoformat() + 'Z'
                body['status']['privacyStatus'] = 'scheduled'
            
            # Upload video
            media = MediaFileUpload(
                video_file,
                chunksize=-1,  # Use single request
                resumable=True,
                mimetype='video/mp4'
            )
            
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            # Handle resumable upload with progress
            response = None
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        print(f"  Upload progress: {progress}%")
                except HttpError as e:
                    print(f"❌ Upload error: {e}")
                    return None
            
            video_id = response['id']
            print(f"✅ Video uploaded! ID: {video_id}")
            
            # Upload thumbnail if provided
            if thumbnail_file and os.path.exists(thumbnail_file):
                self._upload_thumbnail(video_id, thumbnail_file)
            
            return video_id
            
        except HttpError as e:
            print(f"❌ YouTube API error: {e}")
            return None
        except Exception as e:
            print(f"❌ Upload error: {str(e)}")
            return None
    
    def _upload_thumbnail(self, video_id: str, thumbnail_file: str) -> bool:
        """Upload custom thumbnail"""
        
        print(f"  Uploading thumbnail...")
        
        try:
            media = MediaFileUpload(
                thumbnail_file,
                mimetype='image/jpeg'
            )
            
            request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media
            )
            
            request.execute()
            print(f"  ✅ Thumbnail uploaded")
            return True
            
        except Exception as e:
            print(f"  ⚠️  Thumbnail upload failed: {str(e)}")
            return False
    
    def add_to_playlist(
        self,
        video_id: str,
        playlist_id: str
    ) -> bool:
        """
        Add video to playlist
        
        Args:
            video_id: YouTube video ID
            playlist_id: YouTube playlist ID
        
        Returns:
            True if successful
        """
        
        print(f"  Adding to playlist...")
        
        try:
            request = self.youtube.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            )
            
            request.execute()
            print(f"  ✅ Added to playlist")
            return True
            
        except Exception as e:
            print(f"  ⚠️  Playlist addition failed: {str(e)}")
            return False
    
    def create_playlist(self, title: str, description: str = "") -> Optional[str]:
        """
        Create new playlist
        
        Args:
            title: Playlist title
            description: Playlist description
        
        Returns:
            Playlist ID if successful
        """
        
        if not self.youtube:
            return None
        
        print(f"📋 Creating playlist: {title}")
        
        try:
            request = self.youtube.playlists().insert(
                part='snippet,status',
                body={
                    'snippet': {
                        'title': title,
                        'description': description,
                        'defaultLanguage': 'en'
                    },
                    'status': {
                        'privacyStatus': 'public'
                    }
                }
            )
            
            response = request.execute()
            playlist_id = response['id']
            print(f"✅ Playlist created: {playlist_id}")
            return playlist_id
            
        except Exception as e:
            print(f"❌ Playlist creation failed: {str(e)}")
            return None
    
    def schedule_video(
        self,
        video_file: str,
        metadata: Dict,
        publish_delay_hours: int = 24
    ) -> Optional[str]:
        """
        Upload and schedule video for future publication
        
        Args:
            video_file: Path to video
            metadata: Metadata dictionary from MetadataAgent
            publish_delay_hours: Hours from now to publish
        
        Returns:
            Video ID if successful
        """
        
        # Calculate publish time
        publish_time = datetime.utcnow() + timedelta(hours=publish_delay_hours)
        
        return self.upload_video(
            video_file=video_file,
            title=metadata.get('title', 'Untitled'),
            description=metadata.get('description', ''),
            tags=metadata.get('tags', []),
            privacy_status='private',
            publish_at=publish_time
        )


# Setup instructions
def print_setup_instructions():
    """Print YouTube API setup instructions"""
    
    print("""
    📋 YouTube API Setup Instructions:
    
    1. Go to https://console.cloud.google.com
    2. Create a new project
    3. Enable "YouTube Data API v3"
    4. Create OAuth 2.0 credentials:
       - Application type: Desktop application
       - Download as JSON
       - Save as "client_secrets.json" in project root
    5. Run the upload agent - it will open a browser for first-time auth
    
    ✨ All free! YouTube API has unlimited free tier for uploads.
    """)


# Example usage
if __name__ == "__main__":
    print_setup_instructions()
    
    # Example (requires setup)
    # agent = UploadAgent()
    # video_id = agent.upload_video(
    #     video_file="output/videos/final_video.mp4",
    #     title="The Future of AI",
    #     description="Explore the future of artificial intelligence...",
    #     tags=["AI", "Technology", "Future"],
    #     privacy_status="unlisted"
    # )
