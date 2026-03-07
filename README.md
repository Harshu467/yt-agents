# YT-Agents: Automated Faceless YouTube Channel (100% Free)

A complete multi-agent system to automate YouTube video creation from trend detection to publishing.

## 🎯 Architecture

```
Trend Detector → Research Agent → Script Writer → Voice Agent → Subtitles Agent
                                                        ↓
                                                  Visual Planner
                                                        ↓
                                                  Video Generator
                                                        ↓
                                                  Video Editor
                                                        ↓
                                                  Metadata Agent → Upload Agent
                                                        ↓
                                                  Analytics Feedback Loop
```

## 🛠️ Free Tools Stack

| Component | Free Tool | Cost |
|-----------|-----------|------|
| **LLM/AI** | Ollama (Local) + Llama2 | $0 |
| **LLM/AI (alt)** | NVidia NeMo / nvideo (local) | $0 |
| **Voiceover** | Piper TTS / Coqui TTS | $0 |
| **Image Generation** | Stable Diffusion (Local/Replicate Free) | $0 |
| **Stock Videos** | Pexels, Pixabay, Unsplash APIs | $0 |
| **Video Editing** | FFmpeg | $0 |
| **Video Upload** | YouTube API (Free Tier) | $0 |
| **Trends** | Twitter, Reddit, YouTube APIs | $0 |
| **Analytics** | YouTube Analytics API | $0 |

## 📁 Project Structure

```
yt-agents/
├── agents/
│   ├── trend_detector.py
│   ├── research_agent.py
│   ├── script_writer.py
│   ├── voiceover_generator.py
│   ├── subtitle_generator.py
│   ├── visual_planner.py
│   ├── video_generator.py
│   ├── video_editor.py
│   ├── metadata_agent.py
│   ├── upload_agent.py
│   ├── thumbnail_generator.py
│   └── analytics_agent.py
├── utils/
│   ├── llm_client.py
│   ├── youtube_api.py
│   ├── video_utils.py
│   ├── tts_utils.py
│   └── stock_footage.py
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
ollama pull llama2
```

### 2. Set Up APIs (All Free)
- YouTube API key (free, unlimited requests)
- Twitter API v2 (free tier)
- Reddit API (free)
- Pexels API key (free)
- Pixabay API key (free)

### 3. Configure
Edit `config.py` with your API keys.

### 4. Run
```bash
python main.py
```

## 👥 Agent Roles

### 🔍 1. Trend Detector Agent
- Finds trending topics from Twitter, Reddit, YouTube
- Analyzes viral potential
- Ranks by potential views

### 📚 2. Research & Context Agent
- Expands topic with facts using Ollama + web search
- Extracts key points, timeline, misconceptions
- Provides sources

### ✍️ 3. Script Writer Agent
- Converts research into cinematic script
- Creates hook, body, CTA
- Scene-by-scene breakdown

### 🎙️ 4. Voiceover Generator Agent
- Converts script to speech using Piper TTS
- Adjusts tone, pace, emphasis
- Generates multiple voice options

### 📝 5. Subtitle & Timestamp Agent
- Generates SRT files
- Time-coded captions
- Hardcoded subtitle text

### 🎨 6. Visual Scene Planner Agent
- Maps script scenes to visual types
- Suggests animations, stock clips, infographics
- Creates visual storyboard

### 🎬 7. Video Generator Agent
- Generates images using Stable Diffusion
- Fetches stock videos from Pexels/Pixabay
- Creates motion graphics

### 🎞️ 8. Video Editing Agent
- Assembles video using FFmpeg
- Adds music (YouTube Audio Library - free)
- Adds captions, transitions, effects

### 🏷️ 9. Metadata & SEO Agent
- Generates title, description
- Creates keywords, hashtags
- Generates thumbnail text

### 📤 10. Scheduler & Upload Agent
- Uploads to YouTube via API
- Sets thumbnail, tags
- Schedules publication

### 🎬 11. Thumbnail Generator Agent
- Creates AI-powered thumbnails
- Uses Stable Diffusion
- Movie-style design

### 📊 12. Analytics & Feedback Agent
- Tracks performance metrics
- Identifies best topics
- Feeds insights back to Trend Detector

## ⚡ Zero-Cost Implementation Details

### Why Ollama?
- Llama2 is free and runs locally
- No API costs, unlimited usage
- Decent quality for agent tasks

### Why Piper TTS?
- Completely free, open-source
- Offline capable
- Sounds natural

### Why Stable Diffusion?
- Free via Replicate or locally
- High-quality AI images
- Perfect for thumbnails

### Why FFmpeg?
- Industry standard, completely free
- Handles all video formats
- Scriptable CLI

## 🔧 Configuration Example

```python
# config.py
OLLAMA_MODEL = "llama2"
TTS_ENGINE = "piper"
VIDEO_GENERATOR = "stable_diffusion"
STOCK_FOOTAGE_SOURCES = ["pexels", "pixabay", "unsplash"]
YOUTUBE_API_KEY = "your-key-here"
TWITTER_BEARER_TOKEN = "your-token-here"
REDDIT_CLIENT_ID = "your-id-here"
```

## 💡 Workflow Example

1. Trend Detector finds "Top 10 AI Secrets"
2. Research Agent gathers facts
3. Script Writer creates 10-minute script
4. Voiceover Generator creates narration
5. Visual Planner maps scenes
6. Video Generator creates images/fetches clips
7. Video Editor assembles everything
8. Metadata Agent creates title & description
9. Upload Agent publishes to YouTube
10. Analytics Agent tracks performance

## 🎯 Expected Output

- **Video Quality**: Good (with proper assets)
- **Time to Production**: 2-4 hours (from trend to upload)
- **Cost**: $0
- **Scalability**: Unlimited videos

## 📚 Dependencies

All completely free and open-source:
- `ollama` - Local LLM
- `piper-tts` - Text-to-speech
- `ffmpeg-python` - Video editing
- `pillow` - Image processing
- `requests` - API calls
- `google-auth` - YouTube API auth
- `tweepy` - Twitter API
- `praw` - Reddit API

## � Troubleshooting

### Supabase Upload Errors

If you see "Failed to upload video to Supabase storage":

1. **Quick Fix:** Run the validation script
   ```bash
   python3 scripts/validate_supabase.py
   ```

2. **Quick Reference:** See [SUPABASE_ERROR_QUICK_FIX.md](SUPABASE_ERROR_QUICK_FIX.md)

3. **Full Guide:** See [SUPABASE_TROUBLESHOOTING.md](SUPABASE_TROUBLESHOOTING.md)

### Schema Migrations Error

If you see `relation "supabase_migrations.schema_migrations" does not exist`:

1. **Setup videos table:**
   ```bash
   python3 scripts/setup_supabase_table.py
   ```

2. **Then follow the SQL guidance shown**

3. **Check status:**
   ```bash
   python3 scripts/setup_supabase_table.py --status
   ```

See [SUPABASE_SCHEMA_MIGRATIONS_ERROR.md](SUPABASE_SCHEMA_MIGRATIONS_ERROR.md) for details.

### Common Issues

- **Missing credentials** → Set `SUPABASE_URL` and `SUPABASE_KEY`
- **Bucket doesn't exist** → Create "videos" bucket in Storage
- **Wrong key type** → Use "service_role" key, not "anon"
- **Videos table missing** → Run `python3 scripts/setup_supabase_table.py`
- **Permission denied** → Make bucket public or configure RLS

## �🚧 Current Status

- [x] Project structure
- [ ] Agent implementations
- [ ] API integrations
- [ ] Workflow orchestration
- [ ] Testing & optimization

## 📝 License

MIT

---

**Built for creators who want to automate without spending a dime.**