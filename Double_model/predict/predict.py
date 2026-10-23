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
from Models.resnet import ResidualNet, ResidualNet_one
from prefetch_generator import BackgroundGenerator
import pyfiglet
from pyfiglet import Figlet

# Print the banner
f = Figlet(font='doom')
print(f.renderText('MMNet x BuzzID'))
print('*'*80)
print('Start predicting with dual-modality model!!!')
print('*'*80)

# DataLoader with background prefetching
class DataLoaderX(DataLoader):
    def __iter__(self):
        return BackgroundGenerator(super().__iter__())

# Model parameters
ty = 'bumble'
L = 'l'
sizes = 512
dnalm = './Data/be5-dl/'
piclm = './Data/be5-p-512/'
batchsz = 20
lr = 1e-4
epochs = 5
num_workers = 0
num_class = 109

# Image dataset
class Pic(Dataset):
    def __init__(self, keys, path):
        super(Pic, self).__init__()
        self.path = path
        self.keys = keys
        self.env = lmdb.open(self.path, readonly=True, lock=False)

    def __len__(self):
        return len(self.keys)

    def __getitem__(self, idx):
        by = self.keys[idx]
        with self.env.begin(write=False) as txn:
            data = txn.get(by)
        img, _ = pickle.loads(data)
        return img

# DNA dataset
class Dna(Dataset):
    def __init__(self, keys, path):
        super(Dna, self).__init__()
        self.path = path
        self.keys = keys
        self.env = lmdb.open(self.path, readonly=True, lock=False)

    def __len__(self):
        return len(self.keys)

    def __getitem__(self, idx):
        with self.env.begin(write=False) as txn:
            img, _ = pickle.loads(txn.get(self.keys[idx]))
        return img

# Prediction function
def predict(modeld, modelp, dna_dl, pic_dl, species_map, output_file):
    modeld.eval()
    modelp.eval()
    predictions = []
    confidences = []
    species_names = []
    dna_contributions = []
    img_contributions = []
    device = torch.device('cpu')  # Use the CPU explicitly

    with torch.no_grad():
        for d, p in zip(dna_dl, pic_dl):
            dx = d.to(device)  # Keep DNA tensors on the CPU
            px = p.to(device)  # Keep image tensors on the CPU
            logits1 = modeld(dx)
            logits2 = modelp(px)
            logits = logits1 + logits2
            probs = torch.nn.functional.softmax(logits, dim=1)
            conf, pred = torch.max(probs, dim=1)
            
            indices = pred.unsqueeze(1)
            lw1 = torch.sigmoid(torch.gather(logits1, dim=1, index=indices.long()))
            lw2 = torch.sigmoid(torch.gather(logits2, dim=1, index=indices.long()))
            dna_w = lw1 / (lw1 + lw2)
            img_w = lw2 / (lw1 + lw2)

            pred = pred.numpy()
            conf = conf.numpy()
            dna_w = dna_w.numpy()
            img_w = img_w.numpy()

            for p, c, dw, iw in zip(pred, conf, dna_w, img_w):
                species = species_map.get(p, "Unknown")
                species_names.append(f"Bombus_{species}")
                predictions.append(p)
                confidences.append(c)
                dna_contributions.append(dw.item())
                img_contributions.append(iw.item())

    # Write the CSV output
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Prediction', 'Species', 'Confidence', 'DNA_Contribution', 'Image_Contribution'])
        for p, s, c, dw, iw in zip(predictions, species_names, confidences, dna_contributions, img_contributions):
            writer.writerow([p, s, c, dw, iw])

    return predictions, species_names, confidences, dna_contributions, img_contributions

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
    keys = pickle.loads(txn.get(b'keys'))

# Create the data loaders
dna_d = Dna(keys, dnalm)
pic_d = Pic(keys, piclm)
dna_dl = DataLoaderX(dna_d, batch_size=batchsz, num_workers=num_workers)
pic_dl = DataLoaderX(pic_d, batch_size=batchsz, num_workers=num_workers)

# Initialize the model
modeld = ResidualNet_one(50, num_class, 'CBAM')
modelp = ResidualNet(50, num_class, 'CBAM')

# Load the model weights
state_dp = '../train/CKPT/best-d.mdl'
state_pp = '../train/CKPT/best-p.mdl'

# Remove the module. prefix from state_dict keys
state_dict_d = torch.load(state_dp, map_location=torch.device('cpu'))
state_dict_d = {k.replace('module.', ''): v for k, v in state_dict_d.items()}
modeld.load_state_dict(state_dict_d)

state_dict_p = torch.load(state_pp, map_location=torch.device('cpu'))
state_dict_p = {k.replace('module.', ''): v for k, v in state_dict_p.items()}
modelp.load_state_dict(state_dict_p)

print(80*'*')
print('Loaded models from CKPT!!!')

# Run prediction and save the results
output_file = './Output/predict-be5-l-512-batchsz20-lr0.0001-epochs300-repeat0.csv'
predictions, species_names, confidences, dna_contributions, img_contributions = predict(modeld, modelp, dna_dl, pic_dl, species_map, output_file)

print(80*'*')
print('Prediction completed!')
print(f'Results saved to {output_file}')
print('Sample predictions:')
for i in range(min(5, len(predictions))):
    print(f'Prediction: {predictions[i]}, Species: {species_names[i]}, Confidence: {confidences[i]:.4f}, '
          f'DNA_Contribution: {dna_contributions[i]:.4f}, Image_Contribution: {img_contributions[i]:.4f}')
