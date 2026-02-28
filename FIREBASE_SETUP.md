# Firebase Setup Guide

Firebase provides **free storage and database** (with fair-use limits) and is recommended for this project.

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Click "Create a project" or select an existing project
3. Enable Firestore Database and Cloud Storage

## Step 2: Create a Service Account Key

Firebase uses service accounts for server-side authentication.

1. In Firebase Console, go to **Settings** → **Service Accounts**
2. Click "Generate New Private Key" (or "Create Service Account")
3. Download the JSON file (e.g., `serviceAccountKey.json`)
4. Save it securely (e.g., `/path/to/serviceAccountKey.json`)

## Step 3: Set Environment Variables

Add these to your `.env` file or deployment environment:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/serviceAccountKey.json"
export FIREBASE_STORAGE_BUCKET="your-project.appspot.com"
```

The bucket name is in Firebase Console under **Storage** tab, or in your service account JSON as `project_id`.

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

The following libraries will be installed:
- `google-cloud-storage` — Firebase Cloud Storage
- `google-cloud-firestore` — Firebase Firestore Database

## Step 5: Validate Setup

Run the validation script to check your Firebase connection:

```bash
python3 scripts/validate_firebase.py
```

If successful, you'll see:
```
✅ Firebase initialized
✅ Firestore ready
✅ Storage bucket ready
```

## Step 6: Migrate Videos to Firebase

Once validated, migrate existing videos:

```bash
# Dry-run (preview)
python3 scripts/migrate_videos_to_storage.py --dry-run

# Run migration
python3 scripts/migrate_videos_to_storage.py

# Optional: Delete local files after upload
python3 scripts/migrate_videos_to_storage.py --delete-local
```

## Firestore Schema

The `videos` collection stores metadata with these fields:

  - `id` — Timestamp-based unique identifier (20260217_161212)
  - `filename` — MP4 filename
  - `filepath` — Storage path (same as filename)
  - `topic` — Video topic/title
  - `duration` — Duration in seconds
  - `created_at` — ISO timestamp
  - `status` — "completed"
  - `file_size` — Bytes
  - `playable` — Boolean
  - `url` — API endpoint or signed URL
  - `youtube_id` — YouTube video ID (optional, added during upload)

## Free-Tier Limits

Firebase free tier includes:

- **Storage**: 5 GB total
- **Firestore**: 1 GB storage, 50k reads/day, 20k writes/day
- Suitable for small to medium projects

See [Firebase Pricing](https://firebase.google.com/pricing) for details.

## Troubleshooting

**Auth error (`PERMISSION_DENIED`)**:
- Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Verify service account has Firestore and Storage permissions

**Storage bucket not found**:
- Confirm `FIREBASE_STORAGE_BUCKET` matches your project
- Enable Cloud Storage in Firebase Console

**Firestore not available**:
- Make sure Firestore is enabled in Firebase Console
- Check `google-cloud-firestore` is installed

