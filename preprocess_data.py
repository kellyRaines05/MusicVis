"""
Preprocess audio data to extract spectrograms and labels, saving them as NumPy arrays.

Functions:
    - get_spectrograms(): Converts audio waveform to normalized mel-spectrogram.
    - get_data(): Loads audio file and extracts spectrogram and labels.
    - get_all_data(): Processes all audio files in a folder and saves spectrograms and labels.
    - clip_quality_labels(): Filters quality labels to specific attributes and saves the filtered data.
"""

import os
import json
import librosa
import numpy as np
from multiprocessing import get_context

def get_spectrograms(y, sr, eps=1e-6):
    mel = librosa.feature.melspectrogram(y=y, sr=sr)
    mel_db = librosa.power_to_db(mel)

    mean = np.mean(mel_db)
    std = np.std(mel_db)
    Xstd = (mel_db - mean) / (std + eps)

    _min, _max = np.min(Xstd), np.max(Xstd)
    norm_max = _max
    norm_min = _min

    if (_max - _min) > eps:
        V = np.clip(Xstd, norm_min, norm_max)
        V = 255 * (V - norm_min) / (norm_max - norm_min)
    else:
        V = np.zeros_like(Xstd, dtype=np.float32)

    return V.astype(np.float32)

def get_data(args):
    key, data, audio_folder = args
    audio_filename = f"{key}.wav"
    file_path = os.path.join(audio_folder, audio_filename)

    label = {"source": data[key]["instrument_source"], "family": data[key]["instrument_family"], "quality": data[key]["qualities"]}

    if os.path.exists(file_path):
        y, sr = librosa.load(file_path, sr=None)
        spectrogram = get_spectrograms(y, sr)
        return spectrogram, label
    else:
        print(f"Warning: Audio file not found for key '{key}'")
        return None, None

def get_all_data(folder, file_prefix):
    json_path = os.path.join(folder, "examples.json")
    audio_folder = os.path.join(folder, "audio")

    with open(json_path, "r") as f:
        data = json.load(f)

    tasks = [(key, data, audio_folder) for key in data.keys()]

    spectrograms = []
    labels = []
    with get_context("spawn").Pool() as pool:
        results = pool.map(get_data, tasks)

    for spectrogram, label in results:
        if label is not None and spectrogram is not None:
            spectrograms.append(spectrogram)
            labels.append(label)

    y_source = np.array([item['source'] for item in labels], dtype=np.float32)
    y_family = np.array([item['family'] for item in labels], dtype=np.float32)
    y_quality = np.array([item['quality'] for item in labels], dtype=np.float32)
    
    np.save(f"{file_prefix}/y_source.npy", y_source)
    np.save(f"{file_prefix}/y_family.npy", y_family)
    np.save(f"{file_prefix}/quality.npy", y_quality)
    np.save(f"{file_prefix}/spectrograms.npy", np.array(spectrograms))
    
    return spectrograms, labels

def clip_quality_labels(file_prefix, quality_labels_path):
    target_indices = [0, 1, 7, 8]  # bright, dark, percussive, reverb
    spectrograms = np.load(f"{file_prefix}/spectrograms.npy")
    qualities = np.load(quality_labels_path)

    qualities = qualities[:, target_indices]
    mask = qualities.sum(axis=1) > 0

    spectrograms_filtered = spectrograms[mask]
    qualities_filtered = qualities[mask]

    print(f"Before filtering: {spectrograms.shape[0]}")
    print(f"After filtering: {spectrograms_filtered.shape[0]}")

    np.save(f"{file_prefix}/spectrograms_filtered.npy", spectrograms_filtered)
    np.save(f"{file_prefix}/quality_subset.npy", qualities_filtered)

if __name__ == '__main__':
    training_folder = "c:/Users/18155/Programming/nsynth_dataset/nsynth-train/"
    validation_folder = "c:/Users/18155/Programming/nsynth_dataset/nsynth-valid/"
    testing_folder = "c:/Users/18155/Programming/nsynth_dataset/nsynth-test/"

    spectrograms, labels = get_all_data(training_folder, "all_data/training_data")
    print(f"Loaded {len(labels)} labels.")

    clip_quality_labels("all_data/training_data", "all_data/training_data/quality.npy")
    clip_quality_labels("all_data/validation_data", "all_data/validation_data/quality.npy")
    clip_quality_labels("all_data/testing_data", "all_data/testing_data/quality.npy")