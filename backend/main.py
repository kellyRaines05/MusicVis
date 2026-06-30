import uuid
import threading
from pathlib import Path

from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import create_engine

from musicVis import _build_muxed_video
from database import add_stems_to_db, get_all_songs, get_song_file_location
from download_clips import download_video_clip
from stem_music import stem_song

class AddSongRequest(BaseModel):
    song_link: str
    song_title: str

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

def _run_song_job(job_id: str, song_link: str, song_title: str):
    jobs[job_id].update({
        "status": "Downloading clip",
        "progress": 10,
    })

    try:
        file_path = download_video_clip(video_url=song_link, title=song_title)

        jobs[job_id].update({
            "status": "Stemming audio",
            "progress": 35,
            "message": "Separating the audio into stems",
        })
        stem_path = stem_song(file=file_path)

        jobs[job_id].update({
            "status": "Saving song data",
            "progress": 60,
            "message": "Persisting stems and feature data",
        })
        add_stems_to_db(
            engine=engine,
            song_title=song_title,
            song_file_path=file_path,
            stem_file_path=stem_path,
        )

        jobs[job_id].update({
            "status": "Done",
            "progress": 100,
            "message": "Song added successfully",
            "song_title": song_title,
        })
    except Exception as exc:
        jobs[job_id].update({
            "status": f"Error: {exc}",
            "progress": 0,
            "message": str(exc),
            "song_title": song_title,
        })


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/songs")
def get_songs():
    return get_all_songs(engine=engine)


@app.post("/songs/add_song", status_code=202)
def add_song(payload: AddSongRequest):
    song_link = payload.song_link.strip()
    song_title = payload.song_title.strip()

    if not song_link or not song_title:
        raise HTTPException(status_code=400, detail="Both song_link and song_title are required")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": "Queued",
        "progress": 0,
        "message": "Queued for processing",
        "song_title": song_title,
    }

    thread = threading.Thread(target=_run_song_job, args=(job_id, song_link, song_title), daemon=True)
    thread.start()

    return {
        "job_id": job_id,
        "status": jobs[job_id]["status"],
        "progress": jobs[job_id]["progress"],
    }


@app.get("/songs/status/{job_id}")
def get_song_job_status(job_id: str):
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


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
