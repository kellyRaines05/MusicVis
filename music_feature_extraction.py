import crepe
import numpy as np
import time
import librosa
from concurrent.futures import ThreadPoolExecutor

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
    return librosa.feature.spectral_centroid(y=audio, sr=sr)

def estimate_tempo(audio, sr):
    onset_env = librosa.onset.onset_strength(y=audio, sr=sr)
    tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=sr)
    return tempo[0]

def get_features(file, time_chunk=4):
    sr = librosa.get_samplerate(file)
    frame_length = 2048
    hop_length = 512
    block_length = int((sr * time_chunk) / hop_length)
    stream = librosa.stream(file, block_length=block_length, frame_length=frame_length, hop_length=hop_length, mono=True, dtype=np.float32)

    with ThreadPoolExecutor(max_workers=15) as executor:
        for y in stream:
            notes = executor.submit(detect_pitch, y, sr)
            velocity = executor.submit(detect_velocity, y, sr)
            centroid = executor.submit(detect_centroid, y, sr)
            tempo = executor.submit(estimate_tempo, y, sr)

            chunk_features = {
                'notes': notes.result(),
                'velocity': velocity.result(),
                'centroid': centroid.result(),
                'tempo': tempo.result()
            }
            
            yield chunk_features

start = time.time()
file = "C:/Users/18155/Programming/MusicVis/separated/htdemucs_6s/s006_2/piano.wav"
for i, features in enumerate(get_features(file)):
    print(f"Chunk {i+1}")
    print(features)
print(time.time() - start)
