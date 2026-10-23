#!/usr/bin/env python
# coding: utf-8

import os
import sys
import torch
import lmdb
import pickle
import pandas as pd

# Require a CSV file on the command line
if len(sys.argv) < 2:
    print("Usage: python seq_onlyDNA.py <input.csv>")
    sys.exit(1)

csv_file = sys.argv[1]  # Read the CSV file name from the command line

# Read the CSV file
dflab = pd.read_csv(csv_file)

# Database name
dbname = 'be5'

# One-hot encoding for DNA bases
def word2num(seq):
    base_map = {
        'a': torch.Tensor([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]),
        'c': torch.Tensor([[0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]),
        'g': torch.Tensor([[0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]),
        't': torch.Tensor([[0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]),
        'z': torch.Tensor([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]),
        'r': torch.Tensor([[0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]),
        'y': torch.Tensor([[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]]),
        'm': torch.Tensor([[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]]),
        'k': torch.Tensor([[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]]),
        's': torch.Tensor([[0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]]),
        'w': torch.Tensor([[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]]),
        'h': torch.Tensor([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]]),
        'b': torch.Tensor([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]]),
        'v': torch.Tensor([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]]),
        'd': torch.Tensor([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]]),
        'n': torch.Tensor([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]])
    }

    # Convert the DNA sequence to a one-hot matrix
    result = torch.cat([base_map.get(char, base_map['n']) for char in seq], dim=0).unsqueeze(dim=0)
    return result

# Generate record keys
keys = [str(k).encode() for k in range(len(dflab))]

# Create the storage directory
dirs = './Data'
if not os.path.exists(dirs):
    os.makedirs(dirs)

# Create an LMDB database for DNA sequences
envdna = lmdb.open(f"./Data/{dbname}-dl", map_size=109951162776*2)
txndna = envdna.begin(write=True)

# Store each CSV record in LMDB
for i, row in enumerate(dflab.itertuples()):
    seq = row.seqs
    label = row.label
    seq_tensor = word2num(seq)
    label_tensor = torch.tensor(label)
    txndna.put(key=str(i).encode(), value=pickle.dumps((seq_tensor, label_tensor)))

# Store metadata
txndna.put(key=b'keys', value=pickle.dumps(keys))
txndna.put(key=b'len', value=pickle.dumps(len(keys)))
txndna.put(key=b'label', value=pickle.dumps(dflab.label.to_list()))
txndna.commit()
envdna.close()

print(f"DNA data were written to LMDB ({csv_file})")

