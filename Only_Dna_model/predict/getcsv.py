#!/usr/bin/env python3
import argparse
import csv
import sys
import os

# Configure command-line arguments
parser = argparse.ArgumentParser(description="Extract the first two lines from the input file and create a CSV file with idx, seqs, id, name, and label columns.")
parser.add_argument("input_file", help="Input file, such as a FASTA file")
parser.add_argument("output_file", help="Output CSV file")
args = parser.parse_args()

# Get the input and output file paths
input_file = args.input_file
output_file = args.output_file

# Check that the input file exists
if not os.path.isfile(input_file):
    print(f"Error: Input file {input_file} does not exist")
    sys.exit(1)

# Read the first two lines of the input file
try:
    with open(input_file, "r") as f:
        # Read all lines
        lines = f.readlines()
        # Remove trailing line breaks
        lines = [line.strip() for line in lines]
        
        # Require at least two lines
        if len(lines) < 2:
            print(f"Error: {input_file} must contain at least two lines")
            sys.exit(1)
        
        # Extract the first two lines
        first_line = lines[0]
        second_line = lines[1]
except Exception as e:
    print(f"Error: Could not read {input_file}: {e}")
    sys.exit(1)

# Prepare the CSV row
csv_data = [{
    "idx": first_line,
    "seqs": second_line,
    "id": -1,
    "name": -1,
    "label": -1
}]

# Write the CSV output
try:
    with open(output_file, "w", newline="") as f:
        # Define the CSV columns
        fieldnames = ["idx", "seqs", "id", "name", "label"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write the header
        writer.writeheader()
        
        # Write the data row
        writer.writerows(csv_data)
except Exception as e:
    print(f"Error: Could not write {output_file}: {e}")
    sys.exit(1)

print(f"Created {output_file}")
