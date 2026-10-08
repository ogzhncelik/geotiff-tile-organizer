# geotiff-tile-organizer

Scripts for sorting large collections of GeoTIFF tiles into folders based on where they are or what they are named.
Useful for separating sea/land/boundary tiles, removing cloudy scenes or matching tiles to a reference set before building a dataset.
Each script is standalone: set the paths at the top and run it. Matching tiles are moved, and subfolder structure is preserved where applicable.

## Scripts

| Script | What it does |
|---|---|
| `geotiff_classify_by_shp_corners.py` | Checks the four corners of each tile against a shapefile. Tiles fully inside go to one folder, partially inside (boundary) tiles go to another. Runs in parallel. |
| `geotiff_filter_by_shp_intersection.py` | Moves every tile whose extent intersects any polygon in a shapefile (e.g. sea, island or cloud masks). Reprojects the shapefile automatically if needed. |
| `geotiff_filter_by_reference_extent.py` | Moves tiles whose extent exactly matches a tile in a reference folder. Handles different CRS between the two sets. |
| `geotiff_filter_by_filename_prefix.py` | Moves tiles whose file name starts with one of a given set of IDs (e.g. scene numbers of cloudy images). |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python geotiff_filter_by_shp_intersection.py
```

Edit the input/output paths at the top of each script before running it.

## License

MIT
