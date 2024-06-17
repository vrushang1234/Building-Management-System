import RPi.GPIO as GPIO
import time
import threading
from datetime import datetime
from sensor_data import read_sensor_data, read_humidity_from_dht
from weather_data import fetch_weather_loop

# LCD pin mappings
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18

# Constants for LCD commands
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
LCD_CLEAR = 0x01

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Lock for LCD access
lcd_lock = threading.Lock()

# Global variables for desired temperature and weather index
desired_temp = 69
weather_index = 69
led_status = "OFF"
prev_unit = None
prev_door_status = "C"
door_status = prev_door_status

def lcd_init():
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(LCD_CLEAR, LCD_CMD)
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    GPIO.output(LCD_RS, mode)

    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x10 == 0x10:
        GPIO.output(LCD_D4, True)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_D5, True)
    if bits & 0x40 == 0x40:
        GPIO.output(LCD_D6, True)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_D7, True)

    lcd_toggle_enable()
    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x01 == 0x01:
        GPIO.output(LCD_D4, True)
    if bits & 0x02 == 0x02:
        GPIO.output(LCD_D5, True)
    if bits & 0x04 == 0x04:
        GPIO.output(LCD_D6, True)
    if bits & 0x08 == 0x08:
        GPIO.output(LCD_D7, True)
    lcd_toggle_enable()

def lcd_toggle_enable():
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

def update_lcd(desired_temp, weather_index, led_status, door_status):
    global prev_unit, prev_door_status

    with lcd_lock:
        curr_unit = None

        # Check if weather index is above 95 for special alert
        if weather_index > 95:
            lcd_string("FIRE ALERT!!!", LCD_LINE_1)
            lcd_string("EVACUATE", LCD_LINE_2)
            GPIO.output(LED_PIN, GPIO.HIGH)
            GPIO.output(AC, GPIO.HIGH)
            GPIO.output(HEAT, GPIO.HIGH)
            time.sleep(0.3)
            GPIO.output(LED_PIN, GPIO.LOW)
            GPIO.output(AC, GPIO.LOW)
            GPIO.output(HEAT, GPIO.LOW)
            return

        if door_status == "C":
            if weather_index and weather_index - desired_temp > 3:
                curr_unit = "AC"
                GPIO.output(AC, GPIO.HIGH)
                GPIO.output(HEAT, GPIO.LOW)
            elif weather_index and desired_temp - weather_index > 3:
                curr_unit = "HEAT"
                GPIO.output(HEAT, GPIO.HIGH)
                GPIO.output(AC, GPIO.LOW)
            else:
                curr_unit = None
                GPIO.output(HEAT, GPIO.LOW)
                GPIO.output(AC, GPIO.LOW)

            if prev_unit != curr_unit:
                if curr_unit is not None:
                    lcd_string("Heater is on" if curr_unit == "HEAT" else "AC is on", LCD_LINE_1)
                    lcd_string(" " * 16, LCD_LINE_2)  # Clear second line
                else:
                    if prev_unit == "HEAT":
                        lcd_string("Heater is off", LCD_LINE_1)
                    elif prev_unit == "AC":
                        lcd_string("AC is off", LCD_LINE_1)
                    else:
                        lcd_string("Both units are off", LCD_LINE_1)
                    lcd_string(" " * 16, LCD_LINE_2)  # Clear second line

                time.sleep(3)
                prev_unit = curr_unit

        if prev_door_status != door_status:
            if door_status == 'O':
                if prev_unit == 'AC':
                    GPIO.output(AC, GPIO.LOW)
                elif prev_unit == 'HEAT':
                    GPIO.output(HEAT, GPIO.LOW)
            else:
                if prev_unit == 'AC':
                    GPIO.output(AC, GPIO.HIGH)
                elif prev_unit == 'HEAT':
                    GPIO.output(HEAT, GPIO.HIGH)
            lcd_string(f"Door is {'open' if door_status == 'O' else 'closed'}", LCD_LINE_1)
            lcd_string(f"{prev_unit if prev_unit else 'HVAC'} {'OFF' if door_status == 'O' else 'ON'}", LCD_LINE_2)
            time.sleep(3)
            prev_door_status = door_status

        unit_status = f"H:{curr_unit if curr_unit else 'OFF'}"
        led_status_str = f"L:{led_status}".rjust(LCD_WIDTH)
        lcd_string(unit_status + led_status_str[-(LCD_WIDTH - len(unit_status)):], LCD_LINE_2)

        door_str = f"Dr:{door_status}"
        temp_str = f"{desired_temp}/{weather_index} {datetime.now().strftime('%H:%M')} {door_str}"
        lcd_string(temp_str, LCD_LINE_1)

        led_status = "OFF"
        time.sleep(0.5)

def lcd_update_task():
    global desired_temp, weather_index, led_status, door_status

    while True:
        weather_data = fetch_weather_loop()
        if weather_data:
            weather_index = weather_data["main"]["temp"]
            led_status = "ON"

        read_sensor_data()
        humidity = read_humidity_from_dht()

        update_lcd(desired_temp, weather_index, led_status, door_status)
