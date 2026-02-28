#!/usr/bin/env python3
"""
Migrate existing local videos and metadata into configured storage (S3+Postgres or Supabase).

Usage:
  python scripts/migrate_videos_to_storage.py --dry-run
  python scripts/migrate_videos_to_storage.py --delete-local

This script will use `get_video_storage()` from `utils.video_storage` which prefers
S3+Postgres when `AWS_S3_BUCKET`+`DATABASE_URL` are set, then Supabase when
`SUPABASE_URL`+`SUPABASE_KEY` are set. If none are set the script will exit.
"""
import argparse
import json
import os
import sys
from pathlib import Path

# Ensure repo root is on sys.path so imports like `config` resolve when running from scripts/
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from config import Config

from utils.video_storage import get_video_storage


def load_local_metadata() -> dict:
    meta_path = os.path.join(Config.VIDEOS_DIR, 'video_metadata.json')
    if not os.path.exists(meta_path):
        print(f"No metadata file found at {meta_path}")
        return {}
    try:
        with open(meta_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load metadata: {e}")
        return {}


def migrate(dry_run: bool = True, delete_local: bool = False):
    storage = get_video_storage()

    # If current storage is local filesystem, abort
    storage_class = storage.__class__.__name__
    print(f"Detected storage backend: {storage_class}")
    if storage_class == 'VideoStorage':
        print("No remote storage configured. Set AWS or SUPABASE env vars to migrate.")
        return

    metadata = load_local_metadata()
    if not metadata:
        print("No local metadata entries to migrate.")
        return

    total = len(metadata)
    print(f"Found {total} videos to consider for migration.")

    for vid, info in list(metadata.items()):
        filepath = info.get('filepath')
        if not filepath or not os.path.exists(filepath):
            print(f"Skipping {vid}: file not found ({filepath})")
            continue

        print(f"Processing {vid} -> {filepath}")
        if dry_run:
            print("  dry-run: would upload")
            continue

        try:
            with open(filepath, 'rb') as f:
                data = f.read()

            rec = storage.save_video(data, topic=info.get('topic', 'migrated'), duration=info.get('duration', 0))
            print(f"  uploaded -> {rec.get('id') or rec.get('filepath') or rec.get('url')}")

            if delete_local:
                try:
                    os.remove(filepath)
                    print(f"  deleted local file {filepath}")
                except Exception as e:
                    print(f"  failed to delete local file: {e}")

        except Exception as e:
            print(f"  ERROR uploading {vid}: {e}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true', help='Show what would be migrated')
    p.add_argument('--delete-local', action='store_true', help='Delete local files after successful upload')
    args = p.parse_args()

    migrate(dry_run=args.dry_run, delete_local=args.delete_local)


if __name__ == '__main__':
    main()
