"""
Music Visualization: Visualizes music characteristics using fine-grained texture generation based on cross-modal correspondences.

Functions:
    - map_features(): maps visual characteristics based on extracted music features and displays them.
    - musicVis(): main function orchestrating the process of music visualization.
    - display_animation(): displays the generated textures as an animation synchronized to the music tempo.
"""

import cv2
from multiprocessing import Process, Queue
import multiprocessing
from sqlalchemy import create_engine
from database import get_song_features
from music_feature_extraction import *
from algorithmic_art_characteristics import *

def calculate_duration(timeline: list) -> list:
    durations = []
    for i in range(1, len(timeline)):
        durations.append(timeline[i] - timeline[i-1])
    durations.append(4)
    return durations

def map_features(features: MusicFeatures, velocity_threshold=5, centroid_threshold=3000, flatness_threshold=0.55):
    map_source = {0: 1, 1: 3, 2: 5}
    mean_velocity = np.mean(features.velocity)
    mean_spectral_centroid = np.mean(features.centroid)
    mean_flatness = np.mean(features.flatness)

    combined_texture = None
    
    # high velocity mean OR harsh (noisy sounds)
    if (mean_velocity > velocity_threshold) or (mean_flatness > flatness_threshold):
        img = scratchy_texture(n_lines=round(features.tempo), 
                                separation=np.std(features.centroid)/mean_spectral_centroid, 
                                line_length=(100/len(features.notes), 1000/len(features.notes)))
        combined_texture = img
    # low velocity mean OR reverb
    if (mean_velocity <= velocity_threshold) or features.quality[0][3] == 1:
        img = wavy_texture(freq=min(np.std(features.velocity)/mean_velocity, 1),
                            layers=map_source[features.instrument_sources])
        combined_texture = img if combined_texture is None else np.clip(combined_texture + img, 0, 1)
    # high spectral centroid mean OR percussive
    if (mean_spectral_centroid > centroid_threshold) or features.quality[0][2] == 1:
        img = blob_texture(n_main=len(features.notes), blobiness=2)
        combined_texture = img if combined_texture is None else np.clip(combined_texture + img, 0, 1)
    # low spectral centroid mean OR softer (tonal sounds)
    if (mean_spectral_centroid <= centroid_threshold) or (mean_flatness < flatness_threshold):
        img = blob_texture(n_main=len(features.notes), blobiness=7)
        combined_texture = img if combined_texture is None else np.clip(combined_texture + img, 0, 1)
    
    color = get_color(features=features)
    return combined_texture, color, features.tempo

def display_animation(images, colors, tempos, duration, previous_composite=None, previous_colors=None, fps=60):
    num_images = len(images)
    tempo = np.mean(tempos)
    frame_step = max(1, int(tempo / 60))
    frames = int(duration * fps)

    if len(images) == 1:
        single_frame = color_art_pixel(images[0], colors=colors)

        for _ in range(frames):
            cv2.imshow("Music Visualization", single_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return None, None
        return images[0], colors


    def get_animated_image(frame_idx):
        weights = [
            (np.sin(frame_idx * 0.1 + (i * 2 * np.pi / num_images))) + 1
            for i in range(num_images)
        ]
        weights = np.array(weights) / 2
        stacked = np.stack(images, axis=0)
        weights_reshaped = weights[:, None, None]
        blended = np.sum(stacked * weights_reshaped, axis=0)
        
        return np.clip(blended, 0, 1)

    first_composite = get_animated_image(0)
    
    pre_rendered_main_frames = []
    final_composite = first_composite
    for i in range(frames):
        composite = get_animated_image(i * frame_step)
        if i == frames - 1:
            final_composite = composite
        colored = color_art_pixel(composite, colors=colors)
        pre_rendered_main_frames.append(colored)
    
    if previous_composite is not None and previous_colors is not None:
        previous_colors = np.array(previous_colors).astype(np.uint8)
        current_colors = np.array(colors, dtype=np.uint8)

        transition_frames = int(0.25*fps)
        for f in range(transition_frames):
            t = f / transition_frames
            t = t * t * (3 - 2 * t)

            blended = (1 - t) * previous_composite + t * first_composite
            blended = np.clip(blended, 0, 1)
            
            min_size = min(len(previous_colors), len(current_colors))
            
            blended_colors = previous_colors.copy()
            blended_colors[:min_size] = (
                previous_colors[:min_size] * (1 - t)
                + current_colors[:min_size] * t
            )
            if len(colors) > min_size:
                fade_new = current_colors[min_size:] * t
                blended_colors = np.concatenate([blended_colors[:min_size], fade_new], axis=0)
            colored = color_art_pixel(blended, colors=blended_colors.astype(np.uint8))
            
            cv2.imshow("Music Visualization", colored)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return None, None
            
    for display_frame in pre_rendered_main_frames:
        cv2.imshow("Music Visualization", display_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return None, None
    return final_composite, colors

def construct_image(features_timestamped: list[list[MusicFeatures]], preload_queue: Queue):
    for feature in features_timestamped:
        images = []
        colors = []
        tempos = []

        for feat in feature:
            image, color, tempo = map_features(feat)
            images.append(image)
            colors.append(color)
            tempos.append(tempo)

        preload_queue.put((images, colors, tempos))

def musicVis(music_title: str):
    engine = create_engine("sqlite:///musicVis_featrures.sqlite")
    features_timestamped, timeline = get_song_features(song_title=music_title, engine=engine)
    durations = calculate_duration(timeline)

    # multithread requests so that next image is computed before showing the next screen
    preload_queue = Queue(maxsize=3)
    worker = Process(
        target=construct_image,
        args=(features_timestamped, preload_queue)
    )
    worker.daemon = True
    worker.start()

    # play final animated colored images according to the proper duration segment
    image_transition = None
    previous_colors = None
    for duration in durations:
        images, colors, tempos = preload_queue.get()
        image_transition, previous_colors = display_animation(
            images=images, 
            colors=colors, 
            tempos=tempos, 
            duration=duration, 
            previous_composite=image_transition, 
            previous_colors=previous_colors
        )
    cv2.destroyAllWindows()

if __name__ == '__main__':
    multiprocessing.set_start_method("spawn", force=True)
    musicVis("s016")
