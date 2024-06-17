import RPi.GPIO as GPIO
import time
import threading
import board
import adafruit_dht
from lcd_display import lcd_init, lcd_update_task
from sensor_data import read_sensor_data, read_humidity_from_dht
from weather_data import fetch_weather_loop
from button_handling import button_thread_func
from pir_sensor import pir_sensor_thread
from fire_simulation import fire_sim_thread

AC = 20
HEAT = 16
LED_1 = 11
LED_2 = 9
LED_3 = 10

def main():
    try:
        # Initialize GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LCD_E, GPIO.OUT)
        GPIO.setup(LCD_RS, GPIO.OUT)
        GPIO.setup(LCD_D4, GPIO.OUT)
        GPIO.setup(LCD_D5, GPIO.OUT)
        GPIO.setup(LCD_D6, GPIO.OUT)
        GPIO.setup(LCD_D7, GPIO.OUT)

        GPIO.setup(AC, GPIO.OUT)
        GPIO.setup(HEAT, GPIO.OUT)

        # Setup new LED pins
        GPIO.setup(LED_1, GPIO.OUT)
        GPIO.setup(LED_2, GPIO.OUT)
        GPIO.setup(LED_3, GPIO.OUT)

        lcd_init()

        global dht_sensor
        dht_pin = board.D4
        dht_sensor = adafruit_dht.DHT11(dht_pin)

        # To be used when simulating fire
        # fire_thread = threading.Thread(target = fire_sim_thread)
        # fire_thread.start()

        lcd_thread = threading.Thread(target=lcd_update_task)
        lcd_thread.start()

        button_thread = threading.Thread(target=button_thread_func)
        button_thread.start()

        pir_thread = threading.Thread(target=pir_sensor_thread)
        pir_thread.start()

        while True:
            time.sleep(2)
    finally:
        GPIO.cleanup()
        dht_sensor.exit()

if __name__ == "__main__":
    main()
