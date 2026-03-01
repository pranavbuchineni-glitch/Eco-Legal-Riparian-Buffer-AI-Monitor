import os
import geopandas as gpd

# Setup paths
project_dir = r"D:\Projects\Eco_Legal_Riparian_Buffer_AI_Monitor"
rivers_file = os.path.join(project_dir, "bromont_rivers.geojson")
output_file = os.path.join(project_dir, "bromont_riparian_buffers_5m.geojson")

print("Loading river network...")
rivers_gdf = gpd.read_file(rivers_file)

print("Projecting geometry to metric system (UTM Zone 18N)...")
rivers_metric = rivers_gdf.to_crs(epsg=32618)

print("Applying a 5m legal buffer zone...")
buffers_metric = rivers_metric.copy()
buffers_metric['geometry'] = rivers_metric.geometry.buffer(5)

buffers_metric.to_file(output_file, driver="GeoJSON")
print(f"Buffer generation complete! Saved to: {output_file}")