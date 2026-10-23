#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import shutil

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="BuzzID: DNA sequence and dual-modality prediction pipeline (Version 1.2):\n",
        epilog="Examples:\n"
               "  DNA only:\n python buzzid.py --model 1 --fa demo/demo_appositus.fa\n"
               "  DNA and image:\n python buzzid.py --model 2 --fa demo/demo_ardens.fa --img demo/demo_ardens.jpg",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--model", choices=["1", "2"], help="Model type ('1' for single modality(DNA), '2' for dual modality)")
    parser.add_argument("--fa", help="Input FASTA file path (required)")
    parser.add_argument("--img", help="Input image file path (required for --model 2)")
    parser.add_argument("-v", "--version", action="store_true", help="Show version number and exit")
    return parser.parse_args()

def run_command(command, error_msg):
    """Run a shell command and check its exit status"""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error: {error_msg}\nCommand output: {e.stderr}")
        sys.exit(1)

def main():
    args = parse_args()

    # Handle the version option
    if args.version:
        print("BuzzID Version: 1.2")
        sys.exit(0)

    # Check the --model argument
    if not args.model:
        print("Error: --model is required (use --model 1 or --model 2)")
        sys.exit(1)

    # Check the --fa argument
    if not args.fa:
        print("Error: --fa is required and must specify a FASTA file")
        sys.exit(1)

    # Check that the input FASTA file exists
    if not os.path.isfile(args.fa):
        print(f"Error: Input file {args.fa} does not exist")
        sys.exit(1)

    # Extract the input file name and stem
    input_path = os.path.abspath(args.fa)
    input_filename = os.path.basename(input_path)
    input_basename = os.path.splitext(input_filename)[0]

    if args.model == "1":
        # DNA-only prediction workflow
        # Prediction directory
        predict_dir = "Only_Dna_model/predict"
        if not os.path.isdir(predict_dir):
            print(f"Error: Directory {predict_dir} does not exist")
            sys.exit(1)

        # Step 1: Copy the input file
        dest_fasta = os.path.join(predict_dir, f"{input_basename}.fa")
        try:
            shutil.copy(input_path, dest_fasta)
            print(f"Copied: {input_path} -> {dest_fasta}")
        except Exception as e:
            print(f"Error: Could not copy files to {dest_fasta}: {e}")
            sys.exit(1)

        # Step 2: Change to the prediction directory
        try:
            os.chdir(predict_dir)
            print(f"Changed directory to: {predict_dir}")
        except Exception as e:
            print(f"Error: Could not change to directory {predict_dir}: {e}")
            sys.exit(1)

        # Step 3: Run MAFFT
        aligned_fasta = f"{input_basename}_aligned.fa"
        mafft_cmd = f"mafft --add {input_basename}.fa --keeplength ../../data/coi5p_clean_109_aligned.fasta > {aligned_fasta}"
        run_command(mafft_cmd, "MAFFT failed")
        print(f"MAFFT alignment completed: {aligned_fasta}")

        # Step 4: Normalize the aligned FASTA record
        getfa_cmd = f"python getfa.py {aligned_fasta}"
        run_command(getfa_cmd, "getfa.py failed")
        print(f"Aligned FASTA record normalized")

        # Step 5: Build the prediction CSV file
        csv_file = f"{input_basename}.csv"
        getcsv_cmd = f"python getcsv.py {aligned_fasta} {csv_file}"
        run_command(getcsv_cmd, "getcsv.py failed")
        print(f"Prediction CSV created: {csv_file}")

        # Step 6: Build the DNA LMDB from the CSV file
        seq_cmd = f"python seq_onlyDNA.py {csv_file}"
        run_command(seq_cmd, "seq_onlyDNA.py failed")
        print(f"DNA LMDB created")

        # Step 7: Remove intermediate files
        files_to_delete = [f"{input_basename}.fa", aligned_fasta, csv_file]
        for file in files_to_delete:
            if os.path.isfile(file):
                try:
                    os.remove(file)
                    print(f"Removed: {file}")
                except Exception as e:
                    print(f"Warning: Could not remove {file}: {e}")
            else:
                print(f"Warning: File {file} does not exist; skipping removal")

        # Step 8: Run predict_dna.py and print the final prediction
        seq_final_cmd = "python predict_dna.py"
        print("\nRunning final DNA prediction:")
        result = run_command(seq_final_cmd, "predict_dna.py failed")
        print(result.stdout)

    elif args.model == "2":
        # DNA and image prediction workflow
        # Check the --img argument
        if not args.img:
            print("Error: --model 2 requires --img with an image file path")
            sys.exit(1)

        # Check that the image file exists
        if not os.path.isfile(args.img):
            print(f"Error: Image file {args.img} does not exist")
            sys.exit(1)

        # Extract the image file name
        img_path = os.path.abspath(args.img)
        img_filename = os.path.basename(img_path)

        # Prediction directory
        predict_dir = "Double_model/predict"
        tmp_dir = os.path.join(predict_dir, "tmp")
        if not os.path.isdir(predict_dir):
            print(f"Error: Directory {predict_dir} does not exist")
            sys.exit(1)
        if not os.path.isdir(tmp_dir):
            try:
                os.makedirs(tmp_dir)
                print(f"Created directory: {tmp_dir}")
            except Exception as e:
                print(f"Error: Could not create directory {tmp_dir}: {e}")
                sys.exit(1)

        # Step 1: Copy the FASTA and image files and rename the FASTA file
        dest_fasta = os.path.join(tmp_dir, f"{input_basename}.fa")
        dest_img = os.path.join(tmp_dir, img_filename)
        try:
            shutil.copy(input_path, dest_fasta)
            shutil.copy(img_path, dest_img)
            print(f"Copied: {input_path} -> {dest_fasta}")
            print(f"Copied: {img_path} -> {dest_img}")
        except Exception as e:
            print(f"Error: Could not copy files to {tmp_dir}: {e}")
            sys.exit(1)

        # Step 2: Change to the prediction directory
        try:
            os.chdir(predict_dir)
            print(f"Changed directory to: {predict_dir}")
        except Exception as e:
            print(f"Error: Could not change to directory {predict_dir}: {e}")
            sys.exit(1)

        # Step 3: Run MAFFT
        aligned_fasta = f"tmp/{input_basename}_aligned.fa"
        mafft_cmd = f"mafft --add tmp/{input_basename}.fa --keeplength ../../data/coi5p_clean_109_aligned.fasta > {aligned_fasta}"
        run_command(mafft_cmd, "MAFFT failed")
        print(f"MAFFT alignment completed: {aligned_fasta}")

        # Step 4: Normalize the aligned FASTA record
        getfa_cmd = f"python getfa.py {aligned_fasta}"
        run_command(getfa_cmd, "getfa.py failed")
        print(f"Aligned FASTA record normalized")

        # Step 5: Build the prediction CSV file
        csv_file = f"tmp/{input_basename}.csv"
        getcsv_cmd = f"python getcsv.py {aligned_fasta} --img tmp/{img_filename} {csv_file}"
        run_command(getcsv_cmd, "getcsv.py failed")
        print(f"Prediction CSV created: {csv_file}")

        # Step 6: Build the DNA and image LMDB data
        seq_cmd = f"python seq.py {csv_file}"
        run_command(seq_cmd, "seq.py failed")
        print(f"DNA and image LMDB data created")

        # Step 7: Remove temporary files
        tmp_subdir = "tmp"
        files_to_delete = [
            f"{tmp_subdir}/{input_basename}.fa",
            f"{tmp_subdir}/{input_basename}_aligned.fa",
            f"{tmp_subdir}/{img_filename}",
            f"{tmp_subdir}/{input_basename}.csv"
        ]
        if not os.path.isdir(tmp_subdir):
                print(f"Warning: Temporary directory {tmp_subdir} does not exist; skipping removal")
        else:
                print(f"Temporary directory contents: {os.listdir(tmp_subdir)}")  # Show temporary directory contents
                for file in files_to_delete:
                        if os.path.isfile(file):
                                try:
                                        os.remove(file)
                                        print(f"Removed: {file}")
                                except Exception as e:
                                        print(f"Warning: Could not remove {file}: {e}")
                        else:
                                print(f"Warning: File {file} does not exist; skipping removal")
	
        # Step 8: Run predict.py and print the final prediction
        predict_cmd = "python predict.py"
        print("\nRunning final dual-modality prediction:")
        result = run_command(predict_cmd, "predict.py failed")
        print(result.stdout)

    else:
        print(f"Error: Unsupported model type {args.model}")
        sys.exit(1)

if __name__ == "__main__":
    main()
