import RPi.GPIO as GPIO
import time
import logging

button_incr = 21
button_decr = 20
BUTTON_HOLD_TIME = 2
desired_temp = 69

def button_thread_func():
    while True:
        if GPIO.input(button_incr) == GPIO.LOW:
            handle_button_press(button_incr, True)
        if GPIO.input(button_decr) == GPIO.LOW:
            handle_button_press(button_decr, False)
        time.sleep(0.1)

def handle_button_press(button, increment):
    global desired_temp
    start_time = time.time()
    while GPIO.input(button) == GPIO.LOW:
        time.sleep(0.1)
    press_duration = time.time() - start_time

    if press_duration >= BUTTON_HOLD_TIME:
        change_amount = 5
    else:
        change_amount = 1

    if increment:
        desired_temp += change_amount
        logging.info(f"Increased temperature by {change_amount} to {desired_temp}")
    else:
        desired_temp -= change_amount
        logging.info(f"Decreased temperature by {change_amount} to {desired_temp}")
