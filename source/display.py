#!/usr/bin/python3

from __future__ import print_function

import argparse
from papirus import Papirus
from PIL import ImageFont, ImageDraw, Image
import sys
import os
import time

from Display.PapirusDisplay import PapirusDisplay



if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        display = PapirusDisplay(filename)
