import adafruit_dht
import time
import logging

dht_sensor = None  # This will be set in main.py

def read_sensor_data():
    try:
        humidity = dht_sensor.humidity
        temperature = dht_sensor.temperature
        if humidity is not None and temperature is not None:
            logging.info(f"Humidity: {humidity:.2f}% Temp: {temperature:.2f}C")
        else:
            logging.warning("Failed to retrieve data from humidity sensor")
    except RuntimeError as error:
        logging.error(f"Error reading from DHT sensor: {error}")
        time.sleep(2.0)

def read_humidity_from_dht():
    humidity = None
    try:
        humidity = dht_sensor.humidity
    except RuntimeError as error:
        logging.error(f"Error reading from DHT sensor: {error}")
        time.sleep(2.0)
    return humidity
