"""
This Python script scans the `.tif` files in a given source folder, filters only the files whose names
start with a number that exactly matches the allowed set of numbers (prefixes), and moves these files to the specified target folder.

🎯 Purpose:
- Extract `.tif` files that start with specific IDs (e.g. satellite image IDs, region codes, cartesian tile numbers, etc.)
  in bulk and move them to another folder.
- For example: if the IDs of cloudy lakes have been defined manually in the `allowed_prefixes` set beforehand,
  this script moves only the `.tif` files that start with these IDs.

📥 Inputs:
- `source_folder`: Main source folder. It may contain many `.tif` files and subfolders.
- `allowed_prefixes`: Only file names that start with one of these numbers are processed.

📤 Outputs:
- All `.tif` files that start with an allowed ID are moved into `target_folder`.
- The subfolder structure is preserved and recreated the same way in the target folder.

🔁 Processing:
1. All `.tif` files under `source_folder` are scanned with `os.walk()`.
2. The leading number (`leading_number`) is extracted from each file name.
   - E.g.: `"34_lake_tile_01.tif"` → `"34"`
3. If this number is in the `allowed_prefixes` set:
   - The file is moved into the target folder with the same subfolder structure (using `shutil.move()`).
4. A progress bar is shown with `tqdm`.
5. At the end, all matching files have been successfully moved to the target folder.

"""


import os
import shutil
import re
from tqdm import tqdm

# Folder paths
source_folder = r"path\to\input"
target_folder = r"path\to\output"
os.makedirs(target_folder, exist_ok=True)

# Only EXACTLY matching numbers
allowed_prefixes = {
    "3", "12", "13"   # Add more allowed prefixes as needed
}

def extract_exact_leading_number(filename):
    match = re.match(r"^(\d+)", filename)
    return match.group(1) if match else None

# 🔁 Scan the .tif files in all subfolders
tif_files = []
for root, dirs, files in os.walk(source_folder):
    for file in files:
        if file.lower().endswith(".tif"):
            full_path = os.path.join(root, file)
            tif_files.append(full_path)

# 🔄 Start processing with a progress bar
for source_path in tqdm(tif_files, desc="Filtering TIF files"):
    filename = os.path.basename(source_path)
    leading_number = extract_exact_leading_number(filename)

    if leading_number in allowed_prefixes:
        # Relative path → computed relative to source_folder
        relative_path = os.path.relpath(source_path, source_folder)
        target_path = os.path.join(target_folder, relative_path)

        # Create the target folder
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        # Move the file
        shutil.move(source_path, target_path)

print("Filtering and moving completed.")