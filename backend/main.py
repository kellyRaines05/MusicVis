import uuid
import threading

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
import cv2

from musicVis import build_segments, generate_visualization
from database import add_stems_to_db, get_all_songs, get_song_features
from download_clips import download_video_clip
from stem_music import stem_song

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
engine = create_engine("sqlite:///musicVis_featrures.sqlite")
cached_segments = {}
jobs = {}

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/songs")
def get_songs():
    return get_all_songs(engine=engine)

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

@app.websocket("/ws/{song}")
async def websocket_endpoint(websocket: WebSocket, song: str):
    await websocket.accept()

    if song not in cached_segments:
        features_timestamped, timeline = get_song_features(song_title=song, engine=engine)
        segments = build_segments(features_timestamped=features_timestamped, timeline=timeline, screen_size=(1024, 768))

        cached_segments[song] = segments

    segments = cached_segments[song]

    current_index = 0

    while True:
        data = await websocket.receive_json()
        time_ms = data["time"]

        frame, current_index = generate_visualization(segments, time_ms, current_index)

        if frame is None:
            continue

        success, buffer = cv2.imencode(".webp", frame)

        if not success:
            continue

        await websocket.send_bytes(buffer.tobytes())