#!/usr/bin/python3

from __future__ import print_function

import argparse
from PIL import ImageFont, ImageDraw, Image
import sys
import os
import time

from Display.WaveshareDisplay import WaveshareDisplay
#from Display.PapirusDisplay import PapirusDisplay
#from Display.PapirusTechnicalDisplay import PapirusTechnicalDisplay



if __name__ == "__main__":
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
        log = None
        if len(sys.argv) >= 3:
            log = sys.argv[2]
        display = WaveshareDisplay(filename, log)
#        display = PapirusDisplay(filename, log)
#        display = PapirusTechnicalDisplay(filename, log)
