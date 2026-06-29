from fastapi import FastAPI, WebSocket
from sqlalchemy import create_engine
import cv2

from musicVis import build_segments, generate_visualization
from database import get_all_songs, get_song_features

app = FastAPI()
engine = create_engine("sqlite:///musicVis_featrures.sqlite")
cached_segments = {}

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/songs")
def get_songs():
    return get_all_songs(engine=engine)

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

        frame, current_index = generate_visualization(segments,time_ms, current_index)

        if frame is None:
            continue

        success, buffer = cv2.imencode(".webp", frame)

        if not success:
            continue

        await websocket.send_bytes(buffer.tobytes())