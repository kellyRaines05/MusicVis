import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, Subset
from PIL import Image
import torchvision.transforms as T
import torchvision.models as models
import torch.optim as optim
import os
from sklearn.model_selection import KFold
from model import UNet

class ImageDataset(Dataset):
    def __init__(self, images):
        self.images = images
        self.input_transform = T.Compose([
            T.Resize((8, 8), interpolation=T.InterpolationMode.NEAREST),
            T.ToTensor()
        ])
        self.target_transform = T.Compose([
            T.Resize((128, 128), interpolation=T.InterpolationMode.BICUBIC),
            T.ToTensor()
        ])

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img = self.images[idx]
        low_res = self.input_transform(img)
        high_res = self.target_transform(img)

        return low_res, high_res
    
def create_dataset(image_folder):
    augmentation_transformations = [
        T.RandomHorizontalFlip(p=1.0),
        T.RandomVerticalFlip(p=1.0),
        T.RandomRotation(degrees=30),
        T.RandomRotation(degrees=-30),
        T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
    ]

    images = [os.path.join(image_folder, fname) for fname in os.listdir(image_folder) if fname.lower().endswith(('.jpg'))]
    augmented_images = []
    for image_path in images:
        img = Image.open(image_path).convert('RGB')
        augmented_images.append(img)

        for transform in augmentation_transformations:
            augmented_img = transform(img)
            augmented_images.append(augmented_img)
        
    return ImageDataset(augmented_images)

def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=10):
    best_val_loss = float('inf')

    vgg = models.vgg16().features[:16].eval()
    for param in vgg.parameters():
        param.requires_grad = False
    
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for low_res, high_res in train_loader:
            low_res, high_res = low_res, high_res

            optimizer.zero_grad()
            outputs = model(low_res)

            # pixel data MSE and perceptual MSE loss
            loss = criterion(outputs, high_res) + 0.1 * criterion(vgg(outputs), vgg(high_res))
            
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        epoch_loss = running_loss / len(train_loader)
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {epoch_loss:.4f}")
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for low_res, high_res in val_loader:
                low_res, high_res = low_res, high_res

                outputs = model(low_res)
                loss = criterion(outputs, high_res) + 0.1 * criterion(vgg(outputs), vgg(high_res))
                val_loss += loss.item()
        
        avg_val_loss = val_loss / len(val_loader)
        print(f"Validation Loss: {avg_val_loss:.4f}")
        
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), 'best_model.pth')
    return model

def kfold_cross_validation(folder_path, k=5, num_epochs=10):
    dataset = create_dataset(folder_path)
    kf = KFold(n_splits=k, shuffle=True, random_state=42)
        
    for fold, (train_idx, val_idx) in enumerate(kf.split(dataset)):
        print(f"Training Fold {fold + 1}/{k}...")
        
        train_subset = Subset(dataset, train_idx)
        val_subset = Subset(dataset, val_idx)

        train_loader = DataLoader(train_subset, batch_size=50, shuffle=True)
        val_loader = DataLoader(val_subset, batch_size=50, shuffle=False)

        model = UNet()
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=1e-4)

        model = train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs)
    return model

kfold_cross_validation("C:/Users/kelly/Programming/Music-Synthesis/music_images")