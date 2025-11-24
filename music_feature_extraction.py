"""
All feature extraction functions for high-level music characteristics.

This includes pitch detection, velocity detection, spectral centroid calculation, tempo estimation,
instrument source (acoustic, synthetic, electric), instrument family classification, and quality classification.

Functions:
- detect_pitch(): Detects the predominant pitches in the audio and returns them as MIDI note numbers.
- detect_velocity(): Estimates the velocity (loudness) of the audio.
- detect_centroid(): Calculates the spectral centroid of the audio.
- estimate_tempo(): Estimates the tempo (BPM) of the audio.
- detect_instrument(): Classifies the instrument source and family using a pre-trained model.
- detect_quality(): Classifies the quality of the audio using a pre-trained model.
- get_features(): Processes an audio file in chunks and extracts all features concurrently.
"""

import crepe
import numpy as np
import librosa
import torch
from models import *
from preprocess_data import get_spectrograms
# from concurrent.futures import ThreadPoolExecutor

def detect_pitch(audio, sr):
    _, frequency, _, _ = crepe.predict(audio, sr, model_capacity="small", step_size=150, viterbi=True)
    midi = 69 + 12 * np.log2(frequency / 440.0)
    notes = np.rint(midi).astype(int)
    notes = np.unique(notes)
    return notes

def detect_velocity(audio, sr):
    onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
    return np.max(onset_env)

def detect_centroid(audio, sr):
    cent = librosa.feature.spectral_centroid(y=audio, sr=sr)
    return np.mean(cent)

def estimate_tempo(audio, sr):
    onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
    tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=sr)
    return tempo[0]

def detect_instrument(audio, sr):
    state_dict = torch.load("models/instrument_classification_full.pth")
    model = InstrumentClassifier()
    model.load_state_dict(state_dict)

    input = get_spectrograms(audio, sr=sr)
    input = torch.from_numpy(input).float().unsqueeze(0).repeat(3, 1, 1).unsqueeze(0)

    prediction = model(input)
    
    source_outputs = torch.argmax(prediction["source_logits"], dim=1)
    family_outputs = torch.argmax(prediction["family_logits"], dim=1)

    return source_outputs, family_outputs

def detect_quality(audio, sr):
    state_dict = torch.load("models/quality_classification.pth")
    model = QualityClassifier()
    model.load_state_dict(state_dict)

    input = get_spectrograms(audio, sr=sr)
    input = torch.from_numpy(input).float().unsqueeze(0).repeat(3, 1, 1).unsqueeze(0)

    logits = model(input)
    probs = torch.sigmoid(logits)
    output = (probs > 0.5).float()

    return output

def get_features(file, time_chunk=4):
    y, sr = librosa.load(file, sr=None)
    notes = detect_pitch(y, sr)
    velocity = detect_velocity(y, sr)
    centroid = detect_centroid(y, sr)
    tempo = estimate_tempo(y, sr)
    quality = detect_quality(y, sr)
    instrument = detect_instrument(y, sr)

    chunk_features = MusicFeatures(
        notes,
        velocity,
        centroid,
        tempo,
        quality,
        instrument[0],
        instrument[1]
    )

    



# Streamed version of get_features for attempting real-time processing
# def get_features(file, time_chunk=4):
#     sr = librosa.get_samplerate(file)
#     frame_length = 2048
#     hop_length = 512
#     block_length = int((sr * time_chunk) / hop_length)
#     stream = librosa.stream(file, block_length=block_length, frame_length=frame_length, hop_length=hop_length, mono=True, dtype=np.float32)

#     with ThreadPoolExecutor(max_workers=15) as executor:
#         for y in stream:
#             notes = executor.submit(detect_pitch, y, sr)
#             velocity = executor.submit(detect_velocity, y, sr)
#             centroid = executor.submit(detect_centroid, y, sr)
#             tempo = executor.submit(estimate_tempo, y, sr)
#             quality = executor.submit(detect_quality, y, sr)
#             instrument = executor.submit(detect_instrument, y, sr)

#             chunk_features = MusicFeatures(
#                 notes,
#                 velocity,
#                 centroid,
#                 tempo,
#                 quality,
#                 instrument.result()[0],
#                 instrument.result()[1]
#             )
            
#             yield chunk_features