"""
Utility functions for video processing
"""
import subprocess
import os
from typing import Tuple


def get_video_duration(video_path: str) -> float:
    """Get duration of video file in seconds"""
    
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1:nokey=1",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
        
    except:
        return 0.0


def get_video_resolution(video_path: str) -> Tuple[int, int]:
    """Get video resolution (width, height)"""
    
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=s=x:p=0",
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        parts = result.stdout.strip().split('x')
        
        return (int(parts[0]), int(parts[1]))
        
    except:
        return (1920, 1080)  # Default


def resize_video(input_path: str, output_path: str, width: int = 1920, height: int = 1080) -> bool:
    """Resize video to specified dimensions"""
    
    print(f"Resizing video to {width}x{height}...")
    
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vf", f"scale={width}:{height}",
            "-y",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Video resized")
            return True
        else:
            print(f"❌ Resize failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def merge_audio_video(video_path: str, audio_path: str, output_path: str) -> bool:
    """Merge audio and video files"""
    
    print(f"Merging audio and video...")
    
    try:
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            "-y",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Merged")
            return True
        else:
            print(f"❌ Merge failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def convert_to_mp4(input_path: str, output_path: str) -> bool:
    """Convert video to MP4 format"""
    
    print(f"Converting to MP4...")
    
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-c:v", "libx264",
            "-preset", "medium",
            "-c:a", "aac",
            "-b:a", "192k",
            "-y",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Converted to MP4")
            return True
        else:
            print(f"❌ Conversion failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
