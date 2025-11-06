import torch
import numpy as np
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from music_feature_extraction import *
from torch.utils.data import DataLoader
from models import QualityData, QualityClassifier

training_folder = "all_data/training_data"
validation_folder = "all_data/validation_data"
testing_folder = "all_data/testing_data"

def evaluate_model(model, dataloader):
    model.eval()

    preds = []
    targets = []

    with torch.no_grad():
        for batch_X, batch_y in dataloader:
            logits = model(batch_X)
            probs = torch.sigmoid(logits)
            output = (probs > 0.5).float()
            preds.append(output.cpu().numpy())
            targets.append(batch_y.cpu().numpy())

    preds = np.concatenate(preds, axis=0)
    targets = np.concatenate(targets, axis=0)
    score = np.all(preds == targets, axis=1).mean()

    return preds, targets, score

def train_quality_classifier(epochs=10, batch_size=64):
    model = QualityClassifier()
    
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print("LOADING DATA...")
    
    spectrograms_train_path = f"{training_folder}/spectrograms_filtered.npy"
    quality_train_path = f"{training_folder}/quality_subset.npy"
    
    spectrograms_validation_path = f"{validation_folder}/spectrograms_filtered.npy"
    quality_validation_path = f"{validation_folder}/quality_subset.npy"
    
    train_dataloader = DataLoader(dataset=QualityData(spectrograms_train_path, quality_train_path), batch_size=batch_size, shuffle=True)
    validation_dataloader = DataLoader(dataset=QualityData(spectrograms_validation_path, quality_validation_path), batch_size=batch_size, shuffle=True)
    
    model.train()
    best_score = 0.0
    for epoch in range(epochs):
        print(f"Epoch {epoch+1}/{epochs}")
        
        total_loss = 0
        for batch_X, batch_y in train_dataloader:
            optimizer.zero_grad()
            outputs = model(batch_X)

            loss = criterion(outputs, batch_y)

            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        _, _, score = evaluate_model(model, validation_dataloader)
        print(f"ACCURACY SCORE: {score}")
        if score > best_score:
            best_score = score
            torch.save(model.state_dict(), "models/quality_classification.pth")

def plot_multilabel_confusion_matrices(preds, targets, class_names):
    num_classes = preds.shape[1]

    for i in range(num_classes):
        cm = confusion_matrix(targets[:, i], preds[:, i])
        plt.figure(figsize=(4, 4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
        plt.title(f'Confusion Matrix for "{class_names[i]}"')
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.show()


def test_model(model_path, batch_size=64):
    class_names = ["bright", "dark", "percussive", "reverb"]
    state_dict = torch.load(model_path)
    model = QualityClassifier()
    model.load_state_dict(state_dict)

    spectrograms_path = f"{testing_folder}/spectrograms_filtered.npy"
    quality_test_path = f"{testing_folder}/quality_subset.npy"
    testing_dataloader = DataLoader(dataset=QualityData(spectrograms_path, quality_test_path), batch_size=batch_size, shuffle=True)

    preds, targets, score = evaluate_model(model, testing_dataloader)
    plot_multilabel_confusion_matrices(preds, targets, class_names)

    print(f"Model Accuracy on test set: {score}")
    
# train_quality_classifier()
test_model("C:/Users/18155/Programming/MusicVis/models/quality_classification.pth")