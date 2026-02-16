"""
Step 0: Download Massachusetts Housing Data from Kaggle
Uses kagglehub to programmatically download the dataset.
"""

import kagglehub
import shutil
import os
import glob

# Target directory
TARGET_DIR = 'data/raw/'
TARGET_FILE = 'data/raw/ma_housing_raw.csv'

def download_dataset():
    """Download the Massachusetts housing dataset from Kaggle."""
    
    print("Downloading Massachusetts Housing Data from Kaggle...")
    print("This may take a few moments...\n")
    
    # Download latest version
    path = kagglehub.dataset_download("vraj105/massachusetts-housing-data")
    
    print(f"✓ Dataset downloaded to: {path}\n")
    
    # Find all CSV files in the downloaded path
    csv_files = glob.glob(os.path.join(path, "*.csv"))
    
    if not csv_files:
        print("ERROR: No CSV files found in downloaded dataset")
        return None
    
    # Take the first CSV file (should be the housing data)
    source_file = csv_files[0]
    print(f"Found data file: {os.path.basename(source_file)}")
    
    # Ensure target directory exists
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    # Copy to our project structure
    shutil.copy2(source_file, TARGET_FILE)
    print(f"✓ Copied to: {TARGET_FILE}")
    
    # Display file info
    file_size = os.path.getsize(TARGET_FILE) / (1024 * 1024)  # Convert to MB
    print(f"✓ File size: {file_size:.2f} MB")
    
    # Quick preview
    import pandas as pd
    df = pd.read_csv(TARGET_FILE, nrows=5)
    print(f"\n✓ Preview of data ({len(df)} rows shown):")
    print(df.head())
    
    print(f"\n✅ Dataset ready at: {TARGET_FILE}")
    return TARGET_FILE

if __name__ == "__main__":
    download_dataset()
