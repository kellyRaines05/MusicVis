"""
Stem audio files into separate components using Demucs and detect silence in audio files.

Functions:
- stem_song(file): Stems the input audio file into separate components using Demucs.
- detect_silence(file): Detects if the entire audio file is silent.
"""

import shlex
import librosa
# import os
import demucs.separate

model = "htdemucs_6s"

def stem_song(file):
    demucs.separate.main(shlex.split(f'-n {model} {file}'))
    output = file.split("/")
    return f"separated/{model}/{output[len(output) - 1]}"

def detect_silence(audio, sr, top_db=25, min_silence_len=1.0):
    min_silence_samples = int(min_silence_len * sr)
    non_silent_intervals = librosa.effects.split(audio, top_db=top_db, frame_length=2048, hop_length=512)
    if len(non_silent_intervals) == 0:
        return True

    total_non_silent_duration = sum(end - start for start, end in non_silent_intervals)
    if total_non_silent_duration < min_silence_samples:
        return True

    return False

# music_clips_dir = "C:/Users/18155/Programming/MusicVis/all_data/music_clips/"
# for file_name in os.listdir(music_clips_dir):
#     if file_name.endswith(".wav"):
#         file_path = os.path.join(music_clips_dir, file_name)
#         stem_song(file_path)