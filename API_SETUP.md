# 🎬 Real Video Generation Setup Guide

This guide will help you enable **REAL video generation** instead of the placeholder mode.

## 📊 Current Status

When you see this message:
```
"Using placeholder (configure API keys for full video generation)"
```

It means the app is running in **demo mode** without configured APIs. Follow this guide to get real video generation working!

---

## 🎯 Three Ways to Generate Videos (Pick One)

### Option 1: Use Replicate API (Recommended for Beginners) ⭐

**Best for**: First-time users, pay-as-you-go, simple setup

1. **Sign up** (FREE): https://replicate.com
2. **Get your token**:
   - Go to Account → API Tokens
   - Copy your token
3. **Add to your `.env` file**:
   ```bash
   REPLICATE_API_TOKEN=your_token_here
   ```
4. **Restart the app**

**Cost**: FREE tier has 30 runs/month, then $0.00035 per run (very cheap!)

---

### Option 2: Local Stable Diffusion (Best - Completely Free) ✨

**Best for**: Complete control, offline, no API costs

1. **Install the required packages**:
   ```bash
   pip install diffusers torch pillow
   ```

2. **If you have an NVIDIA GPU** (speeds up 10x):
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Add to `.env` file** (optional - shows a helpful message):
   ```bash
   USE_GPU=true
   ```

4. **Restart the app**

Now your video generation will automatically use the local Stable Diffusion model!

**First run**: Downloads ~4GB model (happens only once)  
**Cost**: $0 - Completely free!  
**Speed**: 
- With NVIDIA GPU: ~30 seconds per image
- With CPU: ~2 minutes per image

---

### Option 3: HuggingFace API (Free Alternative)

**Best for**: Simple setup, free tier

1. **Sign up** (FREE): https://huggingface.co
2. **Get token**:
   - Account → Settings → User Access Tokens
   - Create a new token with "api" permission
3. **Install huggingface hub**:
   ```bash
   pip install huggingface-hub
   ```
4. **Add to `.env`**:
   ```bash
   HUGGINGFACE_API_KEY=your_token_here
   ```

**Cost**: FREE tier with usage limits, then cheap

---

## 📹 Stock Video Setup (For Video Backgrounds)

The app can fetch stock videos for visual content. These are completely free!

### Option A: Pexels API (Recommended)

1. **Sign up** (FREE): https://www.pexels.com/api/
2. **Get your key**:
   - Go to API section
   - Copy your API key
3. **Add to `.env`**:
   ```bash
   PEXELS_API_KEY=your_key_here
   ```

### Option B: Pixabay API

1. **Sign up** (FREE): https://pixabay.com/api/docs/
2. **Get your key**:
   - Register → User menu → API
   - Copy your key
3. **Add to `.env`**:
   ```bash
   PIXABAY_API_KEY=your_key_here
   ```

---

## 🧪 Quick Setup Checklist

### Minimal Setup (Video Generation Only)
- [ ] Pick Option 1, 2, or 3 above
- [ ] Configure the API keys in `.env`
- [ ] Restart the Flask app
- [ ] Test by generating a video!

### Full Setup (With Stock Videos)
- [ ] Setup video generation from above
- [ ] Add Pexels API key
- [ ] Add Pixabay API key (optional backup)
- [ ] Restart and generate!

### YouTube Upload (Optional)
- [ ] Go to: https://console.cloud.google.com
- [ ] Create OAuth 2.0 credentials (Desktop type)
- [ ] Download and save as `client_secrets.json`
- [ ] Add to `.env`:
   ```bash
   YOUTUBE_API_KEY=your_key_here
   YOUTUBE_CHANNEL_ID=your_channel_id_here
   ```

---

## 🚀 Test Your Setup

After configuring, test like this:

1. **Start the Flask app**:
   ```bash
   python app.py
   ```

2. **Open in browser**: http://localhost:5000

3. **Login** (default: admin / password123)

4. **Create a new workflow** with a topic

5. **Generate video** and check the console for messages like:
   - ✅ "AI image generated" = Replicate/Local SD working
   - ✅ "Stock video fetched" = Pexels/Pixabay working
   - ⚠️ "Using placeholder" = Still need setup

---

## 🔧 Troubleshooting

### "Using placeholder (configure API keys...)" still shows?

**Check**:
1. Restart the Flask app after adding `.env` values
2. Make sure the `.env` file is in the root directory
3. Check that variable names match exactly (case-sensitive on Linux)
4. Look at console for error messages

### Replicate gives "Rate Limit" error?

You've used up your free 30 runs/month. Either:
- Wait until next month (free tier resets)
- Upgrade to pay-as-you-go (very cheap)
- Use local Stable Diffusion instead

### Local Stable Diffusion is very slow (2+ minutes per image)?

You're using CPU. To use GPU:
1. **Check if you have GPU**:
   ```bash
   nvidia-smi
   ```
2. If yes, install CUDA version of PyTorch:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
3. Add to `.env`:
   ```bash
   USE_GPU=true
   ```

### Can't find Pexels/Pixabay API?

Visit:
- Pexels: https://www.pexels.com/api/ → API section
- Pixabay: https://pixabay.com/api/ → Documentation tab

Both are free, no credit card needed!

---

## 📊 Cost Comparison

| Method | Cost | Setup | Speed | Quality |
|--------|------|-------|-------|---------|
| **Replicate** | $0-cheap | Easy ⭐ | Fast | Excellent |
| **Local SD** | $0 | Medium | Slow | Excellent |
| **HuggingFace** | $0-cheap | Easy | Medium | Good |
| **YouTube Stock** | $0 | Easy | N/A | Free footage |

---

## ✅ After Setup

Once configured, you'll see in the workflow:
- ✅ **Video player** showing generated videos
- ✅ **Real images** from AI (not placeholder text)
- ✅ **Stock video clips** as backgrounds
- ✅ **Full video generation** with 1080p quality

The message will change to show SUCCESS instead of "Using placeholder"!

---

## 📝 Full `.env` Template

```bash
# Video Generation (pick one)
REPLICATE_API_TOKEN=your_token_here
# OR install: pip install diffusers torch

# Stock Videos
PEXELS_API_KEY=your_pexels_key_here
PIXABAY_API_KEY=your_pixabay_key_here

# YouTube Upload (optional)
YOUTUBE_API_KEY=your_api_key_here
YOUTUBE_CHANNEL_ID=your_channel_id_here

# Other Services (optional for trends)
TWITTER_BEARER_TOKEN=your_token_here
REDDIT_CLIENT_ID=your_id_here
REDDIT_CLIENT_SECRET=your_secret_here

# Settings
OUTPUT_DIR=./output
OLLAMA_BASE_URL=http://localhost:11434
USE_GPU=true
```

---

## 🎉 You're Done!

Once setup, video generation will automatically:
1. ✅ Generate AI images for each scene
2. ✅ Fetch relevant stock videos
3. ✅ Add voiceover narration
4. ✅ Add captions and metadata
5. ✅ Create final 1080p video file
6. ✅ Show preview in the player
7. ✅ Upload to YouTube (if configured)

**No more "placeholder" message!** 🚀

