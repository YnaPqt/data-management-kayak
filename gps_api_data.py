import os
import time
import json
import requests

# List of cities to search for
destinations = [
    "Mont Saint Michel", "St Malo", "Bayeux", "Le Havre", "Rouen", "Paris", "Amiens", "Lille", "Strasbourg", 
    "Chateau du Haut Koenigsbourg", "Colmar", "Eguisheim", "Besancon", "Dijon", "Annecy", "Grenoble", "Lyon", 
    "Gorges du Verdon", "Bormes les Mimosas", "Cassis", "Marseille", "Aix en Provence", "Avignon", "Uzes", 
    "Nimes", "Aigues Mortes", "Saintes Maries de la mer", "Collioure", "Carcassonne", "Ariege", "Toulouse", 
    "Montauban", "Biarritz", "Bayonne", "La Rochelle"
]

# API Endpoint
API_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "MyPythonApp/1.0"}  # Required to avoid being blocked

# Output file path
output_folder = "src"
output_file = os.path.join(output_folder, "gps_data.json")

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# If the file exists, remove it
if os.path.exists(output_file):
    os.remove(output_file)

# Data storage
city_data = []
api_count = 0
# Iterate over cities
for city in destinations:
    params = {"q": city, "format": "json", "limit": 1}
    try:
        response = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data:
            city_info = {
                "city": city,
                "lat": data[0]["lat"],
                "lon": data[0]["lon"]
            }
        else:
            city_info = {"city": city, "lat": None, "lon": None}
        
        city_data.append(city_info)
        print(f"Success: Retrieved data for {city}")
    except requests.RequestException as e:
        print(f"Error fetching data for {city}: {e}")
        city_data.append({"city": city, "lat": None, "lon": None})

    api_count += 1 
    time.sleep(1)  # Delay to prevent rate limiting

# Save to JSON file
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(city_data, file, indent=4)

print(f"Data saved to {output_file}")
print(f"\nTotal API calls :{api_count}")
