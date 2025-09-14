import numpy as np
import librosa
from models import SourceClassifier
from models import ImageGenerator
from music_feature_extraction import * 

training_folder = "c:/Users/18155/Programming/nsynth_dataset/nsynth-train/audio"
validation_folder = "c:/Users/18155/Programming/nsynth_dataset/nsynth-valid/audio"
testing_folder = "c:/Users/18155/Programming/nsynth_dataset/nsynth-test/audio"

def get_spectograms(file):
    y, sr = librosa.load(file)
    return librosa.feature.melspectrogram(y=y, sr=sr)

def train_source_classifier():
    instrument_sources = [0, 1, 2]
    model = SourceClassifier(input_channels=1, num_classes=len(instrument_sources))
    # for 

    
    return

def train_family_classifier():
    instrument_families = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # bass, brass, flute, guitar, keyboard, mallet, organ, reed, string, synth_lead, vocal

    return

def train_quality_classifier():
    note_qualities = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] # bright, dark, distortion, fast_decay, long_release, multiphonic, nonlinear_env, percussive, reverb, tempo-synced

    return

def train_image_generator():
    return

file = "c:/Users/18155/Programming/nsynth_dataset/nsynth-train/audio/"
time_chunk=4
sr = librosa.get_samplerate(file)
frame_length = 2048
hop_length = 512
block_length = int((sr * time_chunk) / hop_length)
stream = librosa.stream(file, block_length=block_length, frame_length=frame_length, hop_length=hop_length, mono=True, dtype=np.float32)
for y in stream:
    print(y)