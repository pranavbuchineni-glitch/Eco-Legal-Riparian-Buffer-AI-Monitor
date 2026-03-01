import os
import sqlite3
import rasterio
from rasterio.features import shapes
import geopandas as gpd

# Setup paths
project_dir = r"D:\Projects\Eco_Legal_Riparian_Buffer_AI_Monitor"
classified_tif = os.path.join(project_dir, "bromont_buffer_classified.tif")
db_path = os.path.join(project_dir, "environmental_violations.db")

print("Initializing SQL Database...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS riparian_encroachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        detection_date TEXT, latitude REAL, longitude REAL, area_sq_meters REAL, status TEXT
    )
''')
conn.commit()

print("Extracting encroachment zones...")
with rasterio.open(classified_tif) as src:
    image = src.read(1)
    
    # Target only the red pixels (value = 1)
    mask = image == 1
    results = ({'properties': {'raster_val': v}, 'geometry': s} for i, (s, v) in enumerate(shapes(image, mask=mask, transform=src.transform)))
    geoms = list(results)
    
    if geoms:
        gdf = gpd.GeoDataFrame.from_features(geoms, crs=src.crs)
        gdf['area_sqm'] = gdf.geometry.area
        
        # Filter out tiny artifacts (< 50 sq meters)
        gdf_filtered = gdf[gdf['area_sqm'] > 50].copy()
        gdf_gps = gdf_filtered.to_crs(epsg=4326)
        
        for index, row in gdf_gps.iterrows():
            centroid = row.geometry.centroid
            cursor.execute('''
                INSERT INTO riparian_encroachments (detection_date, latitude, longitude, area_sq_meters, status)
                VALUES (?, ?, ?, ?, ?)
            ''', ("2023-08-28", centroid.y, centroid.x, round(row['area_sqm'], 2), "Pending Review"))
        conn.commit()

conn.close()
print("Success! Structured data logged to SQL database.")