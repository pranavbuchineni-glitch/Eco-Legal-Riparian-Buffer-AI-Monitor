import os
import rasterio
import numpy as np
from sklearn.cluster import KMeans

# Setup paths
project_dir = r"D:\Projects\Eco_Legal_Riparian_Buffer_AI_Monitor"
clipped_tif = os.path.join(project_dir, "bromont_buffer_nir_clipped.tif")
output_tif = os.path.join(project_dir, "bromont_buffer_classified.tif")

print("Loading NIR satellite data...")
with rasterio.open(clipped_tif) as src:
    nir_data = src.read(1)
    meta = src.meta.copy()

# Ignore empty background space
valid_mask = nir_data > 0
valid_pixels = nir_data[valid_mask].reshape(-1, 1)

print("Training K-Means AI model to classify land cover...")
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
labels = kmeans.fit_predict(valid_pixels)

# Map higher NIR reflectance to vegetation (2) and lower to soil/encroachment (1)
veg_cluster = np.argmax(kmeans.cluster_centers_.flatten())
mapped_labels = np.where(labels == veg_cluster, 2, 1)

classified_image = np.zeros_like(nir_data, dtype=np.uint8)
classified_image[valid_mask] = mapped_labels

# Save the map
meta.update(dtype=rasterio.uint8, nodata=0)
with rasterio.open(output_tif, 'w', **meta) as dst:
    dst.write(classified_image, 1)
    
print("Classification complete! Risk map saved.")