# 🚀 Deployment Guide for YouTube Automation Dashboard

## Quick Deployment Options

### Option 1: Deploy to Render.com (Recommended - Free)

#### Step 1: Push Code to GitHub
```bash
cd /workspaces/yt-agents
git add .
git commit -m "Add deployment configuration files"
git push origin main
```

#### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Click "Sign Up"
3. Connect your GitHub account
4. Authorize Render to access your repositories

#### Step 3: Deploy from GitHub
1. Dashboard → New → Web Service
2. Select your `yt-agents` repository
3. Configure:
   - **Name:** `yt-agents`
   - **Runtime:** Python 3
   - **Branch:** main
   - **Build Command:** `pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 app:app`
   - **Plan:** Free

4. Click "Create Web Service"
5. Wait 2-5 minutes for deployment
6. Your app will be live at: `https://yt-agents-xxxxx.onrender.com`

#### Step 4: Test Your Deployment
- Open the Render URL
- You should see the login page
- Login with: `admin` / `password123`

---

### Option 2: Deploy with Docker (Local or Cloud)

#### Build Docker Image
```bash
cd /workspaces/yt-agents
docker build -t yt-agents:latest .
```

#### Run Docker Container Locally
```bash
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e PORT=5000 \
  yt-agents:latest
```

#### Deploy to Docker Registry
```bash
# Login to Docker Hub
docker login

# Tag image
docker tag yt-agents:latest YOUR_DOCKER_USER/yt-agents:latest

# Push to Docker Hub
docker push YOUR_DOCKER_USER/yt-agents:latest
```

#### Deploy to Docker Cloud Services
- **AWS ECS** - Elastic Container Service
- **Google Cloud Run** - Serverless containers
- **Azure Container Instances** - Azure's container service
- **DigitalOcean App Platform** - Simple deployment

---

### Option 3: Deploy to Railway.app (Easy Alternative)

1. Go to [railway.app](https://railway.app)
2. Click "Start New Project"
3. Select "Deploy from GitHub"
4. Choose your repository
5. Railway will auto-detect and deploy it
6. Get your public URL from the dashboard

---

### Option 4: Deploy to Heroku (Legacy but Popular)

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login

# Create app
heroku create yt-agents

# Deploy
git push heroku main

# View logs
heroku logs --tail
```

---

## Environment Variables Setup

### For Production Deployment

Set these in your cloud platform's environment variables section:

```env
# Required
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=your-very-secure-random-key-here

# Optional (for enhanced features)
YOUTUBE_API_KEY=your_youtube_api_key
YOUTUBE_CHANNEL_ID=your_channel_id
TWITTER_BEARER_TOKEN=your_twitter_token
REPLICATE_API_TOKEN=your_replicate_token
PEXELS_API_KEY=your_pexels_api_key
PIXABAY_API_KEY=your_pixabay_api_key
```

### Generate Secure Secret Key
```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## Testing Your Deployed Application

### Test 1: Access Landing Page
```bash
curl https://your-deployed-app.com/login
```

### Test 2: Test Login
```bash
curl -X POST https://your-deployed-app.com/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'
```

### Test 3: Create Workflow
```bash
# First login, get session cookie
# Then create workflow
curl -X POST https://your-deployed-app.com/start-workflow \
  -H "Content-Type: application/json" \
  -d '{"topic": "The Future of AI"}'
```

---

## Production Checklist

- [ ] Change SECRET_KEY to a secure value
- [ ] Set FLASK_ENV to `production`
- [ ] Add SSL certificate (most platforms do this automatically)
- [ ] Configure database if you want persistent user storage
- [ ] Set up error logging/monitoring
- [ ] Add rate limiting
- [ ] Create backup strategy
- [ ] Document API keys required
- [ ] Test all authentication flows
- [ ] Monitor application performance

---

## Current File Structure for Deployment

```
yt-agents/
├── Procfile                 # For Heroku/Render
├── Dockerfile               # For Docker deployment
├── docker-compose.yml       # For local Docker
├── render.yaml              # For Render.com
├── requirements.txt         # Python dependencies (with gunicorn)
├── .env                     # Environment variables (don't commit secrets!)
├── app.py                   # Main Flask application
├── config.py                # Configuration management
├── agents/                  # AI agents
├── templates/               # HTML templates
│   ├── login.html
│   ├── signup.html
│   ├── index.html
│   └── workflow.html
└── utils/                   # Utility modules
```

---

## Troubleshooting Deployment

### Issue: "Port binding failed"
- The deployment platform will automatically assign a PORT variable
- App is configured to use `$PORT` environment variable ✓

### Issue: "Module not found"
- All dependencies are in `requirements.txt` ✓
- Added `gunicorn` to handle WSGI ✓

### Issue: "Connection timeout"
- Set gunicorn timeout to 120 seconds (for long video operations)
- Reduced workers to 1 (for free tier)

### Issue: "Static files not loading"
- Flask automatically serves static files from `/templates`
- CSS/JS are embedded in HTML files ✓

### Issue: "Login not working"
- Users are stored in memory (USERS dict in app.py)
- In production, consider adding database persistence

---

## Getting Your Deployed Link

### After deploying to Render.com:
```
https://yt-agents-[random-id].onrender.com
```

### After deploying to Railway:
```
https://yt-agents-production.up.railway.app
```

### After deploying to Heroku:
```
https://yt-agents.herokuapp.com
```

---

## Monitoring & Logs

### Render.com
- Dashboard → Logs → View logs in real-time

### Railway
- Project → Deployments → View logs

### Docker
```bash
docker logs -f container_id
```

### Local Testing
```bash
cd /workspaces/yt-agents
FLASK_ENV=production gunicorn --bind 0.0.0.0:5000 --workers 1 app:app
```

---

## Next Steps

1. **Choose your deployment platform** (Render recommended for free tier)
2. **Generate secure SECRET_KEY**
3. **Push code to GitHub** (if not already pushed)
4. **Connect to deployment platform**
5. **Set environment variables**
6. **Deploy and test**
7. **Share your live link!**

---

## Support Resources

- **Render Docs:** https://render.com/docs
- **Railway Docs:** https://docs.railway.app
- **Docker Docs:** https://docs.docker.com
- **Flask Deployment:** https://flask.palletsprojects.com/deployment
- **Gunicorn Docs:** https://gunicorn.org

---

**Deployment Date:** February 10, 2026  
**Status:** Ready for Production ✅
