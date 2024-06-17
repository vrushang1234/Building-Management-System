import RPi.GPIO as GPIO
import time
import logging

PIR_PIN = 27
door_status = "C"  # C for Closed, O for Open

def pir_sensor_thread():
    global door_status

    GPIO.setup(PIR_PIN, GPIO.IN)
    logging.info("PIR Sensor initialized")

    while True:
        if GPIO.input(PIR_PIN):
            logging.info("PIR Sensor detected motion!")
            door_status = "O"
        else:
            door_status = "C"
        time.sleep(0.1)
