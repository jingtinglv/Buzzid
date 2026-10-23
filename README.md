# BuzzID v1.2

[中文说明](README_CN.md)

MMNet-Based Multimodal Identification of Bombus Species Using Sequence and Image Data.

BuzzID v1.2 is a CPU inference package for identifying 109 *Bombus* species. The included MMNet models were trained for two prediction modes:

- DNA only: predicts a species from a COI-5P FASTA sequence.
- DNA and image: combines a COI-5P sequence with a specimen image.

## Requirements

- Linux
- Conda
- Git LFS
- MAFFT available on `PATH`

Create the supplied environment:

```bash
conda env create -f environment.yml
conda activate BuzzID
```

If MAFFT is not already installed, install it in the environment:

```bash
conda install -c bioconda mafft
```

## Download

The trained model files are stored with Git LFS.

```bash
git lfs install
git clone https://github.com/jingtinglv/Buzzid.git
cd Buzzid
git lfs pull
```

## Usage

Show the command-line options:

```bash
python buzzid.py --help
```

DNA-only prediction:

```bash
python buzzid.py --model 1 --fa demo/demo_appositus.fa
```

DNA and image prediction:

```bash
python buzzid.py --model 2 --fa demo/demo_ardens.fa --img demo/demo_ardens.jpg
```

An additional *Bombus terrestris* sequence and image pair is available in `demo/`.

Prediction CSV files are written under the corresponding `predict/Output/` directory, and the result is also printed in the terminal.

## Models and reference data

- Number of species: 109
- DNA checkpoint: `best-d.mdl`
- Image checkpoint: `best-p.mdl`
- Reference alignment: `data/coi5p_clean_109_aligned.fasta`
- Label mapping: `data/species_label_109.csv`
- DNA encoding: 15 channels in the order `acgtrymkswhbvdn`
- Image preprocessing: 512 × 512 pixels with ImageNet mean and standard deviation normalization
- Multimodal fusion: addition of the DNA and image logits

The DNA-only workflow uses the DNA branch checkpoint. The multimodal workflow uses both the DNA and image branch checkpoints from the same MMNet repeat.

## Directory structure

| Path | Purpose |
| --- | --- |
| `buzzid.py` | Main command-line entry point. |
| `data/` | COI-5P reference alignment and the 109-species label map. |
| `demo/` | Example FASTA sequences and specimen images. |
| `Only_Dna_model/predict/` | DNA preprocessing and CPU inference scripts. |
| `Only_Dna_model/train/CKPT/` | DNA-only checkpoint used for inference. |
| `Double_model/predict/` | DNA and image preprocessing and CPU inference scripts. |
| `Double_model/train/CKPT/` | DNA and image checkpoints used for inference. |
| `environment.yml` | Conda environment definition. |
| `MODEL_UPDATE_REPORT.md` | Model replacement and configuration record for v1.2. |

The `Data/`, `tmp/`, and `Output/` subdirectories inside the prediction folders are created or populated during execution.

## Version

This repository contains BuzzID v1.2. The command below prints the package version:

```bash
python buzzid.py --version
```

## License

Unless a file states otherwise, this repository is distributed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license](LICENSE). Commercial use is not permitted under this license. Third-party components retain their original notices and terms; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

