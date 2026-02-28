# Video Storage Configuration

This project supports multiple storage backends, with **Firebase** as the recommended free option.

## Storage Options (in order of preference)

| Backend | Cost | Setup | Suitable For |
|---------|------|-------|--------------|
| **Firebase** (Recommended) | Free tier available | 10 min | Small-medium projects, rapid deployment |
| S3 + Postgres | Pay-per-use | Moderate | High-scale, enterprise |
| Supabase | Managed, free tier | 10 min | Postgres users, API-first |
| SQLite | Free, local | Instant | Development, small projects |
| Local JSON | Free, local | Instant | Testing, prototyping |

## Quick Start

### 1. Firebase (Recommended)

```bash
# Set credentials (get from Firebase Console → Settings → Service Accounts)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/serviceAccountKey.json"
export FIREBASE_STORAGE_BUCKET="my-project.appspot.com"

# Validate
python3 scripts/validate_firebase.py

# Migrate
python3 scripts/migrate_videos_to_storage.py --dry-run
python3 scripts/migrate_videos_to_storage.py
```

See [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for detailed steps.

### 2. S3 + Postgres (Alternative)

```bash
# Set AWS and Postgres credentials
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_S3_BUCKET="..."
export DATABASE_URL="postgres://..."

# Migrate
python3 scripts/migrate_videos_to_storage.py
```

See [MIGRATION.md](MIGRATION.md) for details.

### 3. Supabase (Alternative)

```bash
# Set Supabase credentials
export SUPABASE_URL="https://xyz.supabase.co"
export SUPABASE_KEY="service_role_key"

# Migrate
python3 scripts/migrate_videos_to_storage.py
```

See [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for SQL schema and steps.

### 4. Local SQLite (Default)

No setup required. Metadata stored in `./output/videos/videos.db`, files in `./output/videos/`.

## Where Generated Files Are Stored

- **Firebase**: Objects in Cloud Storage, metadata in Firestore `videos` collection
- **S3 + Postgres**: Objects in S3 bucket, metadata in Postgres `videos` table
- **Supabase**: Objects in Storage bucket, metadata in Postgres `videos` table
- **SQLite**: Files in `./output/videos/`, metadata in `./output/videos/videos.db`
- **Local JSON**: Files in `./output/videos/`, metadata in `./output/videos/video_metadata.json`

## Environment Variables (.env)

Required for each backend:

**Firebase**:
```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json
FIREBASE_STORAGE_BUCKET=my-project.appspot.com
```

**S3 + Postgres**:
```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=...
AWS_REGION=us-east-1
DATABASE_URL=postgres://user:pass@host:5432/db
```

**Supabase**:
```
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_KEY=service_role_key
```

**YouTube Upload (Optional)**:
```
YOUTUBE_API_KEY=...
YOUTUBE_CHANNEL_ID=...
FLASK_SECRET_KEY=...
```

## How Video Upload Works

1. **Video created** by agents → stored locally in `./output/videos/`
2. **Video uploaded to YouTube** (optional) via `UploadAgent` → returns YouTube video ID
3. **Metadata stored** in configured backend (Firebase/S3/Supabase/SQLite) with:
   - `id` — unique timestamp
   - `filename`, `filepath` — storage location
   - `url` — API endpoint or signed/public URL
   - `youtube_id` — YouTube ID (if uploaded)
   - Other fields: `topic`, `duration`, `created_at`, `status`, etc.
4. **API endpoints** return URLs for accessing:
   - `GET /api/videos/history` — list all videos
   - `GET /api/videos/<id>` — serve video file

## Validate Setup

Run before migration:

```bash
python3 scripts/validate_firebase.py  # for Firebase
# Or simply try the migration in dry-run mode
python3 scripts/migrate_videos_to_storage.py --dry-run
```

## Next Steps

1. Choose a backend (Firebase recommended)
2. Follow the setup guide for that backend
3. Set environment variables
4. Run `python3 scripts/validate_firebase.py` (or validation for your backend)
5. Run migration: `python3 scripts/migrate_videos_to_storage.py`

