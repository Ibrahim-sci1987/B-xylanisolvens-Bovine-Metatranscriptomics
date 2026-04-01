"""
Title: Integrated Genomic Pipeline for B. xylanisolvens Analysis
Author: Dr. Ibrahim H. Madhloom
Affiliation: University of Basrah, College of Veterinary Medicine
Description: Professional workflow for bulk strain extraction and functional annotation.
"""

import os
import zipfile
import subprocess
from google.colab import drive, files

# ==============================================================================
# PHASE 1: SYSTEM PROVISIONING (Fixes 'ModuleNotFoundError' & 'setupdb' error)
# ==============================================================================
print("--- PHASE 1: Initializing Bioinformatic Environment ---")
drive.mount('/content/drive', force_remount=True)

# Install mandatory dependencies
!pip install biopython -q
!apt-get install -y ncbi-blast+ prokka -qq

# Critical: This command fixes the "databases have not been indexed" error
print("Status: Indexing Prokka Databases (SetupDB)...")
!prokka --setupdb

from Bio import SeqIO # Imported after installation

# ==============================================================================
# PHASE 2 & 3: DATA RECOVERY
# ==============================================================================
print("\n--- PHASE 2 & 3: Recovering Genomic Data ---")
PROJECT_ROOT = '/content/drive/MyDrive/B_xylanisolvens_Project_Ibrahim'
ZIP_PATH = '/content/drive/MyDrive/Ibrahim_Full_Genomic_Archive.zip'
EXTRACT_DIR = './Ibrahim_Unpacked'

if os.path.exists(ZIP_PATH):
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        z.extractall(EXTRACT_DIR)
    print("✅ Archive successfully unpacked.")

# ==============================================================================
# PHASE 4: BULK EXTRACTION & BRANDING (75 Strains + 6.4kb Fragment)
# ==============================================================================
print("\n--- PHASE 4: Selective Extraction & Academic Branding ---")
TARGET_KEYS = ["Bacteroides_xylanisolvens", "(6.4kb)_Region_1"]
final_records = []
counter = 1

for root, _, filenames in os.walk(EXTRACT_DIR):
    for f in filenames:
        if any(key in f for key in TARGET_KEYS) and f.endswith(('.fasta', '.fa')):
            for record in SeqIO.parse(os.path.join(root, f), "fasta"):
                new_id = f"IQ-C-{counter:02d}"
                record.id = f"Bacteroides_xylanisolvens_strain_{new_id}"
                record.description = f"[Source: {f}]"
                final_records.append(record)
                counter += 1

if final_records:
    MASTER_FASTA = "B_xylan_Complete_Dataset_Ibrahim.fasta"
    SeqIO.write(final_records, MASTER_FASTA, "fasta")
    !cp {MASTER_FASTA} {PROJECT_ROOT}/03_Final_Dataset/
    files.download(MASTER_FASTA)
    print(f"✅ Extracted {len(final_records)} sequences for NCBI submission.")

# ==============================================================================
# PHASE 5: FUNCTIONAL ANNOTATION (NCBI COMPLIANT)
# ==============================================================================
print("\n--- PHASE 5: Full Functional Annotation ---")
PROKKA_OUT = "Prokka_Results_Final"
# Running Prokka on the 75 strains
!prokka --outdir {PROKKA_OUT} --prefix Ibrahim_IQ_Series --compliant --force {MASTER_FASTA}

if os.path.exists(PROKKA_OUT):
    ZIP_NAME = "Ibrahim_Full_Annotation_Results.zip"
    subprocess.run(['zip', '-r', ZIP_NAME, PROKKA_OUT])
    !cp {ZIP_NAME} {PROJECT_ROOT}/04_Annotation/
    files.download(ZIP_NAME)
    print("✅ All functional formats (.gff, .faa, .sqn) are ready.")

# ==============================================================================
# PHASE 6 & 7: GLOBAL IDENTITY (BLASTn)
# ==============================================================================
print("\n--- PHASE 6 & 7: Global Identity Report ---")
REPORT = "Final_Genomic_Identity_Report.txt"
!blastn -query {MASTER_FASTA} -db nt -remote -max_target_seqs 2 -outfmt "6 qseqid stitle pident qcovs evalue" > {REPORT}
!cp {REPORT} {PROJECT_ROOT}/06_Phylogeny/
files.download(REPORT)

print("\n" + "="*60 + "\n🏁 MASTER PIPELINE COMPLETED SUCCESSFULLY\n" + "="*60)
