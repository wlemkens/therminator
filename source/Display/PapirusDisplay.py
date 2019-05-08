from __future__ import print_function

import argparse
from papirus import Papirus
from PIL import ImageFont, ImageDraw, Image
import sys
import os
import time

WHITE = 1
BLACK = 0


class PapirusDisplay(object):
    def __init__(self, config):
        self.fontPath = "/usr/local/share/fonts/Righteous-Regular.ttf"
        self.my_papirus = Papirus()
        self.setup, self.mqtt = self.loadConfig(config)
        self.
        self.draw()


    def loadConfig(self, config):
        setup = None
        mqtt = None
        with open(filename) as f:
            config = json.load(f)
        mqttConfig = config["mqtt"]["configFile"]
        setupConfig = config["setup"]["configFile"]
        with open(setupConfig) as f2:
            setup = Setup(json.load(f2))
        with open(setupConfig) as f2:
            mqtt = json.load(f2)
        return setup, mqtt


    def draw(self):
        # initially set all white background
        image = Image.new('1', self.my_papirus.size, WHITE)

        # prepare for drawing
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(self.fontPath, 12)
        printstring = "TEST2"
        draw.text((10, 40), printstring, font=font, fill=BLACK)

        self.my_papirus.display(image)
        partial = True
        if partial:
            self.my_papirus.partial_update()
        else:
            self.my_papirus.update()
