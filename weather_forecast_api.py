import requests
import json
import os
import pandas as pd
from dotenv import load_dotenv

# Load API key 
load_dotenv()

#Open weather api key
API_KEY = os.environ.get('OPENWEATHER_API_KEY')


# Assigning variables to existing coordinates file and to the future weather file.
GPS_DATA_FILE, WEATHER_JSON_FILE = "src/gps_data.json", "src/weather_data.json"
BASE_URL = "https://api.openweathermap.org/data/3.0/onecall/"

# Reads gps file and json load parses json content into list of dictionaries
with open(GPS_DATA_FILE, "r") as gps_file:
    cities = json.load(gps_file)

weather_data = []
api_count =0
# Looping through each city and make API calls and appends weather_data[]
for city in cities:
    response = requests.get(
        f"https://api.openweathermap.org/data/3.0/onecall?lat={city['lat']}&lon={city['lon']}&&exclude=current,minutely,hourly&appid={API_KEY}&units=metric")

    
    days = response.json()['daily']
    for i, day in enumerate(days[1:8]):
            
        timestamp = day['dt']
        temp_day = day['temp']['day']
        summary = day['summary']
        num_day = i + 1
        humidity =day ['humidity']
        dew_point =day ['dew_point']
        weather_main = day['weather'][0]['main']
        weather_descrip = day['weather'][0]['description']
        clouds =day['clouds']
        wind_speed = day['wind_speed']
        pop = day['pop']
    
        weather_data.append([
                num_day,timestamp,city['city'],city['lat'],city['lon'],temp_day,humidity,dew_point,
                weather_main,weather_descrip,clouds,wind_speed,pop])
            
    if response.status_code == 200:
        print(f"Succes fetched data for {city["city"]} (Status Code: {response.status_code})")
        api_count += 1

os.makedirs("src", exist_ok=True)

#Writes json file and converts weather_data[] to json file.
with open(WEATHER_JSON_FILE, "w") as json_file:
    json.dump(weather_data, json_file, indent=4)

print("Weather data successfully fetched and saved as JSON.")
print(f'\n Total API calls:{api_count}')   

