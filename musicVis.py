"""
Music Visualization: Visualizes music characteristics using fine-grained texture generation based on cross-modal correspondences.

Functions:
    - map_features(): maps visual characteristics based on extracted music features and displays them.
    - musicVis(): main function orchestrating the process of music visualization.
    - display_animation(): displays the generated textures as an animation synchronized to the music tempo.
"""

from algorithmic_art_characteristics import *
from music_feature_extraction import *
import cv2

def map_features(features: MusicFeatures, velocity_threshold=5, centroid_threshold=3000):
    map_source = {0: 1, 1: 3, 2: 5}
    mean_velocity = np.mean(features.velocity)
    mean_spectral_centroid = np.mean(features.centroid)

    combined_texture = None
    
    # high velocity mean OR high spectral centroid mean
    if mean_velocity > velocity_threshold or mean_spectral_centroid > centroid_threshold:
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
    # low spectral centroid mean
    if (mean_spectral_centroid <= centroid_threshold):
        img = blob_texture(n_main=len(features.notes), blobiness=7)
        combined_texture = img if combined_texture is None else np.clip(combined_texture + img, 0, 1)
    
    color = get_color(features=features)
    return combined_texture, color, features.tempo

def musicVis(input_music: str):
    pass
    # stemmed_file = stem_song(input_music)
    # is_silent = detect_silence(stemmed_file)
    # if is_silent:
    #     print("The input audio is silent. Exiting visualization.")
    #     return

def display_animation(images, colors, tempo=120):
    frames = 500
    num_images = len(images)

    if num_images == 1:
        colored_image = color_art_pixel(images[0], colors=colors)
        cv2.imshow("Music Visualization", colored_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    frame_step = max(1, int(tempo / 60))

    weights = [
        [(np.sin(frame * 0.1 + (i * 2 * np.pi / num_images)) + 1) / 2 for i in range(num_images)]
        for frame in range(frames)
    ]

    frame_idx = 0
    while True:
        # Get the weights for the current frame
        current_weights = weights[frame_idx]

        # Recalculate the blended image dynamically
        blended_image = np.zeros_like(images[0])
        for img, weight in zip(images, current_weights):
            blended_image += weight * img
        blended_image = np.clip(blended_image, 0, 1)

        # Apply colors to the blended image
        colored_image = color_art_pixel(blended_image, colors=colors)

        # Display the image
        cv2.imshow("Music Visualization", colored_image)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Increment the frame index based on the frame step
        frame_idx = (frame_idx + frame_step) % frames

    cv2.destroyAllWindows()

images = []
colors = []
tempos = []
# input_music="C:\\Users\\18155\\Programming\\MusicVis\\separated\\htdemucs_6s\\s006_2\\bass.wav"
# features = get_features(input_music, time_chunk=4)
# for f in features:
#     if f is not None:
#         img1, color, tempo = map_features(f)
#         colors.append(color)
#         images.append(img1)
#         tempos.append(tempo)
#         break
#     img1, color, tempo = map_features(f)
#     colors.append(color)
#     images.append(img1)
#     tempos.append(tempo)
#     break

# input_music="separated/htdemucs_6s/s001/bass.wav"
# features = get_features(input_music, time_chunk=4)
# for f in features:
#     img1, color, tempo = map_features(f)
#     colors.append(color)
#     images.append(img1)
#     tempos.append(tempo)
#     break

# input_music="separated/htdemucs_6s/s001/drums.wav"
# features = get_features(input_music, time_chunk=4)
# for f in features:
#     img2, color, tempo = map_features(f)
#     colors.append(color)
#     images.append(img2)
#     tempos.append(tempo)
#     break

# input_music="separated/htdemucs_6s/s001/guitar.wav"
# features = get_features(input_music, time_chunk=4)
# for f in features:
#     img3, color, tempo = map_features(f)
#     colors.append(color)
#     images.append(img3)
#     tempos.append(tempo)
#     break

# input_music="separated/htdemucs_6s/s001/other.wav"
# features = get_features(input_music, time_chunk=4)
# for f in features:
#     img4, color, tempo = map_features(f)
#     colors.append(color)
#     images.append(img4)
#     tempos.append(tempo)
#     break

# input_music="separated/htdemucs_6s/s001/vocals.wav"
# features = get_features(input_music, time_chunk=4)
# for f in features:
#     img5, color, tempo = map_features(f)
#     colors.append(color)
#     images.append(img5)
#     tempos.append(tempo)
#     break

# display_animation(images, colors, tempo=np.mean(tempos))

