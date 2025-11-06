import torch
import numpy as np
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from music_feature_extraction import *
from torch.utils.data import DataLoader
from models import InstrumentData, InstrumentClassifier

training_folder = "all_data/training_data"
validation_folder = "all_data/validation_data"
testing_folder = "all_data/testing_data"

def evaluate_model(model, dataloader):
    model.eval()

    source_preds = []
    family_preds = []

    source_targets = []
    family_targets = []

    with torch.no_grad():
        for batch_X, batch_y_source, batch_y_family in dataloader:
            preds = model(batch_X)
            source_outputs = preds["source_logits"]
            family_outputs = preds["family_logits"]

            source_pred_classes = torch.argmax(source_outputs, dim=1)
            family_pred_classes = torch.argmax(family_outputs, dim=1)

            source_preds.append(source_pred_classes.cpu().numpy())
            family_preds.append(family_pred_classes.cpu().numpy())

            source_targets.append(batch_y_source.cpu().numpy())
            family_targets.append(batch_y_family.cpu().numpy())


    y_source_preds = np.concatenate(source_preds, axis=0)
    y_family_preds = np.concatenate(family_preds, axis=0)

    y_source_true = np.concatenate(source_targets, axis=0)
    y_family_true = np.concatenate(family_targets, axis=0)

    source_score = accuracy_score(y_source_true, y_source_preds)
    family_source = accuracy_score(y_family_true, y_family_preds)

    return y_source_preds, y_family_preds, y_source_true, y_family_true, source_score, family_source

def train_instrument_classifier(epochs=10, batch_size=64):
    model = InstrumentClassifier()
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print("LOADING DATA...")
    
    spectrograms_train_path = f"{training_folder}/spectrograms.npy"
    y_source_train_path = f"{training_folder}/y_source.npy"
    y_family_train_path = f"{training_folder}/y_family.npy"
    
    spectrograms_validation_path = f"{validation_folder}/spectrograms.npy"
    y_source_validation_path = f"{validation_folder}/y_source.npy"
    y_family_validation_path = f"{validation_folder}/y_family.npy"
    
    train_dataloader = DataLoader(dataset=InstrumentData(spectrograms_train_path, y_source_train_path, y_family_train_path), batch_size=batch_size, shuffle=True)
    validation_dataloader = DataLoader(dataset=InstrumentData(spectrograms_validation_path, y_source_validation_path, y_family_validation_path), batch_size=batch_size, shuffle=True)
    
    model.train()
    for epoch in range(epochs):
        print(f"Epoch {epoch+1}/{epochs}")
        
        total_loss = 0
        for batch_X, batch_y_source, batch_y_family in train_dataloader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            source_outputs = outputs["source_logits"]
            family_outputs = outputs["family_logits"]

            loss = (
                criterion(source_outputs, batch_y_source) +
                criterion(family_outputs, batch_y_family)
            )

            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        _, _, _, _, source_score, family_source = evaluate_model(model, validation_dataloader)
        print(f"ACCURACY SCORE (SOURCE): {source_score}")
        print(f"ACCURACY SCORE (FAMILY): {family_source}")
        torch.save(model.state_dict(), "models/instrument_classification_full.pth")
    return model

def test_model(model_path, batch_size=64):
    state_dict = torch.load(model_path)
    model = InstrumentClassifier()
    model.load_state_dict(state_dict)

    spectrograms_path = f"{testing_folder}/spectrograms.npy"
    y_source_test_path = f"{testing_folder}/y_source.npy"
    y_family_test_path = f"{testing_folder}/y_family.npy"
    testing_dataloader = DataLoader(dataset=InstrumentData(spectrograms_path, y_source_test_path, y_family_test_path), batch_size=batch_size, shuffle=True)

    y_source_preds, y_family_preds, y_source_true, y_family_true, source_score, family_source = evaluate_model(model, testing_dataloader)

    cm = confusion_matrix(y_source_true, y_source_preds)

    plt.figure(figsize=(24, 24))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix')
    plt.show()

    cm = confusion_matrix(y_family_true, y_family_preds)

    plt.figure(figsize=(24, 24))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix')
    plt.show()

    print(f"Model Accuracy on test set (source): {source_score}")
    print(f"Model Accuracy on test set (family): {family_source}")

# train_instrument_classifier()
test_model("C:/Users/18155/Programming/MusicVis/models/instrument_classification_full.pth")