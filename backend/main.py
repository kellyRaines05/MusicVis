import uuid
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import create_engine

from musicVis import _build_muxed_video
from database import add_stems_to_db, get_all_songs, get_song_file_location
from download_clips import download_video_clip
from stem_music import stem_song

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9000",
        "http://127.0.0.1:9000",
        "http://localhost:9001",
        "http://127.0.0.1:9001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine("sqlite:///musicVis_features.sqlite")
cached_segments = {}
jobs = {}
VIDEO_OUTPUT_DIR = Path(__file__).resolve().parent / "generated_videos"
VIDEO_OUTPUT_DIR.mkdir(exist_ok=True)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/songs")
def get_songs():
    songs =  get_all_songs(engine=engine)
    for i, song in enumerate(songs):
        song_title = song.get('song_title') if isinstance(song, dict) else song
        print(f"[{i}/{len(songs)}] Generating video for '{song_title}'...")
        
        try:
            video_path = _build_muxed_video(song_title=song_title, VIDEO_OUTPUT_DIR=VIDEO_OUTPUT_DIR)
            print(f"  ✓ Success: {video_path}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

    return songs

@app.post("/songs/add_song")
def add_song(song_link: str, song_title: str):
    job_id = str(uuid.uuid4())
    jobs[job_id] = "Starting"

    def worker():
        jobs[job_id] = "Downloading"
        file_path = download_video_clip(
            video_url=song_link,
            title=song_title,
        )

        jobs[job_id] = "Separating stems"
        stem_path = stem_song(file=file_path)

        jobs[job_id] = "Saving to database"
        add_stems_to_db(
            engine=engine,
            song_title=song_title,
            song_file_path=file_path,
            stem_file_path=stem_path,
        )

        jobs[job_id] = "Done"

    threading.Thread(target=worker).start()

    return {"job_id": job_id}

@app.get("/songs/status/{job_id}")
def get_status(job_id: str):
    return {"status": jobs.get(job_id, "Unknown job")}

@app.get("/audio/{song_title}")
def serve_audio(song_title: str):
    file_path = get_song_file_location(song_title=song_title, engine=engine)

    if not file_path:
        raise HTTPException(status_code=404, detail="Song not found")

    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")

    media_type = "audio/mpeg"
    if path.suffix.lower() == ".wav":
        media_type = "audio/wav"
    elif path.suffix.lower() == ".m4a":
        media_type = "audio/mp4"

    return FileResponse(path, media_type=media_type)

@app.get("/video/{song_title}")
def serve_video(song_title: str):
    output_path = _build_muxed_video(song_title=song_title, VIDEO_OUTPUT_DIR=VIDEO_OUTPUT_DIR)
    return FileResponse(output_path, media_type="video/mp4")
