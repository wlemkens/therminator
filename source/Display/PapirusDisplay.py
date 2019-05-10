from __future__ import print_function

import argparse
from papirus import Papirus
from PIL import ImageFont, ImageDraw, Image
import sys
import os
import time

import json
from json import JSONDecoder
from collections import OrderedDict

import paho.mqtt.client as mqtt

from Entity.Zone import Zone

WHITE = 1
BLACK = 0


class PapirusDisplay(object):
    def __init__(self, config):
        self.zones = []
        self.lock = False
        self.fullUpdate = True
        self.fontPath = "/usr/local/share/fonts/Righteous-Regular.ttf"
        self.my_papirus = Papirus()
        self.setup, self.mqtt = self.loadConfig(config)
        self.createLayout(self.setup, self.mqtt)
        self.client = mqtt.Client()
        self.client.connect(self.mqtt["address"], self.mqtt["port"], 60)
        while True:
            time.sleep(5*60)
            self.fullUpdate = True


    def getFontSize(self, area, printstring):
        # returns (ideal fontsize, (length of text, height of text)) that maximally
        # fills a papirus object for a given string
        fontsize = 0
        stringlength = 0
        stringwidth = 0

        maxLength = area[0]
        maxHeight = area[1]

        while (stringlength <= maxLength and stringwidth <= maxHeight):

            fontsize += 1
            font = ImageFont.truetype(self.fontPath, fontsize)
            size = font.getsize(printstring)
            stringlength = size[0]
            stringwidth = size[1]

        #font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', fontsize-1)
        font = ImageFont.truetype(self.fontPath, fontsize-1)
        return fontsize-1, font.getsize(printstring)

    def updateRequestedPower(self, power, draw):
        heightOffset = 35
        fullSize = self.my_papirus.height-heightOffset*2
        percent = 0.01 * power
        pp = percent * percent
        offset = int(0.5 * fullSize * (1 - percent))
        x1 = 10 + offset
        y1 = heightOffset + offset
        x2 = fullSize + 10 - offset
        y2 = heightOffset + fullSize - offset
        draw.pieslice([x1, y1, x2, y2], 90, 270, fill=BLACK)

    def updateDeliveredPower(self, power, draw):
        heightOffset = 35
        fullSize = self.my_papirus.height-heightOffset*2
        percent = 0.01 * power
        pp = percent * percent
        offset = int(0.5 * fullSize * (1 - percent))
        draw.pieslice([10 + offset + 2, heightOffset + offset, fullSize+10-offset+2, heightOffset + fullSize - offset], -90, 90, fill=BLACK)


    def updateZone(self, zone, index, draw):
        lineHeight = self.fontSize + 1
        lineWidth = self.my_papirus.width / 3
        name = "{:}".format(zone.getLabel())
        text = "{:}/{:} ".format(zone.getTemperature(), zone.getSetpoint())
        font = ImageFont.truetype(self.fontPath, self.fontSize)
        draw.text((self.my_papirus.width - lineWidth - self.fontSize * 3, lineHeight * (index )), name, font=font, fill=BLACK)
        draw.text((self.my_papirus.width - lineWidth , lineHeight * (index )), text, font=font, fill=BLACK)

    def update(self):
        if not self.lock:
            self.lock = True
            i = 0
            image = Image.new('1', self.my_papirus.size, WHITE)
            draw = ImageDraw.Draw(image)
            for zone in self.zones:
                self.updateZone(zone, i, draw)
                i += 1
            self.updateRequestedPower(100,draw)
            self.updateDeliveredPower(50,draw)
            self.my_papirus.display(image)
            if self.fullUpdate:
                self.my_papirus.update()
                self.fullUpdate = False
            else:
                self.my_papirus.partial_update()
            self.lock = False

    def createLayout(self, setup, mqtt):
        for zone in setup["zones"]:
            self.zones += [Zone(zone, mqtt, self.update)]
        lineHeight = 1.0 * self.my_papirus.height / len(self.zones)
        lineWidth = self.my_papirus.width / 3
        self.fontSize, dims = self.getFontSize([lineWidth, lineHeight], "44.4/44.4")

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
