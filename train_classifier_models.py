import numpy as np
import librosa
from sklearn import RandomForestClassifier
import torch
import torch.nn as nn
import torch.nn.functional as F

class SoundClassifier(nn.Module):
    def __init__(self, input_channels, num_classes):
        super(SoundClassifier, self).__init__()
        self.conv1 = nn.Conv2d(input_channels, 32, kernel_size=3)
        self.pool1 = nn.MaxPool2d(kernel_size=2)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3)
        self.pool2 = nn.MaxPool2d(kernel_size=2)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3)
        self.pool3 = nn.MaxPool2d(kernel_size=2)
        self.fc1 = nn.Linear(self.get_flattened_size(), 128)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(128, num_classes)

    def get_flattened_size(self):
        # This function helps calculate the correct input size for the first linear layer.
        # It's a placeholder; you need to calculate this based on your spectrogram dimensions.
        # Example calculation for a 128x128 spectrogram:
        # 128 -> (128-2)/1 + 1 = 127 -> 127/2 = 63.5 -> 63
        # 63 -> (63-2)/1 + 1 = 62 -> 62/2 = 31
        # 31 -> (31-2)/1 + 1 = 30 -> 30/2 = 15
        # The output size would be 15x15 * 128 (channels)
        return 128 * 15 * 15 # This is an example, adjust for your data

    def forward(self, x):
        x = self.pool1(F.relu(self.conv1(x)))
        x = self.pool2(F.relu(self.conv2(x)))
        x = self.pool3(F.relu(self.conv3(x)))
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

training_folder = "c:/Users/18155/Programming/nsynth_dataset/nsynth-train/audio"
validation_folder = "c:/Users/18155/Programming/nsynth_dataset/nsynth-valid/audio"
testing_folder = "c:/Users/18155/Programming/nsynth_dataset/nsynth-test/audio"


instrument_families = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # bass, brass, flute, guitar, keyboard, mallet, organ, reed, string, synth_lead, vocal
note_qualities = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] # bright, dark, distortion, fast_decay, long_release, multiphonic, nonlinear_env, percussive, reverb, tempo-synced



def train_source_classifier():
    instrument_sources = [0, 1, 2] # acoustic, electric, synthetic
    model = SoundClassifier(input_channels=1, num_classes=len(instrument_sources))

    
    return

def train_family_classifier():
    return

def train_quality_classifier():
    return


sr = librosa.get_samplerate(file)
frame_length = 2048
hop_length = 512
stream = librosa.stream(file, block_length=256, frame_length=frame_length, hop_length=hop_length, mono=True, dtype=np.float32)

n_mels = 128
mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
mel_spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)
