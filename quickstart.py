#!/usr/bin/env python3
"""
Quick start script - Interactive setup
"""
import os
import sys

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def main():
    print_header("YT-AGENTS: FREE YouTube Automation")
    
    print("""
This system creates faceless YouTube videos COMPLETELY FREE using:
- Ollama (Local LLM)
- Piper TTS (Voice)
- Stable Diffusion (Images)
- FFmpeg (Video Editing)
- Free APIs (Pexels, Pixabay, YouTube)

NO PAID TOOLS REQUIRED!
    """)
    
    print_header("System Requirements")
    
    print("""
Required (Free):
  ✓ Python 3.8+
  ✓ FFmpeg (video editing)
  ✓ Ollama (local AI) - https://ollama.ai
  ✓ Piper TTS (voice) - pip install piper-tts
  
Optional (Free API Tiers):
  ✓ YouTube API key
  ✓ Pexels API key
  ✓ Pixabay API key
  ✓ Twitter/Reddit API keys
    """)
    
    response = input("Continue with setup? (y/n): ").lower()
    if response != 'y':
        return
    
    print_header("Installation")
    
    # Install dependencies
    print("\n1. Installing Python dependencies...")
    os.system("pip install -r requirements.txt")
    
    print("\n2. Installing Piper TTS...")
    os.system("pip install piper-tts")
    
    print("\n3. Checking FFmpeg...")
    result = os.system("ffmpeg -version > /dev/null 2>&1")
    if result != 0:
        print("⚠️  FFmpeg not found. Install with:")
        print("   Linux: sudo apt-get install ffmpeg")
        print("   Mac: brew install ffmpeg")
        print("   Windows: https://ffmpeg.org/download.html")
    else:
        print("✅ FFmpeg found")
    
    print_header("Ollama Setup")
    
    print("""
Ollama is required for local, offline AI (free!):

1. Download from: https://ollama.ai
2. Install and run the application
3. In terminal, run: ollama pull llama2
4. Leave it running while using YT-Agents

This downloads a 4GB model (one-time only).
Then you have unlimited FREE AI!
    """)
    
    response = input("Is Ollama installed and running? (y/n): ").lower()
    
    if response == 'y':
        print("✅ Good! We'll test the connection when you run main.py")
    else:
        print("⚠️  Install Ollama from https://ollama.ai and come back")
        return
    
    print_header("Configuration")
    
    # Create .env if needed
    if not os.path.exists('.env'):
        os.system("cp .env.example .env")
        print("✅ Created .env file")
    else:
        print("ℹ️  .env file already exists")
    
    print("""
Edit .env with your API keys (all optional):
  - YouTube API: https://console.cloud.google.com
  - Pexels: https://www.pexels.com/api
  - Pixabay: https://pixabay.com/api
  - Twitter: https://developer.twitter.com
  - Reddit: https://reddit.com/prefs/apps
  
RUN WITHOUT KEYS FOR DEMO MODE!
    """)
    
    print_header("Ready to Go!")
    
    print("""
✅ Setup complete!

To start creating videos:
  python main.py

This will:
1. Test all agents
2. Detect trends (needs API keys)
3. Research topics
4. Write scripts using AI
5. Generate voiceovers
6. Create metadata & thumbnails

Questions? See README.md for details!
    """)

if __name__ == "__main__":
    main()
