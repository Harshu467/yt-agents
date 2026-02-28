#!/usr/bin/env python3
"""Migrate videos recorded in local SQLiteStorage into currently configured backend (e.g. Firebase)."""
import sys
import os
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from utils.sqlite_storage import SQLiteStorage
from utils.video_storage import get_video_storage


def migrate(delete_local: bool = False):
    local = SQLiteStorage()
    recs = local.get_all_videos()
    print(f"Found {len(recs)} local SQLite records to migrate")
    storage = get_video_storage()
    for r in recs:
        print(f"Processing {r['id']} -> {r['filepath']}")
        if not os.path.exists(r['filepath']):
            print("  file missing, skipping")
            continue
        with open(r['filepath'], 'rb') as f:
            data = f.read()
        newrec = storage.save_video(data, topic=r.get('topic',''), duration=r.get('duration',0))
        print(f"  uploaded -> {newrec.get('id')} url={newrec.get('url')}")
        if delete_local:
            try:
                os.remove(r['filepath'])
                print("  deleted local file")
            except Exception as e:
                print(f"  failed delete: {e}")


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--delete-local', action='store_true', help='remove local files after upload')
    args = p.parse_args()
    migrate(delete_local=args.delete_local)

if __name__ == '__main__':
    main()
