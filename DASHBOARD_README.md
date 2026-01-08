# YouTube Video Automation Dashboard

A beautiful web interface for creating YouTube videos with step-by-step approval workflow.

## 🚀 Features

- **Interactive Dashboard** - User-friendly web interface
- **Step-by-Step Workflow** - 5 stages with approval gates:
  1. **Research** - Gather data and insights
  2. **Script** - Generate video script
  3. **Metadata** - Create SEO-optimized YouTube metadata
  4. **Video** - Generate video file
  5. **Upload** - Publish to YouTube

- **Approval System** - Review and approve/reject each step before moving forward
- **Live Preview** - See generated content before approval
- **Progress Tracking** - Visual progress bar showing completion status
- **One-Click Upload** - Final upload to YouTube when all steps are approved

## 🌐 How to Use

### Start the Server

```bash
python app.py
```

The dashboard will be available at:
- **Local:** http://localhost:5000
- **Network:** http://10.0.1.126:5000 (or your server IP)

### Workflow Steps

1. **Enter Topic** - Type your video topic (e.g., "The Future of AI in 2025")
2. **Generate Research** - Click "Generate" to research the topic
   - Review the summary and key points
   - Click **✓ Approve** to continue
3. **Write Script** - System generates video script
   - Review intro, segments, and outro
   - Click **✓ Approve** to continue
4. **Create Metadata** - Generate YouTube title, description, tags
   - Review SEO-optimized content
   - Click **✓ Approve** to continue
5. **Generate Video** - Create video file
   - Review video properties
   - Click **✓ Approve** to continue
6. **Upload to YouTube** - Click the big **📤 Upload** button
   - Confirm upload in popup
   - Video publishes to YouTube

## 📋 Features Detail

### Research Agent
- Gathers relevant information about topic
- Identifies key points
- Finds sources and references

### Script Writer
- Creates engaging video intro
- Generates content segments
- Writes compelling outro

### Metadata Agent
- Optimizes YouTube title (60 chars)
- Creates SEO-rich description
- Generates relevant tags and keywords

### Video Generator
- Creates video from script
- Adds visuals and effects
- Exports in MP4 format

### Upload Agent
- Handles YouTube API authentication
- Publishes video to channel
- Sets metadata and privacy settings

## 🔧 Configuration

### Environment Variables (.env)

```bash
# YouTube API
YOUTUBE_API_KEY=your_youtube_api_key

# Ollama (Local LLM)
OLLAMA_API_URL=http://localhost:11434

# Replicate (Image Generation)
REPLICATE_API_TOKEN=your_replicate_token

# NVidia (Optional LLM Provider)
NVIDEO_ENABLED=false
NVIDEO_API_URL=your_nvideo_endpoint
NVIDEO_MODEL_NAME=nvideo-small
```

### Required Services

- **Ollama** (for LLM) - Install from https://ollama.ai
  ```bash
  ollama pull llama2
  ollama serve
  ```

- **YouTube API** - Set up from Google Cloud Console
- **Replicate** (optional) - For image generation

## 🎨 UI Highlights

- **Modern Design** - Gradient backgrounds, smooth animations
- **Responsive Layout** - Works on desktop and tablet
- **Real-time Updates** - Auto-refresh every 2 seconds
- **Status Indicators** - Visual status for each step
- **Progress Bar** - Overall workflow completion
- **Example Topics** - Quick start with pre-filled topics

## 📊 Workflow States

Each step can be in one of these states:

- **Pending** 🟡 - Waiting to be generated
- **Completed** 🟢 - Generated and ready for review
- **Approved** 🔵 - Approved and moving to next step
- **Rejected** 🔴 - Rejected, needs to be regenerated
- **Uploaded** ✅ - Successfully uploaded to YouTube

## 🔄 Workflow Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Dashboard (index.html)             │
│  Enter Topic → Start Workflow → Get workflow_id     │
└─────────────┬───────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────┐
│            Workflow Dashboard (workflow.html)        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │Research  │→ │ Script   │→ │Metadata  │→ Video    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  Upload   │
│       │ Approve     │ Approve      │ Approve         │
│       └─────────────┴──────────────┴─────────────────┘
│              All Steps Approved → Upload Button      │
└─────────────────────────────────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────────────────┐
│            Final Upload to YouTube                  │
│  Title, Description, Tags → Video File → YouTube    │
└─────────────────────────────────────────────────────┘
```

## 🚀 API Endpoints

### Start Workflow
```
POST /start-workflow
Body: { "topic": "Your Video Topic" }
Response: { "workflow_id": "abc123", "topic": "..." }
```

### Generate Step
```
POST /api/workflow/{workflow_id}/step/{step}
Response: { "status": "success", "data": {...} }
```

### Approve Step
```
POST /api/workflow/{workflow_id}/approve/{step}
Response: { "status": "approved", "next_step": "..." }
```

### Reject Step
```
POST /api/workflow/{workflow_id}/reject/{step}
Response: { "status": "rejected" }
```

### Upload Video
```
POST /api/workflow/{workflow_id}/upload
Response: { "status": "uploaded", "video_id": "..." }
```

### Workflow Summary
```
GET /api/workflow/{workflow_id}/summary
Response: { "id": "...", "topic": "...", "steps": {...} }
```

## 💾 Data Storage

Workflows are stored in memory during the session. For production:
- Use a database (PostgreSQL, MongoDB)
- Store generated content to disk
- Implement session persistence

## 📝 Example Workflow

```
1. User enters: "The Future of AI in 2025"
2. Research Agent runs → Finds key insights
3. User approves research
4. Script Writer creates script
5. User approves script
6. Metadata Agent optimizes for YouTube
7. User approves metadata
8. Video Generator creates MP4
9. User approves video
10. User clicks Upload
11. Video published to YouTube! 🎉
```

## 🎯 Next Steps

- [ ] Add database support for persistent storage
- [ ] Implement real YouTube upload with OAuth
- [ ] Add video preview in dashboard
- [ ] Support batch video creation
- [ ] Add analytics dashboard
- [ ] Email notifications on completion
- [ ] Team collaboration features

## 📞 Support

For issues or questions:
1. Check agent logs in terminal
2. Verify .env configuration
3. Ensure services are running (Ollama, YouTube API)
4. Check Flask console for errors

---

**Created with ❤️ for YouTube creators**
