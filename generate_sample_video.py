#!/usr/bin/env python3
"""
Generate a sample YouTube video as an example result.
Uses moviepy to create a 30-second video with text and color.
"""
import os
import sys
from pathlib import Path

try:
    from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip
except ImportError:
    print("Installing moviepy...")
    os.system("pip install -q moviepy")
    from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, concatenate_videoclips

def create_sample_video():
    """Create a sample YouTube video example"""
    output_dir = Path("/workspaces/yt-agents/example_results")
    output_dir.mkdir(exist_ok=True)
    
    video_path = output_dir / "sample_video_ai_future.mp4"
    
    print(f"🎬 Creating sample video: {video_path}")
    
    # Create a colorful background
    width, height = 1280, 720
    fps = 30
    duration = 30  # 30 seconds
    
    # Scene 1: Title (0-10s)
    bg1 = ColorClip(size=(width, height), color=(15, 23, 42))  # Dark blue
    title = TextClip(
        "The Future of AI in 2025",
        fontsize=70,
        font="Arial-Bold",
        color="white",
        method="caption",
        size=(width-100, None)
    )
    title = title.set_position("center").set_duration(10)
    scene1 = CompositeVideoClip([bg1.set_duration(10), title])
    
    # Scene 2: Subtitle (10-20s)
    bg2 = ColorClip(size=(width, height), color=(30, 58, 138))  # Medium blue
    subtitle = TextClip(
        "Revolutionary Breakthroughs in AI Technology",
        fontsize=50,
        font="Arial",
        color="white",
        method="caption",
        size=(width-100, None)
    )
    subtitle = subtitle.set_position("center").set_duration(10)
    scene2 = CompositeVideoClip([bg2.set_duration(10), subtitle])
    
    # Scene 3: Key Points (20-30s)
    bg3 = ColorClip(size=(width, height), color=(59, 130, 246))  # Bright blue
    points = TextClip(
        "✓ Advanced Reasoning Models\n✓ Multimodal AI\n✓ Open-Source Innovation\n✓ Ethical Frameworks",
        fontsize=40,
        font="Arial",
        color="white",
        method="caption",
        size=(width-100, None)
    )
    points = points.set_position("center").set_duration(10)
    scene3 = CompositeVideoClip([bg3.set_duration(10), points])
    
    # Concatenate all scenes
    video = concatenate_videoclips([scene1, scene2, scene3])
    
    # Write video file
    print("  ✓ Rendering video (this may take a minute)...")
    video.write_videofile(
        str(video_path),
        fps=fps,
        codec='libx264',
        audio=False,
        verbose=False,
        logger=None
    )
    
    print(f"  ✓ Video created successfully!")
    print(f"\n📊 Video Properties:")
    print(f"  • Resolution: 1280x720 (HD)")
    print(f"  • Duration: 30 seconds")
    print(f"  • Frame Rate: 30 fps")
    print(f"  • Codec: H.264")
    print(f"  • File: {video_path}")
    print(f"  • Size: {os.path.getsize(video_path) / (1024*1024):.2f} MB")
    
    return str(video_path)

if __name__ == "__main__":
    try:
        video_file = create_sample_video()
        print(f"\n✅ Sample video ready at: {video_file}")
    except Exception as e:
        print(f"❌ Error creating video: {e}")
        print("  Trying alternative method...")
        # Fallback: create minimal MP4 using ffmpeg
        os.system("python /workspaces/yt-agents/create_minimal_video.py")
