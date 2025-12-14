import pygame
import numpy as np
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

def animated_composite(frame_idx: float, images: list[np.ndarray], num_images: int) -> np.ndarray:
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
    engine = create_engine("sqlite:///musicVis_featrures.sqlite")
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

if __name__ == "__main__":
    musicVis("s001")
