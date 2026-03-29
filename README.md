# EECS 113 - Project 5: Building Management System

## Overview

A Raspberry Pi-based Building Management System that integrates multiple sensors and components to monitor and control environmental conditions. The system displays real-time data on a 16x2 LCD including temperature, HVAC status, door status, motion-detected lighting status, and current time.

![Picture of the Circuit](https://github.com/vrushang1234/Building-Management-System/blob/main/circuit-picture.png)

## Features

- **Temperature-controlled HVAC** - Automatically switches AC or Heater on/off based on the difference between desired and ambient temperature (threshold: difference of 3°F)
- **Fire alarm system** - Triggers a flashing LED alert and "FIRE ALERT / EVACUATE" message on LCD when weather index exceeds 95
- **Motion-based lighting** - PIR sensor turns on a light LED when motion is detected; auto-off after 10 seconds of no motion
- **Password-protected door** - 3-bit binary password entered via LEDs/buttons; password changes daily based on the day of the week (Monday=1, Tuesday=2, etc.)
- **Real-time clock display** - Current time shown on LCD, updated every 5 seconds
- **Event logging** - All state changes (temperature adjustments, door events, motion) are written to `log.txt` with timestamps

## Hardware Components

| Component | Description |
|-----------|-------------|
| Raspberry Pi | Main controller |
| 1602A LCD (16-pin) | Displays system status; contrast via potentiometer |
| DHT11 Sensor | Reads ambient temperature and humidity (GPIO D4) |
| PIR Motion Sensor | Detects room occupancy (GPIO 21) |
| 3x LEDs (password) | Represent binary password bits (GPIO 11, 9, 10) |
| 1x LED (motion/fire) | Lights LED controlled by PIR / fire alert (GPIO 26) |
| 2x Relay outputs | Control AC unit (GPIO 20) and Heater (GPIO 16) |
| 6x Push buttons | Temp up/down, door toggle, and 3 LED password buttons |

## GPIO Pin Mapping

```
LCD:     RS=7, E=8, D4=25, D5=24, D6=23, D7=18
Buttons: INC=17, DEC=27, DOOR=14
         LED1=19, LED2=13, LED3=6
LEDs:    LED1=11, LED2=9, LED3=10
AC:      GPIO 20
HEAT:    GPIO 16
PIR:     GPIO 21
PIR LED: GPIO 26
```

## Software Dependencies

```
RPi.GPIO
adafruit-circuitpython-dht
aiohttp
requests
```

Install with:
```bash
pip install RPi.GPIO adafruit-circuitpython-dht aiohttp requests
```

## How It Works

### Weather Index Calculation

Humidity is fetched from the [CIMIS API](http://et.water.ca.gov/api/data) (station 75, Irvine). If the API call fails or times out, the DHT11 sensor's humidity reading is used as a fallback. The weather index is computed as:

```
weather_index = temperature_f + 0.05 * humidity
```

This index is compared against the desired temperature to control the HVAC system.

### HVAC Control Logic

| Condition | Action |
|-----------|--------|
| `weather_index - desired_temp > 3` | AC turns ON |
| `desired_temp - weather_index > 3` | Heater turns ON |
| Within ±3° range | Both units OFF |
| Door is open | HVAC turns OFF |
| `weather_index > 95` | Fire alert — all units OFF, LED strobes |

### Password-Protected Door

Three buttons toggle three LEDs that represent bits of a 3-bit binary number. The decimal value of this binary number must match the current day of the week (1=Monday … 7=Sunday). Pressing the door button:
- If correct: door opens
- If incorrect: LCD shows "INCORRECT PASSWORD!!" for 3 seconds and logs the attempt

### Threading Model

The system runs three concurrent threads:
1. **`lcd_update_task`** - Fetches weather data via async loop and updates the LCD every 5 seconds
2. **`button_thread_func`** - Handles all button GPIO interrupts with 200ms debounce
3. **`pir_sensor_thread`** - Polls PIR sensor every second and manages motion LED

## Running the System

```bash
python3 EECS113Project5.py
```

The script must be run on a Raspberry Pi with all components wired as described above. Press `Ctrl+C` to exit; GPIO and DHT sensor are cleaned up automatically.

## Log File

All events are appended to `log.txt` in the working directory with timestamps:

```
2025-01-15 23:14:02: Desired Temperature increased to 70
2025-01-15 23:15:44: Motion detected (PIR LED ON)
2025-01-15 23:16:01: Door opened
```
