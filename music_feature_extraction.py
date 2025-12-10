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
import pyloudnorm as pyln
from preprocess_data import get_spectrograms
from concurrent.futures import ThreadPoolExecutor
from models import *
from stem_music import detect_silence

def detect_pitch(audio, sr):
    _, frequency, _, _ = crepe.predict(audio, sr, model_capacity="small", step_size=150, viterbi=True)
    midi = 69 + 12 * np.log2(frequency / 440.0)
    notes = np.rint(midi).astype(int)
    notes = np.unique(notes)
    return notes

def detect_velocity(audio, sr):
    return librosa.onset.onset_strength(y=audio, sr=sr)

def detect_loudness(audio, sr):
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    meter = pyln.Meter(sr)
    return meter.integrated_loudness(audio)

def detect_centroid(audio, sr):
    cent = librosa.feature.spectral_centroid(y=audio, sr=sr)
    return cent

def detect_flatness(audio, sr):
    flatness = librosa.feature.spectral_flatness(y=audio)
    return flatness

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
    sr = librosa.get_samplerate(file)
    frame_length = 2048
    hop_length = 512
    block_length = int((sr * time_chunk) / hop_length)
    stream = librosa.stream(file, block_length=block_length, frame_length=frame_length, hop_length=hop_length, mono=True, dtype=np.float32, fill_value=0)

    with ThreadPoolExecutor(max_workers=15) as executor:
        for n, y in enumerate(stream):
            silent = executor.submit(detect_silence, y, sr)
            if silent.result():
                yield None
                continue
            else:
                block_time = librosa.blocks_to_time(n, block_length=block_length, hop_length=hop_length, sr=sr)
                notes = executor.submit(detect_pitch, y, sr)
                velocity = executor.submit(detect_velocity, y, sr)
                loudness = executor.submit(detect_loudness, y, sr)
                centroid = executor.submit(detect_centroid, y, sr)
                flatness = executor.submit(detect_flatness, y, sr)
                tempo = executor.submit(estimate_tempo, y, sr)
                quality = executor.submit(detect_quality, y, sr)
                instrument = executor.submit(detect_instrument, y, sr)
                instrument_sources = instrument.result()[0].item()

                chunk_features = MusicFeatures(
                    time=block_time,
                    notes=notes.result(),
                    velocity=velocity.result(),
                    loudness=loudness.result(),
                    centroid=centroid.result(),
                    flatness=flatness.result(),
                    tempo=tempo.result(),
                    quality=quality.result(),
                    instrument_sources=instrument_sources
                )
                
                yield chunk_features
