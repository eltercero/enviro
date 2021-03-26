#!/usr/bin/env python3

import time
import colorsys
import os
import sys
import ST7735
import logging
import numpy as np
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from bme280 import BME280
from enviroplus import gas
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fonts.ttf import RobotoMedium as UserFont
from datetime import datetime
from Adafruit_IO import Client, Feed

TEMPERATURE_FACTOR= 2.25
FEEDS={
    'temperature': {
        'name': 'temperature',
        'unit_type': 'temperature',
        'unit_symbol': 'ºC'
    }, 
    'humidity': {
        'name': 'humidity',
        'unit_type': 'humidity',
        'unit_symbol': '%'
    }, 
    'oxidising': {
        'name': 'oxidising',
        'unit_type': 'gas',
        'unit_symbol': 'kO'
    },
    'reducing': {
        'name': 'reducing',
        'unit_type': 'gas',
        'unit_symbol': 'kO'
    },
    'nh3': {
        'name': 'nh3',
        'unit_type': 'gas',
        'unit_symbol': 'kO'
    }
}

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()

# Loggin basic configuration
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp

# Starting values
global_cpu_temps = [get_cpu_temperature()] * 5
last_recorded_minute = 0
aio = Client(os.environ['IO_USERNAME'], os.environ['IO_KEY'])

def setup_io_feeds():
    existing_feeds = aio.feeds()
    existing_feeds_keys = list(map(lambda feed: feed.key, existing_feeds))

    for feed_name, feed_values in FEEDS.items():
        if feed_name not in existing_feeds_keys:
            feed = Feed(name=feed_values['name'], key=feed_values['name'], unit_symbol=feed_values['unit_symbol'],unit_type=feed_values['unit_type'])
            aio.create_feed(feed)

def get_current_temperature():
    cpu_temp = get_cpu_temperature()
    cpu_temps = global_cpu_temps[1:] + [cpu_temp]
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
    raw_temp = bme280.get_temperature()
    comp_temp = raw_temp - ((avg_cpu_temp - raw_temp) / TEMPERATURE_FACTOR)
    return comp_temp

def feed_io(key, value):
    logging.info("> Sending –– {} –– values to adafruit io {:05.2f} *C".format(key, value))
    aio.send_data(key, value)

setup_io_feeds()

temperature_array = []
humidity_array = []
oxidising_array = []
reducing_array = []
nh3_array = []

try:
    while True:
        gas_data = gas.read_all()

        temperature_array.append(get_current_temperature())
        humidity_array.append(bme280.get_humidity())
        oxidising_array.append(gas_data.oxidising/1000)
        reducing_array.append(gas_data.reducing/1000)
        nh3_array.append(gas_data.nh3/1000)

        if last_recorded_minute != datetime.now().time().minute:
            last_recorded_minute = datetime.now().time().minute


            current_values = {
                "temperature": np.mean(temperature_array),
                "humidity": np.mean(humidity_array) ,
                "oxidising": np.mean(oxidising_array) ,
                "reducing": np.mean(reducing_array) ,
                "nh3": np.mean(nh3_array) 
            }

            temperature_array = []
            humidity_array = []
            oxidising_array = []
            reducing_array = []
            nh3_array = []

            for key, value in current_values.items():
                feed_io(key, value)
# Exit cleanly
except KeyboardInterrupt:
    sys.exit(0)
