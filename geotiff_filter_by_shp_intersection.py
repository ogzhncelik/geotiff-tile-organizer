"""
This Python script checks the spatial intersection between a given shapefile (vector data) and raster images (TIF files),
and moves the raster images that intersect the geometries in the shapefile
to another folder.

🎯 Purpose:
- Detect TIF files that overlap with a specific vector area (e.g. sea or island geometries)
- Move these TIF files to the specified target folder without breaking the subfolder structure

📥 Input:
- `shapefile_path`: Vector data used for the intersection check (e.g. sea/island geometries in `.shp` format)
- `tif_folder`: Main folder containing the TIF raster files to be checked (including subfolders)
- The intersection with the geometries is checked using the geographic bounds of the raster files (`src.bounds`)

📤 Output:
- `output_folder`: Target folder where the TIF files that intersect the shapefile will be moved
- The subfolder structure is preserved using `os.path.relpath`

🔧 Processing:
1. The shapefile is read with `geopandas`.
2. All `.tif` files under `tif_folder` are listed with `os.walk`.
3. The geographic bounds (`bounds`) of each TIF file are read with `rasterio` and a polygon is created with `shapely.geometry.box`.
4. The CRS (coordinate reference system) of the raster file is compared with the shapefile CRS; if different, the shapefile is reprojected.
5. If the raster geometry intersects any polygon in the shapefile:
   - The file is moved (`shutil.move`) to the target folder, preserving the same subpath (`os.makedirs`).
6. Errors are caught and printed on screen.
7. The processing status (progress bar) is shown to the user with `tqdm`.

"""


import os
import shutil
import geopandas as gpd
import rasterio
from shapely.geometry import box
from tqdm import tqdm

# File paths
shapefile_path = r"path\to\shapefile.shp"
tif_folder = r"path\to\input"
output_folder = r"path\to\output"

# Create the main output folder (for the files to be removed)
os.makedirs(output_folder, exist_ok=True)

# Read the shapefile
gdf = gpd.read_file(shapefile_path)

# Go through all subfolders
tif_paths = []
for root, dirs, files in os.walk(tif_folder):
    for file in files:
        if file.lower().endswith(".tif"):
            tif_paths.append(os.path.join(root, file))

# Start the progress bar with tqdm
for tif_path in tqdm(tif_paths, desc="Checking TIF Files"):
    try:
        with rasterio.open(tif_path) as src:
            bounds = src.bounds
            raster_geom = box(bounds.left, bounds.bottom, bounds.right, bounds.top)

            raster_crs = src.crs
            if gdf.crs != raster_crs:
                gdf_proj = gdf.to_crs(raster_crs)
            else:
                gdf_proj = gdf

            intersects = any(cloud_geom.intersects(raster_geom) for cloud_geom in gdf_proj.geometry)

        if intersects:
            # Calculate the relative path to preserve the subfolder structure
            relative_path = os.path.relpath(tif_path, tif_folder)
            target_path = os.path.join(output_folder, relative_path)

            # Create the target folder
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            # Move the file
            shutil.move(tif_path, target_path)

    except Exception as e:
        print(f"Error ({tif_path}): {e}")