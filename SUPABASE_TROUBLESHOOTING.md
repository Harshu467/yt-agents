# Supabase Upload Error - Troubleshooting Guide

## Error: "Video generation failed: Failed to upload video to Supabase storage"

This guide helps you diagnose and fix Supabase storage upload failures.

---

## Quick Diagnosis

Run the validation script to identify the issue:

```bash
python3 scripts/validate_supabase.py
python3 scripts/validate_supabase.py --setup   # For detailed setup instructions
```

---

## Common Issues & Fixes

### 1. ❌ Missing Credentials

**Symptoms:**
- `SUPABASE_URL: NOT SET`
- `SUPABASE_KEY: NOT SET`

**Fix:**

1. **Get credentials from Supabase:**
   - Go to https://app.supabase.com
   - Select your project
   - Settings → API → Copy credentials

2. **Set environment variables:**

   **Option A: Export in terminal**
   ```bash
   export SUPABASE_URL='https://your-project.supabase.co'
   export SUPABASE_KEY='your_service_role_key'
   ```

   **Option B: Add to .env file**
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_service_role_key
   ```

3. **Verify:**
   ```bash
   python3 scripts/validate_supabase.py
   ```

---

### 2. 🪣 Storage Bucket Doesn't Exist

**Symptoms:**
- `Storage API: ✗ Failed (404)`
- Error message mentions "bucket not found"

**Fix:**

1. **Create storage bucket in Supabase:**
   - Go to https://app.supabase.com
   - Project → Storage → Buckets
   - Click "New bucket"
   - Name: `videos` (must match config)
   - Make it Public OR set RLS policies

2. **Verify the bucket exists:**
   ```bash
   python3 scripts/validate_supabase.py
   ```

---

### 3. 🔐 Authentication Failed

**Symptoms:**
- `Storage API: ✗ Failed (401)`
- Error message: "Authentication failed"

**Fixes:**

**A. Wrong Key Type**
- Make sure you're using **service_role key**, not anon key
- Go to Settings → API → Look for "service_role" (not "anon")

**B. Key Expired or Revoked**
- Generate a new key in Settings → API
- Update SUPABASE_KEY environment variable

**C. Key Has Insufficient Permissions**
- Go to Settings → API → Check permissions
- Make sure it has storage write permissions

---

### 4. 🚫 Permission Denied

**Symptoms:**
- `Storage API: ✗ Failed (403)`
- Error message: "Permission denied"

**Fixes:**

**A. Make Bucket Public**
- Storage → Buckets → Select "videos"
- Click "Policies"
- Remove RLS or add public read/write policy

**B. Set RLS Policy**
If you want authenticated uploads only:
```sql
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public uploads to videos"
ON storage.objects
FOR INSERT
WITH CHECK (bucket_id = 'videos');
```

**C. Run Setup Script**
```bash
python3 scripts/setup_supabase_rls.py  # If available
```

---

### 5. 📊 Metadata Table Missing

**Symptoms:**
- `Metadata API: ✗ Failed (400+)`
- Error: `relation "videos" does not exist`
- Error: `relation "supabase_migrations.schema_migrations" does not exist`
- Storage works but metadata insert fails

**Fix:**

Create the videos table in Supabase SQL Editor:

**Option A: Use Setup Script (Automatic)**
```bash
python3 scripts/setup_supabase_table.py
```
This will guide you through the process and show you the SQL to run.

**Option B: Manual SQL Setup**
1. Go to https://app.supabase.com → SQL Editor
2. Create new query
3. Paste this SQL:

```sql
CREATE TABLE IF NOT EXISTS public.videos (
  id text PRIMARY KEY,
  filename text,
  filepath text,
  topic text,
  duration real,
  file_size integer,
  created_at timestamptz DEFAULT now(),
  status text DEFAULT 'pending',
  playable boolean DEFAULT FALSE,
  url text,
  youtube_id text
);

CREATE INDEX IF NOT EXISTS idx_videos_created_at ON public.videos (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_videos_topic ON public.videos (topic);
CREATE INDEX IF NOT EXISTS idx_videos_youtube_id ON public.videos (youtube_id);
```

4. Click "Run"
5. Verify with: `python3 scripts/setup_supabase_table.py --status`

---

### 6. 🌐 Network/Connection Issues

**Symptoms:**
- Timeout errors
- Connection refused
- DNS resolution failure

**Fixes:**

1. **Check internet connection**
   ```bash
   ping 8.8.8.8
   curl https://app.supabase.com
   ```

2. **Check Supabase URL format**
   - Should be: `https://your-project.supabase.co`
   - Not: `https://your-project.supabase.io` (wrong TLD)

3. **Check firewall/proxy**
   - If behind corporate firewall, whitelist supabase.co domain

4. **Verify Supabase project is running**
   - Go to https://app.supabase.com
   - Check project status

---

### 7. 🎯 Invalid Bucket Name

**Symptoms:**
- Upload works but metadata fails
- Bucket path issues

**Fix:**

Bucket name must be:
- Lowercase letters, numbers, hyphens, underscores
- No spaces or special characters
- Standard config uses: `videos`

If using custom bucket name, set:
```bash
export SUPABASE_STORAGE_BUCKET='your-bucket-name'
```

### 8. 📁 Serving Remote URLs

**Symptoms:**
- Server logs show an error similar to:
  ```
  [Errno 2] No such file or directory: '/opt/render/project/src/https://...'
  ```
- Clicking the video link returns “This video isn’t available any more.”

This happens when the storage backend (e.g. Supabase) returns a **URL**
instead of a local filepath. The Flask `send_file` helper then tries to open
that string as a filesystem path.

**Fix:**
- The application now redirects to remote URLs automatically. Update to the
  latest code or modify your own `serve_video` route:
  ```python
  filepath = storage.get_video_file(video_id)
  if filepath and filepath.startswith(('http://', 'https://')):
      return redirect(filepath)
  ```
- Ensure the bucket is public or that signed URLs are valid. Expired signed
  links will show “video isn’t available”.

Retry your workflow after upgrading and confirm the link points to a working
Supabase object.

---

## Step-by-Step Setup

If you're starting fresh, follow this order:

### Step 1: Create Supabase Project
```bash
# Visit https://app.supabase.com
# Click "New Project"
# Fill in details and create
```

### Step 2: Extract Credentials
```
Settings → API → Copy these values:
  SUPABASE_URL = "Project URL"
  SUPABASE_KEY = "service_role secret"
```

### Step 3: Create Storage Bucket
```
Storage → Buckets → New bucket → "videos" → Public
```

### Step 4: Create Videos Table
```sql
-- Copy this into SQL Editor and run
CREATE TABLE public.videos (
  id TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  filepath TEXT NOT NULL,
  topic TEXT,
  duration FLOAT,
  file_size INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status TEXT DEFAULT 'pending',
  playable BOOLEAN DEFAULT FALSE,
  url TEXT
);
```

### Step 5: Set Environment Variables
```bash
# In your terminal or .env file
export SUPABASE_URL='https://your-project.supabase.co'
export SUPABASE_KEY='your_service_role_key'
```

### Step 6: Validate
```bash
python3 scripts/validate_supabase.py
```

You should see: ✅ Configuration Valid!

---

## Advanced Troubleshooting

### Check Request Details

The improved error messages now show:
- **HTTP Status Code** (401, 403, 404, etc.)
- **Response from API** (exact error message)
- **Request URL** (what was being uploaded to)
- **Helpful hints** based on status code

Example output:
```
⚠️  Supabase upload failed: 401
   URL: https://your-project.supabase.co/storage/v1/object/videos/...
   Error: Invalid authentication header
   ❌ Authentication failed - check SUPABASE_KEY is valid
```

### View Detailed Logs

When running the application:
```bash
# Logs will show detailed error messages
python3 app.py
# Or
python3 create_video_example.py
```

### Manual Upload Test

Test Supabase connection directly:
```bash
python3 << 'EOF'
from utils.supabase_storage import SupabaseStorage
import os

try:
    storage = SupabaseStorage()
    print("✓ Client initialized")
    
    # Validate config
    result = storage.validate_configuration()
    print(f"✓ Validation result: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
EOF
```

---

## Getting Help

If issues persist:

1. **Check Supabase Status**
   - https://status.supabase.com

2. **Review Supabase Docs**
   - https://supabase.com/docs

3. **Check Firebase Alternative**
   - If Supabase issues are blocking, switch to Firebase:
   - `export FIREBASE_STORAGE_BUCKET='your-bucket'`
   - See FIREBASE_SETUP.md

4. **Use Local Storage (Development)**
   - Works offline, no setup needed
   - Stores in `./output/videos/`

---

## Configuration Reference

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| SUPABASE_URL | Yes | https://abc123.supabase.co | From Settings → API |
| SUPABASE_KEY | Yes | eyJ0... | service_role key, keep secret |
| SUPABASE_BUCKET | No | videos | Defaults to "videos" |

---

## Next Steps

After fixing the error:

1. ✅ Verify with validation script
2. ✅ Try uploading a test video
3. ✅ Check dashboard to confirm video appears
4. ✅ Proceed with your workflow

Good luck! 🚀
