"""
Stem audio files into separate components using Demucs and detect silence in audio files.

Functions:
- stem_song(file): Stems the input audio file into separate components using Demucs.
- detect_silence(file): Detects if the entire audio file is silent.
"""

import shlex
# import os
import numpy as np
from pydub import AudioSegment, silence
import demucs.separate

model = "htdemucs_6s"

def stem_song(file):
    demucs.separate.main(shlex.split(f'-n {model} {file}'))
    output = file.split("/")
    return f"separated/{model}/{output[len(output) - 1]}"

def detect_silence(y, sr):
    audio = AudioSegment(
        (y * 32767).astype(np.int16).tobytes(),
        frame_rate=sr,
        sample_width=2,
        channels=1
    )
    silence_times = silence.detect_silence(audio, min_silence_len=1000, silence_thresh=-35)

    if len(silence_times) == 1 and silence_times[0][1] == len(audio):
        return True
    else:
        return False

# music_clips_dir = "C:/Users/18155/Programming/MusicVis/all_data/music_clips/"
# for file_name in os.listdir(music_clips_dir):
#     if file_name.endswith(".wav"):
#         file_path = os.path.join(music_clips_dir, file_name)
#         stem_song(file_path)