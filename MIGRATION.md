**Migrating existing local videos to remote storage**

This project supports three storage backends (in order of preference):

- S3 + Postgres (recommended for production)
- Supabase (managed Postgres + storage)
- Local filesystem (default)

When deployed, set the required environment variables to enable a remote backend:

- S3 + Postgres:
  - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET`, optionally `AWS_REGION`
  - `DATABASE_URL` (Postgres connection string)

- Supabase:
  - `SUPABASE_URL`, `SUPABASE_KEY`

Migration steps (recommended):

1. Install runtime dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment variables for S3 or Supabase.

3. Dry-run migration to see what would be uploaded:

```bash
python scripts/migrate_videos_to_storage.py --dry-run
```

4. Run migration (optionally delete local files after successful upload):

```bash
python scripts/migrate_videos_to_storage.py --delete-local
```

Notes:
- The script uses `get_video_storage()` so it automatically selects the configured backend.
- For S3, objects are uploaded and a presigned URL is stored in Postgres. For Supabase, objects are uploaded to the storage bucket and a public/signed URL is stored in the `videos` table.
- If you need help setting up the remote DB or bucket, tell me and I can provide exact SQL and IAM policies.
