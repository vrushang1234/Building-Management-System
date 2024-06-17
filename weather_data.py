import requests
import json
import logging
import time

API_KEY = 'your_openweathermap_api_key'
CITY = 'Gainesville'
URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=imperial'

def fetch_weather_loop():
    while True:
        try:
            response = requests.get(URL)
            data = response.json()
            logging.info(json.dumps(data, indent=2))
            return data
        except requests.RequestException as e:
            logging.error(f"Error fetching weather data: {e}")
        time.sleep(600)  # Sleep for 10 minutes before retrying
