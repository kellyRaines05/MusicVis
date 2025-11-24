import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import pandas as pd
import os
import matplotlib.pyplot as plt

class SoundArtDataset(Dataset):
    def __init__(self, csv_path, image_dir, transform=None):
        self.data = pd.read_csv(csv_path)
        self.image_dir = image_dir
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        features = torch.tensor(row[1:].values, dtype=torch.float32)
        img_name = row[0]
        img_path = os.path.join(self.image_dir, img_name)
        image = Image.open(img_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        return features, image

class SoundToArt(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(4, 128),
            nn.ReLU(),
            nn.Linear(128, 8 * 8 * 64),
            nn.ReLU()
        )
        self.deconv = nn.Sequential(
            nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(32, 16, 4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(16, 3, 4, stride=2, padding=1),
            nn.Sigmoid()
        )

    def forward(self, x):
        x = self.fc(x)
        x = x.view(-1, 64, 8, 8)
        return self.deconv(x)

transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor()
])

csv_path = "/content/your_features.csv"       # <-- UPDATE THIS
image_dir = "/content/art_images"             # <-- UPDATE THIS

dataset = SoundArtDataset(csv_path, image_dir, transform=transform)
loader = DataLoader(dataset, batch_size=16, shuffle=True)

# 6. Train
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SoundToArt().to(device)
criterion = nn.L1Loss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

for epoch in range(10):
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        out = model(x)
        loss = criterion(out, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print(f"Epoch {epoch+1}, Loss: {loss.item():.4f}")

# 7. Visualize
model.eval()
test_x, _ = next(iter(loader))
test_x = test_x.to(device)
with torch.no_grad():
    gen_images = model(test_x).cpu()

fig, axes = plt.subplots(1, 8, figsize=(16, 2))
for i, img in enumerate(gen_images[:8]):
    axes[i].imshow(img.permute(1, 2, 0))
    axes[i].axis('off')
plt.show()
