import crepe
import numpy as np
import librosa
import torch
from concurrent.futures import ThreadPoolExecutor
from models import *
from preprocess_data import get_spectrograms

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

def detect_classifier_features(audio):
    instrument_sources, instrument_families = detect_instrument(audio)
    quality = detect_quality(audio)


def get_features(file, time_chunk=4):
    sr = librosa.get_samplerate(file)
    frame_length = 2048
    hop_length = 512
    block_length = int((sr * time_chunk) / hop_length)
    stream = librosa.stream(file, block_length=block_length, frame_length=frame_length, hop_length=hop_length, mono=True, dtype=np.float32)
    for y in stream:
        quality = detect_quality(y, sr)
        instrument_sources, instrument_families = detect_instrument(y, sr)
        print("Instruments Source:", instrument_sources)
        print("Instruments Family:", instrument_families)
        print("Quality:", quality)
        
    # with ThreadPoolExecutor(max_workers=15) as executor:
    #     for y in stream:
    #         notes = executor.submit(detect_pitch, y, sr)
    #         velocity = executor.submit(detect_velocity, y, sr)
    #         centroid = executor.submit(detect_centroid, y, sr)
    #         tempo = executor.submit(estimate_tempo, y, sr)

    #         chunk_features = {
    #             'notes': notes.result(),
    #             'velocity': velocity.result(),
    #             'centroid': centroid.result(),
    #             'tempo': tempo.result()
    #         }
            
    #         yield chunk_features

get_features("C:/Users/18155/Programming/MusicVis/separated/htdemucs_ft/s003/other.wav")