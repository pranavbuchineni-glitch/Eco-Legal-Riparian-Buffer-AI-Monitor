import os
import osmnx as ox

# Setup workspace
project_dir = r"D:\Projects\Eco_Legal_Riparian_Buffer_AI_Monitor"
os.makedirs(project_dir, exist_ok=True)

# Extract OpenStreetMap River Data
print("Fetching Bromont river network from OpenStreetMap...")
rivers = ox.features_from_place("Bromont, Quebec, Canada", tags={"waterway": True})

# Save the geometry
output_file = os.path.join(project_dir, "bromont_rivers.geojson")
rivers.to_file(output_file, driver="GeoJSON")
print(f"Success! River network saved to: {output_file}")