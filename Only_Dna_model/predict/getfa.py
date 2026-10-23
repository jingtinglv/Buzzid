#!/usr/bin/env python3
from Bio import SeqIO
from Bio.Seq import Seq
import sys
import argparse

# Configure command-line arguments
parser = argparse.ArgumentParser(description="Keep only the final FASTA record, replace '-' with 'z', and write the sequence on one line.")
parser.add_argument("input_fa", help="Input FASTA file")
args = parser.parse_args()

# Get the input file from the command-line arguments
input_fa = args.input_fa

# Read all records from the input FASTA file
try:
    sequences = list(SeqIO.parse(input_fa, "fasta"))
except Exception as e:
    print(f"Error: Could not read {input_fa}: {e}")
    sys.exit(1)

if not sequences:
    print(f"Error: {input_fa} contains no sequence records")
    sys.exit(1)

# Select the final sequence record
last_sequence = sequences[-1]

# Replace '-' with 'z' and remove line breaks from the sequence
modified_sequence = str(last_sequence.seq).replace("-", "z").replace("\n", "")

# Convert the modified sequence back to a Seq object
last_sequence.seq = Seq(modified_sequence)

# Overwrite the input file with the modified final record on one line
try:
    with open(input_fa, "w") as output_handle:
        # Write FASTA manually to keep the sequence on one line
        output_handle.write(f">{last_sequence.id}\n")
        output_handle.write(f"{str(last_sequence.seq)}\n")
except Exception as e:
    print(f"Error: Could not write {input_fa}: {e}")
    sys.exit(1)
