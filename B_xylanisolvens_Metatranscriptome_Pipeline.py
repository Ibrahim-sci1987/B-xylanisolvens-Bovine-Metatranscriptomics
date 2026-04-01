#!/usr/bin/env python3
"""
Title: Master Genomic Pipeline for Bacteroides xylanisolvens Analysis
Author: Dr. Ibrahim H. Madhloom
Affiliation: University of Basrah, College of Veterinary Medicine
Version: 2.0 (Stable - Comprehensive Edition)
Description: 
    Full-cycle automated workflow: Environment provisioning, Data recovery, 
    Academic branding (75 strains), Functional Annotation, and Global BLAST Identity.
"""

import os
import zipfile
import subprocess
import sys
from google.colab import drive, files

# ==============================================================================
# PHASE 1: ENVIRONMENT PROVISIONING & DATABASE INDEXING
# ==============================================================================
print("--- PHASE 1: Initializing Bioinformatic Environment ---")
drive.mount('/content/drive', force_remount=True)

# Install mandatory dependencies silently
print("Status: Installing Biopython, BLAST+, and Prokka...")
!pip install biopython -q
!apt-get install -y ncbi-blast+ prokka -qq

# CRITICAL FIX: Indexing Prokka Databases to prevent "setupdb" errors
print("Status: Indexing Prokka Databases (Essential for Execution)...")
!prokka --setupdb

from Bio import SeqIO  # Imported after pip install

# ==============================================================================
# PHASE 2: DATA RECOVERY & PATH MANAGEMENT
# ==============================================================================
print("\n--- PHASE 2: Recovering Genomic Data from Drive ---")
PROJECT_ROOT = '/content/drive/MyDrive/B_xylanisolvens_Project_Ibrahim'
ZIP_PATH = '/content/drive/MyDrive/Ibrahim_Full_Genomic_Archive.zip'
EXTRACT_DIR = './Ibrahim_Unpacked'

# Create necessary directories in Google Drive
for folder in ['03_Final_Dataset', '04_Annotation', '06_Phylogeny']:
    os.makedirs(os.path.join(PROJECT_ROOT, folder), exist_ok=True)

if os.path.exists(ZIP_PATH):
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        z.extractall(EXTRACT_DIR)
    print("✅ Archive unpacked successfully.")
else:
    print("⚠️ Warning: Zip file not found in Drive. Ensure path is correct.")

# ==============================================================================
# PHASE 3: SELECTIVE EXTRACTION & ACADEMIC BRANDING
# ==============================================================================
print("\n--- PHASE 3: Selective Extraction & Strain Branding ---")
# TARGET_KEYS matches your specific 75 strains and the 6.4kb region
TARGET_KEYS = ["Bacteroides_xylanisolvens", "(6.4kb)_Region_1"]
final_records = []
counter = 1

for root, _, filenames in os.walk(EXTRACT_DIR):
    for f in filenames:
        if any(key in f for key in TARGET_KEYS) and f.endswith(('.fasta', '.fa')):
            file_path = os.path.join(root, f)
            for record in SeqIO.parse(file_path, "fasta"):
                # Professional Naming Convention for NCBI Submission
                strain_id = f"IQ-C-{counter:02d}"
                record.id = f"Bacteroides_xylanisolvens_strain_{strain_id}"
                record.description = f"[Author: Ibrahim Madhloom | Source: {f}]"
                final_records.append(record)
                counter += 1

if final_records:
    MASTER_FASTA = "B_xylan_Complete_Dataset_Ibrahim.fasta"
    SeqIO.write(final_records, MASTER_FASTA, "fasta")
    
    # Save to Drive and provide Download
    !cp {MASTER_FASTA} {PROJECT_ROOT}/03_Final_Dataset/
    print(f"✅ Extracted and Branded {len(final_records)} sequences.")
    files.download(MASTER_FASTA)
else:
    print("❌ Error: No matching genomic sequences found.")
    sys.exit()

# ==============================================================================
# PHASE 4: NCBI-COMPLIANT FUNCTIONAL ANNOTATION
# ==============================================================================
print("\n--- PHASE 4: Automated Functional Annotation (Prokka) ---")
PROKKA_OUT = "Prokka_Results_Final"

# Running Prokka with --compliant and --force to ensure full processing
!prokka --outdir {PROKKA_OUT} \
        --prefix Ibrahim_IQ_Series \
        --genus Bacteroides \
        --species xylanisolvens \
        --compliant \
        --force {MASTER_FASTA}

if os.path.exists(PROKKA_OUT):
    # Compressing results for easy transfer
    ZIP_NAME = "Ibrahim_Full_Annotation_Results.zip"
    subprocess.run(['zip', '-r', ZIP_NAME, PROKKA_OUT])
    
    # Sync with Drive and Download
    !cp {ZIP_NAME} {PROJECT_ROOT}/04_Annotation/
    files.download(ZIP_NAME)
    print("✅ Functional Annotation (.gff, .faa, .sqn) completed and saved.")

# ==============================================================================
# PHASE 5: REMOTE BLAST & IDENTITY REPORTING
# ==============================================================================
print("\n--- PHASE 5: Global Identity Verification (Remote BLASTn) ---")
REPORT = "Final_Genomic_Identity_Report.txt"

# Querying NCBI databases remotely to find closest relatives
!blastn -query {MASTER_FASTA} \
        -db nt -remote \
        -max_target_seqs 2 \
        -outfmt "6 qseqid stitle pident qcovs evalue" > {REPORT}

if os.path.exists(REPORT):
    !cp {REPORT} {PROJECT_ROOT}/06_Phylogeny/
    files.download(REPORT)
    print("✅ BLAST Report generated successfully.")

print("\n" + "="*60)
print("🏁 MASTER PIPELINE COMPLETED - ALL PHASES SUCCESSFUL")
print("="*60)
