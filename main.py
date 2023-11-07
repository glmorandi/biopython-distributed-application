from Bio import AlignIO, SeqIO
from Bio.Align.Applications import ClustalOmegaCommandline
import os

# Define the input and output file names
input_file = "ls_orchid.gbk"
temp_file = "temp.fasta"
output_file = "aligned_sequences.fasta"

# Function to load sequences from a GenBank file and save as FASTA
def load_sequences(input_file, temp_file):
    sequences = SeqIO.parse(input_file, "genbank")
    SeqIO.write(sequences, temp_file, "fasta")

# Function to perform sequence alignment with Clustal Omega
def perform_alignment(input_file, output_file):
    clustalomega_cline = ClustalOmegaCommandline(infile=input_file, outfile=output_file, verbose=True, auto=True)
    stdout, stderr = clustalomega_cline()

# Clean up temporary files
def cleanup_temp_files():
    os.remove(temp_file)
    os.remove(output_file)

if __name__ == "__main":
    # Load sequences
    load_sequences(input_file, temp_file)

    # Perform alignment
    perform_alignment(temp_file, output_file)

    # Load the resulting alignment
    alignment = AlignIO.read(output_file, "fasta")

    # Display the alignment
    print("Sequences Alignment:")
    print(alignment)

    # Clean up temporary files
    cleanup_temp_files()
