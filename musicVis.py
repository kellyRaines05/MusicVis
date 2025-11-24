"""
Music Visualization: Visualizes music characteristics using fine-grained texture generation based on cross-modal correspondences.

Functions:
    - musicVis(): main function orchestrating the process of music visualization.
    - map_features(): maps visual characteristics based on extracted music features and displays them.
"""

import time
from IPython.display import display, clear_output
import matplotlib.pyplot as plt
from algorithmic_art_characteristics import *
from music_feature_extraction import *
from stem_music import *

def map_features(input_music: str):
    features = get_features(input_music, time_chunk=4)


def musicVis(input_music: str):
    stemmed_file = stem_song(input_music)
    is_silent = detect_silence(stemmed_file)
    if is_silent:
        print("The input audio is silent. Exiting visualization.")
        return
    


def transition_frames(img1, img2, steps=30):
    img1_f = img1.astype(np.float32)
    img2_f = img2.astype(np.float32)

    frames = []
    for i in range(steps):
        alpha = i / (steps - 1)
        frame = (1 - alpha) * img1_f + alpha * img2_f
        frames.append(frame.astype(np.uint8))
    return frames

def show_transition(frames, delay=0.03):
    plt.figure(figsize=(4,4))
    for frame in frames:
        clear_output(wait=True)
        plt.imshow(frame)
        plt.axis('off')
        display(plt.gcf())
        time.sleep(delay)
