#!/usr/bin/env python3
"""
Temporary script to generate videos for all songs in the database.
Run this script from the backend directory to generate all muxed videos.
"""

from pathlib import Path
from sqlalchemy import create_engine
from database import get_all_songs
from musicVis import _build_muxed_video

# Set up paths and database
VIDEO_OUTPUT_DIR = Path(__file__).resolve().parent / "generated_videos"
VIDEO_OUTPUT_DIR.mkdir(exist_ok=True)

engine = create_engine("sqlite:///musicVis_features.sqlite")

# Get all songs
songs = get_all_songs(engine=engine)
print(f"Found {len(songs)} songs to process")

# # Generate videos for each song
# for i, song in enumerate(songs):
#     song_title = song.get('song_title') if isinstance(song, dict) else song
#     print(f"[{i}/{len(songs)}] Generating video for '{song_title}'...")
    
#     try:
#         video_path = _build_muxed_video(song_title=song_title, VIDEO_OUTPUT_DIR=VIDEO_OUTPUT_DIR)
#         print(f"  ✓ Success: {video_path}")
#     except Exception as e:
#         print(f"  ✗ Error: {str(e)}")

# print("Done!")
