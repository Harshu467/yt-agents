#!/usr/bin/env python3
"""Smoke test for SQLite storage: saves a placeholder video and lists DB entries."""
import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from utils.video_storage import get_video_storage


def main():
    storage = get_video_storage()
    print("Using storage backend:", storage.__class__.__name__)

    # Create a small placeholder video
    data = storage.create_blank_video(topic="smoke-test", duration=2)
    rec = storage.save_video(data, topic="smoke-test", duration=2)
    print("Saved record:", rec)

    all_v = storage.get_all_videos()
    print(f"Total videos in storage: {len(all_v)}")
    for v in all_v[:5]:
        print(v)


if __name__ == '__main__':
    main()
