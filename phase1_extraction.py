import os
import requests
import osmnx as ox
from tqdm import tqdm

# 1. Set up your workspace paths
project_dir = r"D:\Projects\Eco_Legal_Riparian_Buffer_AI_Monitor"
os.makedirs(project_dir, exist_ok=True)

# 2. Extract OpenStreetMap River Data
print("Fetching Bromont river network from OpenStreetMap...")
rivers = ox.features_from_place("Bromont, Quebec, Canada", tags={"waterway": True})
rivers_file = os.path.join(project_dir, "bromont_rivers.geojson")
rivers.to_file(rivers_file, driver="GeoJSON")
print(f"River network saved to: {rivers_file}\n")

# ==========================================
# SATELLITE IMAGERY ACQUISITION (COPERNICUS)
# ==========================================

# NOTE FOR GITHUB: Never hardcode real passwords here! 
USERNAME = "YOUR_COPERNICUS_EMAIL@EXAMPLE.COM" 
PASSWORD = "YOUR_COPERNICUS_PASSWORD"          

product_name = "S2B_MSIL2A_20230828T154819_N0510_R054_T18TXR_20241025T202724"

# 3. Look up the internal UUID for the download server
print(f"Looking up internal UUID for {product_name}...")
odata_search_url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter=Name eq '{product_name}'"
search_response = requests.get(odata_search_url).json()

# Proceed only if we have valid API credentials inserted
if USERNAME != "YOUR_COPERNICUS_EMAIL@EXAMPLE.COM":
    product_uuid = search_response['value'][0]['Id']
    print(f"Found UUID: {product_uuid}")

    # 4. Authenticate to get an Access Token
    print("Authenticating with Copernicus API...")
    auth_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    data = {
        "client_id": "cdse-public",
        "username": USERNAME,
        "password": PASSWORD,
        "grant_type": "password",
    }

    response = requests.post(auth_url, data=data)
    response.raise_for_status()
    access_token = response.json()["access_token"]
    
    # 5. Download the Satellite Image (Handling Redirects)
    download_url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({product_uuid})/$value"
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {access_token}"})

    print(f"Starting satellite image download...")
    response = session.get(download_url, stream=True, allow_redirects=False)
    while response.is_redirect:
        redirect_url = response.headers["Location"]
        response = session.get(redirect_url, stream=True, allow_redirects=False)
    response.raise_for_status() 

    # 6. Save the file locally with a progress bar
    file_path = os.path.join(project_dir, f"{product_name}.zip")
    total_size = int(response.headers.get('content-length', 0))

    with open(file_path, "wb") as file, tqdm(
        desc="Downloading Sentinel-2 Image",
        total=total_size, unit='iB', unit_scale=True, unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    print(f"\nDownload complete! File saved to: {file_path}")
else:
    print("Skipping download: Please insert valid Copernicus credentials to run this section.")
