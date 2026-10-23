#!/usr/bin/env python3
from __future__ import division
import numpy as np
import lmdb
import pickle
from torchvision import transforms
from PIL import Image
import pandas as pd
import random
from torch.utils import data
import os, glob, csv, torch, torchvision
from torch.utils.data import Dataset, DataLoader
from torchvision.models import resnet18
from torchvision import models
from torch import nn
from Models.resnet import ResidualNet_one  # Import the DNA model architecture
from prefetch_generator import BackgroundGenerator
import pyfiglet
from pyfiglet import Figlet

# Print the banner
f = Figlet(font='doom')
print(f.renderText('PREDICT'))
print('*'*80)
print('Start predicting with DNA only model!!!')
print('*'*80)

# DataLoader with background prefetching
class DataLoaderX(DataLoader):
    def __iter__(self):
        return BackgroundGenerator(super().__iter__())

# Model parameters
ty = 'bombus'
L = 'l'
sizes = 512
dnalm = './Data/be5-dl'
batchsz = 20
lr = 1e-4
epochs = 300
num_workers = 0
num_class = 109

# Dataset that loads sequence tensors only
class Dna(Dataset):
    def __init__(self, keys, path):
        super(Dna).__init__()
        self.path = path
        self.keys = keys
        self.env = lmdb.open(self.path, readonly=True, lock=False)

    def __len__(self):
        return len(self.keys)

    def __getitem__(self, idx):
        with self.env.begin(write=False) as txn:
            img = pickle.loads(txn.get(self.keys[idx]))[0]  # Use only the sequence tensor and ignore the label
        return img

# Prediction function
def predict(model, data_dl, species_map, output_file):
    model.eval()
    predictions = []
    confidences = []
    species_names = []
    device = torch.device('cpu')  # Use the CPU explicitly

    with torch.no_grad():
        for x in data_dl:
            x = x.to(device)  # Keep input tensors on the CPU
            logits = model(x)
            probs = torch.nn.functional.softmax(logits, dim=1)
            conf, pred = torch.max(probs, dim=1)
            
            # Convert tensors to NumPy arrays
            pred = pred.numpy()
            conf = conf.numpy()
            
            # Map predicted labels to species names
            for p in pred:
                species = species_map.get(p, "Unknown")
                species_names.append(f"Bombus_{species}")
                predictions.append(p)
                confidences.append(conf[list(pred).index(p)])

    # Write the CSV output
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Prediction', 'Species', 'Confidence'])
        for p, s, c in zip(predictions, species_names, confidences):
            writer.writerow([p, s, c])

    return predictions, species_names, confidences

# Create the output directory
ou = './Output/'
if not os.path.exists(ou):
    os.makedirs(ou)

# Read the species label mapping
s2l_df = pd.read_csv('../../data/species_label_109.csv')
species_map = dict(zip(s2l_df['Label'], s2l_df['Species']))

# Load the dataset
env = lmdb.open(dnalm, readonly=True, lock=False)
with env.begin(write=False) as txn:
    keys = pickle.loads(txn.get(b'keys'))  # Load all sample keys

# Create the data loaders
data_d = Dna(keys, dnalm)
data_dl = DataLoaderX(data_d, batch_size=batchsz, num_workers=num_workers)

# Initialize the model
model = ResidualNet_one(50, num_class, 'CBAM')

# Load the model weights
state_d = '../train/CKPT/best-d.mdl'
state_dict = torch.load(state_d, map_location=torch.device('cpu'))
# Remove the module. prefix from state_dict keys
state_dict = {k.replace('module.', ''): v for k, v in state_dict.items()}
model.load_state_dict(state_dict)

print(80*'*')
print('Loaded DNA model from CKPT!!!')

# Run prediction and save the results
output_file = './Output/predict-dna-only-{}-{}-{}-batchsz{}-lr{}-epochs{}-repeat0.csv'.format(ty, L, sizes, batchsz, lr, epochs)
predictions, species_names, confidences = predict(model, data_dl, species_map, output_file)

print(80*'*')
print('Prediction completed!')
print(f'Results saved to {output_file}')
print('Sample predictions:')
for i in range(min(5, len(predictions))):
    print(f'Prediction: {predictions[i]}, Species: {species_names[i]}, Confidence: {confidences[i]:.4f}')
