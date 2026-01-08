"""
Configuration management for YT-Agents
"""
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Main configuration class"""
    
    # LLM Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")
    
    # TTS Configuration
    TTS_ENGINE: str = os.getenv("TTS_ENGINE", "piper")
    TTS_VOICE: str = os.getenv("TTS_VOICE", "en_US-lessac-medium")
    
    # YouTube API
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    YOUTUBE_CHANNEL_ID: str = os.getenv("YOUTUBE_CHANNEL_ID", "")
    
    # Twitter/X API
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    
    # Reddit API
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    
    # Pexels API
    PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")
    
    # Pixabay API
    PIXABAY_API_KEY: str = os.getenv("PIXABAY_API_KEY", "")
    
    # Replicate API (for Stable Diffusion - has free tier)
    REPLICATE_API_TOKEN: Optional[str] = os.getenv("REPLICATE_API_TOKEN")
    
    # NVidia / "nvideo" model support (optional, free/local if available)
    # Set NVIDEO_ENABLED=true to enable a custom nvideo endpoint
    NVIDEO_ENABLED: bool = os.getenv("NVIDEO_ENABLED", "false").lower() in ("1", "true", "yes")
    NVIDEO_API_URL: Optional[str] = os.getenv("NVIDEO_API_URL")
    NVIDEO_MODEL_NAME: Optional[str] = os.getenv("NVIDEO_MODEL_NAME", "nvideo-small")
    
    # Video Generation Settings
    VIDEO_DURATION: int = 600  # 10 minutes default
    VIDEO_FPS: int = 30
    VIDEO_RESOLUTION: tuple = (1920, 1080)  # 1080p
    
    # Output Directories
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./output")
    TEMP_DIR: str = os.path.join(OUTPUT_DIR, "temp")
    VIDEOS_DIR: str = os.path.join(OUTPUT_DIR, "videos")
    SCRIPTS_DIR: str = os.path.join(OUTPUT_DIR, "scripts")
    VOICEOVERS_DIR: str = os.path.join(OUTPUT_DIR, "voiceovers")
    THUMBNAILS_DIR: str = os.path.join(OUTPUT_DIR, "thumbnails")
    
    # Trend Detection Settings
    TRENDING_CHECK_INTERVAL: int = 3600  # 1 hour
    MIN_TREND_SCORE: float = 0.7
    
    # Video Quality Settings
    VIDEO_BITRATE: str = "8000k"  # High quality
    AUDIO_BITRATE: str = "192k"
    
    @staticmethod
    def create_directories():
        """Create all necessary output directories"""
        dirs = [
            Config.OUTPUT_DIR,
            Config.TEMP_DIR,
            Config.VIDEOS_DIR,
            Config.SCRIPTS_DIR,
            Config.VOICEOVERS_DIR,
            Config.THUMBNAILS_DIR,
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    @staticmethod
    def validate():
        """Validate critical configuration"""
        if not Config.YOUTUBE_API_KEY:
            print("⚠️  WARNING: YOUTUBE_API_KEY not set. Upload functionality will be disabled.")
        if not Config.OLLAMA_BASE_URL:
            print("⚠️  WARNING: OLLAMA_BASE_URL not set. Please install Ollama from https://ollama.ai")
