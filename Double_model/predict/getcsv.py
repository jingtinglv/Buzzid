#!/usr/bin/env python3
import argparse
import csv
import sys
import os

parser = argparse.ArgumentParser(description="Extract the first two lines from the input file and create a CSV file with idx, seqs, id, name, label, and img columns.")
parser.add_argument("input_file", help="Input file, such as a FASTA file")
parser.add_argument("output_file", help="Output CSV file")
parser.add_argument("--img", required=True, help="Image file path")
args = parser.parse_args()

input_file = args.input_file
output_file = args.output_file
img_file = args.img

if not os.path.isfile(input_file):
    print(f"Error: Input file {input_file} does not exist")
    sys.exit(1)

if not os.path.isfile(img_file):
    print(f"Error: Image file {img_file} does not exist")
    sys.exit(1)

try:
    with open(input_file, "r") as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
        if len(lines) < 2:
            print(f"Error: {input_file} must contain at least two lines")
            sys.exit(1)
        first_line = lines[0]
        second_line = lines[1]
except Exception as e:
    print(f"Error: Could not read {input_file}: {e}")
    sys.exit(1)

csv_data = [{
    "idx": first_line,
    "seqs": second_line,
    "id": -1,
    "name": -1,
    "label": -1,
    "img": img_file
}]

try:
    with open(output_file, "w", newline="") as f:
        fieldnames = ["idx", "seqs", "id", "name", "label", "img"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
except Exception as e:
    print(f"Error: Could not write {output_file}: {e}")
    sys.exit(1)

print(f"Created {output_file}")
