import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset

class Data(Dataset):
    def __init__(self, spectrograms_path, y_source_path, y_family_path):
        self.spectrograms = np.load(spectrograms_path, mmap_mode='r')
        self.y_source = np.load(y_source_path, mmap_mode='r')
        self.y_family = np.load(y_family_path, mmap_mode='r')
        self.len = self.spectrograms.shape[0]

    def __getitem__(self, index):
        x = np.copy(self.spectrograms[index])
        y_source = int(self.y_source[index])
        y_family = int(self.y_family[index])

        x = torch.from_numpy(x).float().unsqueeze(0).repeat(3, 1, 1)
        y_source = torch.tensor(y_source).long()
        y_family = torch.tensor(y_family).long()
        return x, y_source, y_family

    def __len__(self):
        return self.len

class SoundClassifier(nn.Module):
    def __init__(self, num_families=11, num_sources=3):
        super(SoundClassifier, self).__init__()
        
        self.cnn = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((4, 4))
        )

        self.fc_shared = nn.Sequential(
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32)
        )

        self.fc_family = nn.Linear(32, num_families)
        self.fc_source = nn.Linear(32, num_sources)

    def forward(self, x):
        x = self.cnn(x)
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc_shared(x))

        family_logits = self.fc_family(x)
        source_logits = self.fc_source(x)

        return {
            "source_logits": source_logits,
            "family_logits": family_logits
        }

class MusicVis(nn.Module):
    def __init__(self, input_channels=7, output_channels=3):
    
    # should have memory of previous images generated within the same song!
    # low resolution --> 32x32x3
    # upscale --> 1024x1024x3
        return
    def forward(self, x):
        return