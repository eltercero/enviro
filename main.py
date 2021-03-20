#!/usr/bin/env python3

import time
import colorsys
import os
import sys
import ST7735
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from bme280 import BME280
from enviroplus import gas
from subprocess import PIPE, Popen
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fonts.ttf import RobotoMedium as UserFont
from datetime import datetime
import logging

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()

def log_data(info):
    logging.info("""Logging something""")

try:
    while True:
        if datetime.now().time().second%10 == 0:
            logging.info("""Do something""")

# Exit cleanly
except KeyboardInterrupt:
    sys.exit(0)
