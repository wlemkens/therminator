from __future__ import print_function

import argparse
from papirus import Papirus
from PIL import ImageFont, ImageDraw, Image
import sys
import os
import time

import json
import paho.mqtt.client as mqtt

from Entity.Zone import Zone

WHITE = 1
BLACK = 0


class PapirusDisplay(object):
    def __init__(self, config):
        self.zones = []
        self.fontPath = "/usr/local/share/fonts/Righteous-Regular.ttf"
        self.my_papirus = Papirus()
        self.setup, self.mqtt = self.loadConfig(config)
        self.createLayout(self.setup, self.mqtt)
        self.client = mqtt.Client()
        self.client.connect(self.mqtt["address"], self.mqtt["port"], 60)
        self.client.loop_forever()


    def getFontSize(self, area, printstring):
        # returns (ideal fontsize, (length of text, height of text)) that maximally
        # fills a papirus object for a given string
        fontsize = 0
        stringlength = 0
        stringwidth = 0

        maxLength = area[1]
        maxHeight = area[0]

        while (stringlength <= maxLength and stringwidth <= maxHeight):

            fontsize += 1
            font = ImageFont.truetype(self.fontPath, fontsize)
            size = font.getsize(printstring)
            stringlength = size[0]
            stringwidth = size[1]

        #font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', fontsize-1)
        font = ImageFont.truetype(self.fontPath, fontsize-1)
        return fontsize-1, font.getsize(printstring)

    def updateZone(self, zone, index, draw):
        lineHeight = 1.0 * self.my_papirus.height / len(self.zones)
        lineWidth = self.my_papirus.width / 3
        text = "{:}: {:}/{:}".format(zone.getName(), zone.getTemperature(), zone.getSetpoint())
        fontSize = self.getFontSize([lineWidth, lineHeight], text)
        font = ImageFont.truetype(self.fontPath, 12)
        draw.text((lineWidth  , lineHeight * (index )), text, font=font, fill=BLACK)

    def update(self):
        print("Updating")
        i = 0
        image = Image.new('1', self.my_papirus.size, WHITE)
        draw = ImageDraw.Draw(image)
        for zone in self.zones:
            self.updateZone(zone, i, draw)
            i += 1
        self.my_papirus.display(image)
        #self.my_papirus.partial_update()
        self.my_papirus.update()

    def createLayout(self, setup, mqtt):
        for zone in setup["zones"].keys():
            self.zones += [Zone(zone, setup["zones"][zone], mqtt, self.update)]

    def loadConfig(self, configFilename):
        setup = None
        mqtt = None
        with open(configFilename) as f:
            config = json.load(f)
        mqttConfig = config["mqtt"]["configFile"]
        setupConfig = config["setup"]["configFile"]
        with open(setupConfig) as f2:
            setup = json.load(f2)
        with open(mqttConfig) as f2:
            mqtt = json.load(f2)
        return setup, mqtt


    def draw(self):
        # initially set all white background
        image = Image.new('1', self.my_papirus.size, WHITE)

        # prepare for drawing
        draw = ImageDraw.Draw(image)
        printstring = "TEST2"
        draw.text((10, 40), printstring, font=font, fill=BLACK)

        self.my_papirus.display(image)
        partial = True
        if partial:
            self.my_papirus.partial_update()
        else:
            self.my_papirus.update()
