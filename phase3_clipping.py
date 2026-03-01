import os
import zipfile
import geopandas as gpd
import rasterio
from rasterio.mask import mask

# Setup paths
project_dir = r"D:\Projects\Eco_Legal_Riparian_Buffer_AI_Monitor"
zip_filename = "S2A_MSIL2A_20230823T154821_N0510_R054_T18TXR_20241025T054611.SAFE.zip"
zip_path = os.path.join(project_dir, zip_filename)
buffer_file = os.path.join(project_dir, "bromont_riparian_buffers_5m.geojson")
output_tif = os.path.join(project_dir, "bromont_buffer_nir_clipped.tif")

print("Loading legal buffer polygons...")
buffers = gpd.read_file(buffer_file)

print("Scanning Sentinel-2 ZIP archive for Near-Infrared data...")
b8_path = None
with zipfile.ZipFile(zip_path, 'r') as z:
    for file in z.namelist():
        if "R10m" in file and file.endswith("B08_10m.jp2"):
            # Format VSI path for Windows
            safe_zip_path = zip_path.replace(os.sep, '/')
            b8_path = f"/vsizip/{safe_zip_path}/{file}"
            break

if b8_path:
    with rasterio.open(b8_path) as src:
        print("Clipping satellite imagery...")
        buffers = buffers.to_crs(src.crs)
        geometries = [feature["geometry"] for _, feature in buffers.iterrows()]
        
        out_image, out_transform = mask(src, geometries, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({"driver": "GTiff", "height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform})

        with rasterio.open(output_tif, "w", **out_meta) as dest:
            dest.write(out_image)
    print("Success! Clipped satellite data saved.")
else:
    print("Error: Could not locate Band 8 in the ZIP file.")