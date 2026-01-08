# YT-AGENTS SETUP GUIDE

## 🎯 Your Zero-Cost YouTube Automation System

This is a complete, production-ready system to create and publish YouTube videos **100% FREE**.

## 💰 Cost Breakdown

| Component | Cost | Why |
|-----------|------|-----|
| **LLM (Ollama + Llama2)** | $0 | Runs locally, no cloud costs |
| **Voiceover (Piper TTS)** | $0 | Open-source, offline |
| **AI Images (Stable Diffusion)** | $0 | Free tier via Replicate or local |
| **Stock Videos (Pexels/Pixabay)** | $0 | Free APIs with great footage |
| **Video Editing (FFmpeg)** | $0 | Industry standard, open-source |
| **YouTube Upload** | $0 | YouTube API is free |
| **Analytics** | $0 | YouTube Analytics API is free |
| **TOTAL COST** | **$0** | ✨ Completely Free ✨ |

---

## 🚀 Quick Start (5 minutes)

### 1. Clone & Setup
```bash
cd /workspaces/yt-agents
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install Ollama (The AI Brain)
- Download: https://ollama.ai
- Install and run the app
- In terminal: `ollama pull llama2`
- Keep it running while using YT-Agents

### 3. Install System Tools
```bash
# Linux
sudo apt-get install ffmpeg

# Mac
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### 4. Configure (Optional - Demo Mode Works Without This)
```bash
cp .env.example .env
# Edit .env with your API keys (all optional)
```

### 5. Run It!
```bash
python main.py
```

---

## 📋 What You Get

### 12 Specialized Agents Working Together:

1. **Trend Detector** - Finds viral topics from Twitter, Reddit, YouTube
2. **Research Agent** - Gathers facts, statistics, misconceptions
3. **Script Writer** - Creates engaging, cinematic scripts
4. **Voiceover Generator** - Converts scripts to natural speech
5. **Subtitle Generator** - Creates YouTube-ready captions
6. **Visual Planner** - Plans what visuals each scene needs
7. **Video Generator** - Creates images and fetches stock clips
8. **Video Editor** - Assembles everything into final video
9. **Metadata Agent** - Writes SEO-optimized titles & descriptions
10. **Upload Agent** - Publishes directly to YouTube
11. **Thumbnail Generator** - Creates movie-style thumbnails
12. **Analytics Agent** - Tracks performance and improves algorithm

---

## 🔧 API Keys (All Optional)

### For Trend Detection (Optional)
```
YouTube API: https://console.cloud.google.com
  - Free tier: Unlimited API calls
  - Used for: Trend detection, uploading, analytics

Twitter API: https://developer.twitter.com
  - Free tier: 1,500 tweets/month
  - Used for: Trend detection

Reddit API: https://reddit.com/prefs/apps
  - Free tier: Unlimited
  - Used for: Trend detection
```

### For Stock Assets (Optional)
```
Pexels API: https://www.pexels.com/api
  - Completely free, no limits
  - 1000s of high-quality stock videos

Pixabay API: https://pixabay.com/api
  - Completely free, no limits
  - 1000s of stock videos & images
```

### For AI Images (Optional)
```
Replicate API: https://replicate.com
  - Free $50/month credits
  - Runs Stable Diffusion
  - Or run locally for unlimited free use
```

---

## 📁 Project Structure

```
yt-agents/
├── agents/                    # The 12 agents
│   ├── trend_detector.py     # 1. Finds viral topics
│   ├── research_agent.py     # 2. Research & facts
│   ├── script_writer.py      # 3. Cinematic scripts
│   ├── voiceover_generator.py # 4. AI voices
│   ├── subtitle_generator.py  # 5. Captions
│   ├── visual_planner.py     # 6. Visual planning
│   ├── video_generator.py    # 7. Creates visuals
│   ├── video_editor.py       # 8. Assembles video
│   ├── metadata_agent.py     # 9. SEO metadata
│   ├── upload_agent.py       # 10. YouTube upload
│   ├── thumbnail_generator.py # 11. Movie thumbnails
│   └── analytics_agent.py    # 12. Performance tracking
├── utils/
│   ├── llm_client.py         # Ollama integration
│   ├── video_utils.py        # FFmpeg helpers
│   └── [more utilities]
├── output/                    # Generated videos
│   ├── videos/
│   ├── scripts/
│   ├── voiceovers/
│   ├── subtitles/
│   └── thumbnails/
├── config.py                 # Configuration
├── main.py                   # Main orchestrator
├── .env.example             # Copy to .env
├── requirements.txt         # Dependencies
└── README.md               # This file
```

---

## 💡 How It Works

### The Complete Workflow:

```
1. TREND DETECTION
   ↓ Finds trending topics from social media
   ↓
2. RESEARCH
   ↓ Gathers facts, statistics, misconceptions
   ↓
3. SCRIPT WRITING
   ↓ Creates engaging, viral-optimized script
   ↓
4. VOICEOVER GENERATION
   ↓ Converts script to natural AI voice
   ↓
5. SUBTITLE GENERATION
   ↓ Creates YouTube-ready captions
   ↓
6. VISUAL PLANNING
   ↓ Maps visuals for each scene
   ↓
7. VIDEO GENERATION
   ↓ Creates images and fetches stock footage
   ↓
8. VIDEO EDITING
   ↓ Assembles everything with effects & music
   ↓
9. METADATA GENERATION
   ↓ Creates SEO-optimized title, description, tags
   ↓
10. THUMBNAIL GENERATION
   ↓ Creates cinematic movie-style thumbnail
   ↓
11. UPLOAD TO YOUTUBE
   ↓ Publishes with all metadata
   ↓
12. ANALYTICS & FEEDBACK
   ↓ Tracks performance, improves algorithm
```

---

## 🎬 Example Usage

### Demo Mode (No API Keys Needed)
```python
python main.py
# Select option 3 for demo mode
# Tests all agents with sample data
```

### With Custom Topic
```python
python main.py
# Select option 2
# Enter your topic
# Full workflow with trend detection disabled
```

### With Trend Detection (Requires API Keys)
```python
python main.py
# Select option 1
# Uses real trending topics
# Full end-to-end automation
```

---

## 🛠️ Customization

### Change AI Model
Edit `config.py`:
```python
OLLAMA_MODEL = "neural-chat"  # or any Ollama model
# Run: ollama pull neural-chat
```

### Change Voice
```python
# In voiceover_generator.py
agent = VoiceoverGeneratorAgent(voice="female_us")
```

### Change Video Duration
```python
# In script_writer.py
writer = ScriptWriterAgent(video_duration=900)  # 15 minutes
```

### Change Output Quality
```python
# In config.py
VIDEO_BITRATE = "8000k"  # Higher = better quality, larger file
AUDIO_BITRATE = "192k"
```

---

## 📊 Monitoring & Analytics

The Analytics Agent tracks:
- **CTR** (Click-Through Rate)
- **Watch Time** (How long people watch)
- **Retention** (Where people drop off)
- **Engagement** (Likes, comments, shares)

This feeds back into the Trend Detector to improve topic selection.

---

## 🔒 Privacy & Security

- **All LLM inference is local** - No data sent to cloud
- **API keys are optional** - Demo mode works without them
- **No telemetry** - This system doesn't track anything
- **Open source** - You can inspect and modify everything

---

## ⚡ Performance Tips

### Faster Video Generation
1. Use lower resolution: `VIDEO_RESOLUTION = (1280, 720)`
2. Use faster AI model: `ollama pull neural-chat`
3. Cache stock footage locally

### Better Quality Videos
1. Use higher bitrate: `VIDEO_BITRATE = "12000k"`
2. Use better AI model: `ollama pull mistral`
3. Create custom thumbnails

### Faster Uploads
1. Keep videos under 2GB
2. Use MP4 format (fastest)
3. Upload during off-peak hours

---

## 🐛 Troubleshooting

### Ollama Not Connecting
```
Error: Cannot connect to Ollama

Solution:
1. Install Ollama from https://ollama.ai
2. Run the Ollama app
3. In terminal: ollama serve
4. Keep it running in background
```

### FFmpeg Not Found
```
Error: FFmpeg not found

Solution (Linux):
  sudo apt-get install ffmpeg

Solution (Mac):
  brew install ffmpeg

Solution (Windows):
  Download from https://ffmpeg.org/download.html
```

### API Key Not Working
```
Solution:
1. Check .env file exists
2. Verify key format (no extra spaces)
3. Test key on the provider's website
4. If failing, just run without that API
```

### Out of Memory
```
Solution:
1. Reduce video resolution
2. Use smaller AI model
3. Process videos one at a time
4. Increase system RAM
```

---

## 🚀 Advanced Usage

### Running Multiple Videos
```python
from main import YouTubeAutomationPipeline

pipeline = YouTubeAutomationPipeline()

topics = [
    "AI in Healthcare",
    "Future of Remote Work",
    "Cryptocurrency Explained"
]

for topic in topics:
    pipeline.create_video_workflow(custom_topic=topic)
    # Videos upload automatically
```

### Custom Agent Chain
```python
from agents.research_agent import ResearchAgent
from agents.script_writer import ScriptWriterAgent

research = ResearchAgent()
writer = ScriptWriterAgent()

research_data = research.research_topic("Your Topic")
script = writer.write_script("Your Topic", research_data, style="entertaining")

# Customize further...
```

### Batch Processing
```bash
# Create multiple videos from a list
python -c "
topics = open('topics.txt').readlines()
from main import YouTubeAutomationPipeline
pipeline = YouTubeAutomationPipeline()
for topic in topics:
    pipeline.create_video_workflow(custom_topic=topic.strip())
"
```

---

## 📈 Expected Results

| Metric | Value |
|--------|-------|
| **Video Quality** | Professional (with proper assets) |
| **Time per Video** | 2-4 hours (mostly waiting for processing) |
| **Cost per Video** | $0 |
| **Scalability** | Unlimited (single computer) |
| **Consistency** | Perfect (same process every time) |

---

## 🎓 Learning Resources

- **Ollama Docs**: https://ollama.ai
- **FFmpeg Guide**: https://ffmpeg.org/documentation.html
- **YouTube API**: https://developers.google.com/youtube
- **Stable Diffusion**: https://huggingface.co/CompVis/stable-diffusion-v1-4

---

## 📝 License

MIT License - Use freely, modify, share

---

## 🤝 Contributing

Found a bug? Want to add features? Feel free to contribute!

---

## 💬 Support

- Check `README.md` in root directory
- Review example code in agents/
- Test with demo mode first
- Read error messages carefully

---

## ✨ What Makes This Special

✅ **100% Free** - No paid tools required
✅ **No Cloud Costs** - Everything runs locally
✅ **Offline Capable** - Works without internet (after setup)
✅ **Open Source** - See and modify all code
✅ **Production Ready** - Actually creates real videos
✅ **Scalable** - Create unlimited videos
✅ **Professional** - Cinematic quality output

---

**Built with ❤️ for creators who want to automate without breaking the bank.**

Start creating now: `python main.py`
