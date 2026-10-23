#!/usr/bin/env python
# coding: utf-8

import os
import torch
import lmdb
import pickle
import pandas as pd
from torchvision import transforms
from torch.utils.data import Dataset,DataLoader
from PIL import Image
import argparse

parser = argparse.ArgumentParser(description='Train a Random Forest model on a CSV file.')
parser.add_argument('csv_file', type=str, help='Path to the CSV file for training')
args = parser.parse_args()
csv_file = args.csv_file
# Read the input CSV file from the first command-line argument
dflab = pd.read_csv(csv_file)

# Change the database name. Here, 'be' represents beetle.
dbname='be5'

def word2num(seq):
    a=torch.Tensor([[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])
    c=torch.Tensor([[0,1,0,0,0,0,0,0,0,0,0,0,0,0,0]])
    g=torch.Tensor([[0,0,1,0,0,0,0,0,0,0,0,0,0,0,0]])
    t=torch.Tensor([[0,0,0,1,0,0,0,0,0,0,0,0,0,0,0]])
    z=torch.Tensor([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])
    r=torch.Tensor([[0,0,0,0,1,0,0,0,0,0,0,0,0,0,0]])
    y=torch.Tensor([[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0]])
    m=torch.Tensor([[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0]])
    k=torch.Tensor([[0,0,0,0,0,0,0,1,0,0,0,0,0,0,0]])
    s=torch.Tensor([[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0]])
    w=torch.Tensor([[0,0,0,0,0,0,0,0,0,1,0,0,0,0,0]])
    h=torch.Tensor([[0,0,0,0,0,0,0,0,0,0,1,0,0,0,0]])
    b=torch.Tensor([[0,0,0,0,0,0,0,0,0,0,0,1,0,0,0]])
    v=torch.Tensor([[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0]])
    d=torch.Tensor([[0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]])
    n=torch.Tensor([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1]])
    result=torch.cat(list(eval(','.join(seq))),dim=0).unsqueeze(dim=0)
    return result

keys=[str(k).encode() for k in range(len(dflab))]

dirs = './Data'
if not os.path.exists(dirs):
    os.makedirs(dirs)

# Establish DNA sequences database. l->long sequences, s->short sequences
envdna = lmdb.open("./Data/{}-dl".format(dbname),map_size=109951162776*2)
txndna = envdna.begin(write=True)

for i,row in enumerate(dflab.iterrows()):
    seq=row[1]['seqs']
    label=row[1]['label']
    seq=word2num(seq)
    label=torch.tensor(label)
    txndna.put(key = str(i).encode(), value = pickle.dumps((seq,label)))
txndna.put(key=b'keys', value=pickle.dumps(keys))
txndna.put(key=b'len', value=pickle.dumps(len(keys)))
txndna.put(key=b'label', value=pickle.dumps(dflab.label))
txndna.commit()
envdna.close()

# Picture size
size=512


class Pic(Dataset):

    def __init__(self):
        super(Pic,self).__init__()
        self.seqs,self.labels=self.load_csv()

    def load_csv(self):
        seqs=list(dflab['img'])
        labels=list(dflab['label'])
        return seqs ,labels

    def __len__(self):
         return len(self.seqs)

    def __getitem__(self,idx):
        seq,label=self.seqs[idx],self.labels[idx]
        tf=transforms.Compose([
            lambda x:Image.open(x).convert('RGB'),
            transforms.Resize((size,size)),
#             transforms.CenterCrop(448),
            transforms.ToTensor(),
            normalize,
        ])
        img=tf(seq)
        label=torch.tensor(label)
        return img,label

normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
train_p=Pic()
train_pl = DataLoader(train_p, num_workers=0,collate_fn=lambda x: x)
envpic = lmdb.open("./Data/{}-p-{}".format(dbname,size),map_size=109951162776*2)
txnpic = envpic.begin(write=True)

for idx, data in enumerate(train_pl):
    image, label = data[0]
    txnpic.put(key = str(idx).encode(), value = pickle.dumps((image,label)))
txnpic.put(key =b'keys', value = pickle.dumps(keys))
txnpic.put(key =b'len', value = pickle.dumps(len(keys)))
txnpic.commit()
envpic.close()
