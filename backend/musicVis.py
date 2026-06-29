from typing import List
import math
import subprocess
from pathlib import Path

import pygame
import numpy as np
import cv2
from fastapi import HTTPException
from sqlalchemy import create_engine
from database import get_song_features, get_song_file_location
from music_feature_extraction import MusicFeatures
from algorithmic_art_characteristics import *

def numpy_to_surface(img: np.ndarray) -> pygame.Surface:
    img = np.clip(img * 255, 0, 255).astype(np.uint8)
    img = np.transpose(img, (1, 0, 2))
    return pygame.surfarray.make_surface(img)

def map_features(features: MusicFeatures, screen_size:tuple=(512, 512), flatness_threshold: float=4):
    map_source = {0: 1, 1: 3, 2: 5}
    mean_velocity = np.mean(features.velocity)
    spectral_centroid_deviation = np.std(features.centroid)/np.mean(features.centroid)
    flatness_deviation = np.std(features.flatness)/np.mean(features.flatness)

    combined_texture = None
    
    # harsh (noisy sounds)
    if flatness_deviation > flatness_threshold:
        img = scratchy_texture(w=screen_size[0], h=screen_size[1], n_lines=round(features.tempo), 
                                separation=spectral_centroid_deviation, line_length=(50/len(features.notes), 500/len(features.notes)))
        combined_texture = img
    # reverb
    if features.quality[0][3] == 1:
        img = wavy_texture(w=screen_size[1], h=screen_size[0],
                           freq=min(np.std(features.velocity)/mean_velocity, 1),
                           layers=map_source[features.instrument_sources])
        combined_texture = img if combined_texture is None else np.clip(combined_texture + img, 0, 1)
    # blobs/splatters
    if combined_texture is None or features.instrument_sources != 0:
        img = blob_texture(w=screen_size[0], h=screen_size[1],
                           n_main=len(features.notes), blobiness=mean_velocity)
        combined_texture = img if combined_texture is None else np.clip(combined_texture + img, 0, 1)
    color = None
    if combined_texture is not None:
        color = get_color(features=features)
    return combined_texture, color, features.tempo

def animated_composite(frame_idx: float, images: List[np.ndarray], num_images: int) -> np.ndarray:
    weights = [
        (np.sin(frame_idx * 1.5 + (i * 2 * np.pi / num_images))) + 1
        for i in range(num_images)
    ]
    weights = np.array(weights) / 2
    stacked = np.stack(images, axis=0)
    weights_reshaped = weights[:, None, None]
    blended = np.sum(stacked * weights_reshaped, axis=0)
    
    return np.clip(blended, 0, 1)

def build_segments(features_timestamped, timeline, screen_size):
    segments = []

    for i, feature_group in enumerate(features_timestamped):
        images = []
        colors = []
        tempos = []

        for feat in feature_group:
            img, color, tempo = map_features(features=feat, screen_size=screen_size)
            if img is not None:
                images.append(img)
                colors.append(color)
                tempos.append(tempo)

        segments.append({
            "start": int(timeline[i] * 1000),
            "end": int(timeline[i + 1] * 1000) if i + 1 < len(timeline) else None,
            "images": images,
            "colors": colors,
            "tempo": float(np.mean(tempos))
        })

    return segments

def musicVis(song_title: str):
    engine = create_engine("sqlite:///musicVis_features.sqlite")
    features_timestamped, timeline = get_song_features(song_title=song_title, engine=engine)

    screen_size = (1024, 768)

    segments = build_segments(features_timestamped, timeline, screen_size)
    song_file = get_song_file_location(song_title=song_title, engine=engine)

    pygame.init()
    pygame.mixer.init(buffer=512)

    screen = pygame.display.set_mode((screen_size[0], screen_size[1]))
    pygame.display.set_caption("Music Visualization")

    clock = pygame.time.Clock()

    pygame.mixer.music.load(song_file)
    pygame.mixer.music.play()

    running = True

    while running and pygame.mixer.music.get_busy():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        t = pygame.mixer.music.get_pos()
        if t < 0:
            continue
        segment = next(
            (s for s in segments if s["start"] <= t and
             (s["end"] is None or t < s["end"])),
            None
        )

        if segment:
            local_seconds = (t - segment["start"]) / 1000.0
            frame_idx = local_seconds * segment["tempo"] / 30.0

            if len(segment["images"]) == 1:
                composite = segment["images"][0]
            else:
                composite = animated_composite(frame_idx, segment["images"], len(segment["images"]))

            colored = color_art_pixel(composite, segment["colors"])
            surface = numpy_to_surface(colored)

            screen.blit(surface, (0, 0))
            pygame.display.flip()

        clock.tick(60)

    pygame.quit()

# visualization function for frontend (equivalent to musicVis)
def generate_visualization(segments, time_ms, current_index):
    while current_index < len(segments) - 1:
        seg = segments[current_index + 1]
        if seg["start"] <= time_ms:
            current_index += 1
        else:
            break

    segment = segments[current_index]

    if segment["end"] is not None and time_ms >= segment["end"]:
        blank = np.zeros((768, 1024, 3), dtype=np.uint8)
        _, buffer = cv2.imencode('.webp', blank)
        return buffer.tobytes(), current_index

    local_seconds = (time_ms - segment["start"]) / 1000.0 
    frame_idx = local_seconds * segment["tempo"] / 30.0

    if len(segment["images"]) == 1:
        composite = segment["images"][0]
    else:
        composite = animated_composite(frame_idx, segment["images"], len(segment["images"]))

    colored = color_art_pixel(composite, segment["colors"])
    
    success, buffer = cv2.imencode('.webp', colored)
    if not success:
        raise Exception("Could not encode image to WebP")

    return buffer.tobytes(), current_index

def _get_audio_duration(audio_path: Path) -> float:
    if not audio_path.exists():
        return 0.0

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return 0.0

    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def _build_muxed_video(song_title: str, VIDEO_OUTPUT_DIR: Path) -> Path:
    output_path = VIDEO_OUTPUT_DIR / f"{song_title}.mp4"
    if output_path.exists():
        return output_path

    audio_path = get_song_file_location(song_title=song_title, engine=create_engine("sqlite:///musicVis_features.sqlite"))
    if not audio_path:
        raise HTTPException(status_code=404, detail="Song not found")

    audio_file = Path(audio_path)
    if not audio_file.exists() or not audio_file.is_file():
        raise HTTPException(status_code=404, detail="Audio file not found")

    engine = create_engine("sqlite:///musicVis_features.sqlite")
    features_timestamped, timeline = get_song_features(song_title=song_title, engine=engine)
    cached_segments = build_segments(
        features_timestamped=features_timestamped,
        timeline=timeline,
        screen_size=(1028, 768),
    )

    segments = cached_segments

    fps = 30
    duration_seconds = _get_audio_duration(audio_file)
    frame_count = max(1, int(math.ceil(duration_seconds * fps))) if duration_seconds > 0 else 90

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "image2pipe",
        "-framerate",
        str(fps),
        "-vcodec",
        "png",
        "-i",
        "-",
        "-i",
        str(audio_file),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "ultrafast",
        "-c:a",
        "aac",
        "-shortest",
        str(output_path),
    ]

    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    current_index = 0
    for index in range(frame_count):
        time_ms = int(index * 1000 / fps)
        frame_bytes, current_index = generate_visualization(segments, time_ms, current_index)
        if not frame_bytes:
            continue

        frame_array = cv2.imdecode(np.frombuffer(frame_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        if frame_array is None:
            continue

        success, png_frame = cv2.imencode(".png", frame_array)
        if not success:
            continue

        process.stdin.write(png_frame.tobytes())
        process.stdin.flush()

    if process.stdin is not None:
        process.stdin.close()

    stderr_output = process.stderr.read().decode("utf-8", errors="ignore") if process.stderr else ""
    return_code = process.wait()

    if return_code != 0:
        raise RuntimeError(f"ffmpeg failed: {stderr_output}")

    return output_path

# if __name__ == "__main__":
#     musicVis("s001")
