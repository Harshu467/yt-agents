#!/usr/bin/env bash
set -euo pipefail

echo "Preparing deployment..."

missing=0
check_env() {
  if [ -z "${!1:-}" ]; then
    echo "  MISSING: $1"
    missing=$((missing+1))
  else
    echo "  OK: $1"
  fi
}

echo "Checking S3+Postgres vars (recommended):"
check_env AWS_ACCESS_KEY_ID
check_env AWS_SECRET_ACCESS_KEY
check_env AWS_S3_BUCKET
check_env DATABASE_URL

echo "\nChecking Supabase vars (optional):"
check_env SUPABASE_URL
check_env SUPABASE_KEY

echo "\nChecking Firebase vars (optional but recommended free option):"
check_env GOOGLE_APPLICATION_CREDENTIALS
check_env FIREBASE_STORAGE_BUCKET

if [ "$missing" -gt 0 ]; then
  echo "\nSome environment variables are missing. Please set them (see .env.example)."
  echo "You can still run the migration in dry-run mode to preview:"
  echo "  python3 scripts/migrate_videos_to_storage.py --dry-run"
  exit 1
fi

echo "All required env vars present. Running dry-run migration..."
python3 scripts/migrate_videos_to_storage.py --dry-run

echo "To run actual migration, execute:"
echo "  python3 scripts/migrate_videos_to_storage.py"
