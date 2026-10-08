"""
This Python script compares the `.tif` raster files in a given folder against a shapefile (SHP) geometry
and automatically sorts them into three categories based on their geographic location:
- Files completely inside the shapefile geometry → moved to the `deniz_folder` folder
- Files partially inside (intersecting) → moved to the `boundary_folder` folder
- Files with no intersection → left where they are

🎯 Purpose:
- Identify and classify `.tif` images that geographically overlap with the SHP file
- Move the images to the appropriate target folders based on how much they are contained

📥 Inputs:
- `shp_path`: The first `.shp` file found in the folder
- `tif_folder`: Folder containing the `.tif` raster files to be checked geographically

📤 Outputs:
- `.tif` files completely inside the shapefile → moved to the `deniz_folder` folder
- `.tif` files that only partially intersect the shapefile → moved to the `boundary_folder` folder
- Other `.tif` files stay where they are

🔁 Processing Steps:
1. The SHP file is read and converted to the CRS of the raster files.
2. For each `.tif` file:
   - The bounding box (corner points) is calculated
   - The geographic intersection of these points with the SHP geometry is tested
   - If all 4 corners are inside the shapefile → moved to the `deniz_folder` folder
   - If at least one corner is inside the shapefile → moved to the `boundary_folder` folder
   - If none are inside → the file stays where it is
3. Processing is parallelized with `multiprocessing.Pool` for speed.
4. A progress bar is shown on screen with `tqdm`.

"""


import os
import shutil
import rasterio
import geopandas as gpd
from shapely.geometry import box, Point
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import re

# Folder paths
shp_path = r"path\to\shp"
tif_folder = r"path\to\input"
deniz_folder = r"path\to\output\inside"
boundary_folder = r"path\to\output\boundary"

os.makedirs(deniz_folder, exist_ok=True)
os.makedirs(boundary_folder, exist_ok=True)

# Read the SHP file
shp_files = [f for f in os.listdir(shp_path) if f.endswith(".shp")]
if not shp_files:
    raise FileNotFoundError("SHP file not found.")
shapefile_path = os.path.join(shp_path, shp_files[0])
shapefile = gpd.read_file(shapefile_path)


def process_tif(tif_file):
    tif_path = os.path.join(tif_folder, tif_file)
    try:
        with rasterio.open(tif_path) as src:
            bounds = src.bounds
            tif_crs = src.crs
            tif_geom = box(*bounds)

        # Convert the SHP file to the CRS of the tif
        shp_in_tif_crs = shapefile.to_crs(tif_crs)

        # Test the corner points
        corners = [
            Point(bounds.left, bounds.top),
            Point(bounds.right, bounds.top),
            Point(bounds.right, bounds.bottom),
            Point(bounds.left, bounds.bottom)
        ]

        inside_flags = [shp_in_tif_crs.contains(pt).any() for pt in corners]
        inside_count = sum(inside_flags)

        if inside_count == 4:
            shutil.move(tif_path, os.path.join(deniz_folder, tif_file))
        elif inside_count > 0:
            shutil.move(tif_path, os.path.join(boundary_folder, tif_file))


    except Exception as e:
        pass

# Process all tif files

if __name__ == "__main__":
    # Filtered .tif files — by extension only
    tif_files = [
        f for f in os.listdir(tif_folder)
        if f.endswith(".tif")
    ]

    with Pool(processes=max(1, cpu_count() // 3)) as pool:
        list(tqdm(pool.imap_unordered(process_tif, tif_files), total=len(tif_files), desc="Processing TIF files"))

    print("Processing completed.")