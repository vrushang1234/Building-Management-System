import RPi.GPIO as GPIO
import time

LED_PIN = 22

def fire_sim_thread():
    GPIO.setup(LED_PIN, GPIO.OUT)
    while True:
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(0.3)
