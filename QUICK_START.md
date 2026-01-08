# 🚀 QUICK START REFERENCE CARD

## One-Command Setup
```bash
cd /workspaces/yt-agents
python quickstart.py
```

## Three-Step Installation

### 1. Install Ollama (Free AI)
```
Download: https://ollama.ai
Then: ollama pull llama2
Keep running while using system
```

### 2. Install FFmpeg (Free Video Editor)
```bash
# Linux
sudo apt-get install ffmpeg

# Mac
brew install ffmpeg

# Windows
https://ffmpeg.org/download.html
```

### 3. Run System
```bash
python main.py
# Choose option 3 (demo) first
```

---

## 12 AI Agents You Have

| # | Agent | What It Does | Uses |
|---|-------|-------------|------|
| 1 | Trend Detector | Finds viral topics | Twitter, Reddit APIs |
| 2 | Research Agent | Gathers facts & data | Ollama LLM |
| 3 | Script Writer | Creates engaging scripts | Ollama LLM |
| 4 | Voiceover Gen | Converts text to speech | Piper TTS |
| 5 | Subtitle Gen | Creates captions | FFmpeg |
| 6 | Visual Planner | Plans visuals for scenes | Ollama LLM |
| 7 | Video Generator | Creates images/fetches clips | Stable Diffusion + Stock APIs |
| 8 | Video Editor | Assembles final video | FFmpeg |
| 9 | Metadata Agent | SEO title/description | Ollama LLM |
| 10 | Upload Agent | Publishes to YouTube | YouTube API |
| 11 | Thumbnail Gen | Creates movie thumbnails | Stable Diffusion |
| 12 | Analytics Agent | Tracks performance | YouTube Analytics |

---

## 💰 Cost Breakdown

```
AI Models (Ollama)    → $0 (runs locally)
Voice Generation      → $0 (Piper TTS)
Video Editing         → $0 (FFmpeg)
Stock Footage         → $0 (Pexels/Pixabay)
AI Images             → $0 (Replicate free tier)
YouTube Upload        → $0 (free API)

TOTAL: $0 ✨
```

---

## 📋 File Guide

```
agents/              → All 12 AI agents
├── trend_detector.py
├── research_agent.py
├── script_writer.py
├── voiceover_generator.py
├── subtitle_generator.py
├── visual_planner.py
├── video_generator.py
├── video_editor.py
├── metadata_agent.py
├── upload_agent.py
├── thumbnail_generator.py
└── analytics_agent.py

main.py              → Run this to start
config.py            → Configuration
requirements.txt     → Dependencies
.env.example         → Copy to .env for API keys
```

---

## 🎬 Workflow Summary

```
Topic Input
    ↓
[Trend Detection] - Finds viral topics
    ↓
[Research] - Gathers facts
    ↓
[Script] - Creates engaging script
    ↓
[Voiceover] - AI narration
    ↓
[Subtitles] - Auto captions
    ↓
[Visuals] - Images + stock footage
    ↓
[Editing] - Assembles video
    ↓
[Metadata] - SEO optimization
    ↓
[Thumbnail] - Movie-style image
    ↓
[Upload] - Publishes to YouTube
    ↓
VIDEO PUBLISHED ✨
```

---

## 🛠️ Common Commands

```bash
# Test system without API keys
python main.py
# → Choose option 3 (demo mode)

# Create video from custom topic
python main.py
# → Choose option 2
# → Enter topic name

# See all agents
ls -la agents/

# Check dependencies
pip list | grep -E "torch|pydantic|requests"

# View configuration
cat config.py
```

---

## 🔑 Optional API Keys

All are optional. System works without them in demo mode.

```
YouTube:   https://console.cloud.google.com
Twitter:   https://developer.twitter.com
Reddit:    https://reddit.com/prefs/apps
Pexels:    https://www.pexels.com/api
Pixabay:   https://pixabay.com/api
Replicate: https://replicate.com
```

Add them to `.env` file.

---

## 📊 Expected Results

| Metric | Value |
|--------|-------|
| Video Quality | Professional |
| Time per Video | ~80 minutes |
| Cost per Video | $0 |
| Setup Time | ~30 minutes |
| Scalability | Unlimited |

---

## ⚡ Pro Tips

1. **Start with demo mode** to test everything
2. **Keep Ollama running** in background
3. **Use free API keys** from Pexels/Pixabay
4. **Test different topics** to find what works
5. **Monitor analytics** to improve over time

---

## 🐛 If Something Doesn't Work

```
Ollama not connecting?
→ Download from ollama.ai, install & run

FFmpeg not found?
→ sudo apt-get install ffmpeg (Linux)
→ brew install ffmpeg (Mac)

API key not working?
→ Test key on provider's website
→ Remove from .env to skip that feature

Script generation slow?
→ Use faster model: ollama pull neural-chat
→ Change in config.py: OLLAMA_MODEL="neural-chat"
```

---

## 🎯 Your First Video

```bash
# 1. Install Ollama from ollama.ai
# 2. Keep it running
# 3. Run this:

python main.py

# 4. Select option 3 (demo)
# 5. Watch agents work
# 6. Review output
# 7. Try option 2 with custom topic
```

**Your first video is ready in ~2 hours!**

---

## 📚 Documentation

- **README.md** - Overview
- **SETUP.md** - Detailed setup
- **COMPLETE_GUIDE.md** - Everything you need
- **config.py** - Configuration reference
- **agents/** - Code for each agent

---

## 🚀 You're All Set!

```bash
python main.py
```

Select option 3 to test, then:
- Option 2 for custom topic
- Option 1 for full automation (with API keys)

**Start creating now! 🎬✨**

---

**Questions?** See SETUP.md or COMPLETE_GUIDE.md

**Ready to go?** `python main.py`
