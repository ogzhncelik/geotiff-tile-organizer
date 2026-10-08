"""
This Python script checks the intersection between the spatial extents of the reference TIF files
in one folder and the TIF files in another folder, and moves the intersecting ones
to the target folder.

🎯 Purpose:
- Detect TIF files that overlap with the raster extents in the reference TIF folder
- Move these TIF files to the specified target folder without breaking the subfolder structure

📥 Input:
- `reference_tif_folder`: Folder containing the reference TIF files used for the intersection check
- `tif_folder`: Main folder containing the TIF raster files to be checked (including subfolders)

📤 Output:
- `output_folder`: Target folder where the TIF files that intersect the reference TIFs will be moved

🔧 Processing:
1. The bounds of all TIF files in the reference folder are read with rasterio and a list of geometries is created.
2. The bounds of each TIF file in the folder to be checked are read.
3. If the CRS is different, the reference geometries are reprojected.
4. If there is an intersection, the file is moved to the target folder.
"""

import os
import shutil
import rasterio
from shapely.geometry import box
from shapely.ops import transform
from pyproj import Transformer
from tqdm import tqdm


# ============ FILE PATHS ============
reference_tif_folder = r"path\to\reference"
tif_folder = r"path\to\input"
output_folder = r"path\to\output"
# ====================================

# Create the target folder
os.makedirs(output_folder, exist_ok=True)


# 1) Read the geometries and CRS information of the reference TIFs
print("Reading reference TIF files...")
reference_geoms = []  # (geometry, crs) pairs

for root, dirs, files in os.walk(reference_tif_folder):
    for file in files:
        if file.lower().endswith(".tif"):
            ref_path = os.path.join(root, file)
            try:
                with rasterio.open(ref_path) as src:
                    bounds = src.bounds
                    geom = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
                    reference_geoms.append((geom, src.crs))
            except Exception as e:
                print(f"Could not read reference TIF ({ref_path}): {e}")

print(f"  → {len(reference_geoms)} reference geometries loaded.\n")


# 2) List the TIF files to be checked
tif_paths = []
for root, dirs, files in os.walk(tif_folder):
    for file in files:
        if file.lower().endswith(".tif"):
            tif_paths.append(os.path.join(root, file))

print(f"{len(tif_paths)} TIF files will be checked.\n")


# 3) Helper function: convert a geometry to a different CRS
def reproject_geom(geom, src_crs, dst_crs):
    """Converts a geometry from src_crs to dst_crs."""
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    return transform(transformer.transform, geom)


# 4) Check the intersection for each TIF file
moved_count = 0
for tif_path in tqdm(tif_paths, desc="Checking TIF Files"):
    try:
        with rasterio.open(tif_path) as src:
            bounds = src.bounds
            raster_geom = box(bounds.left, bounds.bottom, bounds.right, bounds.top)
            raster_crs = src.crs

        # Intersection check with the reference geometries
        intersects = False
        for ref_geom, ref_crs in reference_geoms:
            # If the CRS is different, convert the reference geometry to the raster CRS
            if ref_crs != raster_crs:
                ref_geom_proj = reproject_geom(ref_geom, ref_crs, raster_crs)
            else:
                ref_geom_proj = ref_geom

            # if ref_geom_proj.intersects(raster_geom):
            if ref_geom_proj.equals_exact(raster_geom, tolerance=1e-6):
                intersects = True
                break  # One intersection is enough, exit the loop

        if intersects:
            relative_path = os.path.relpath(tif_path, tif_folder)
            target_path = os.path.join(output_folder, relative_path)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.move(tif_path, target_path)
            moved_count += 1

    except Exception as e:
        print(f"Error ({tif_path}): {e}")

print(f"\nDone! {moved_count} files moved → {output_folder}")