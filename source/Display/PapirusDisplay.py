from __future__ import print_function

import argparse
from papirus import Papirus
from PIL import ImageFont, ImageDraw, Image
import sys
import os
import time
from datetime import datetime

import json
from json import JSONDecoder
from collections import OrderedDict

import paho.mqtt.client as mqtt

from Entity.Zone import Zone
from Entity.Boiler import Boiler

WHITE = 1
BLACK = 0


class PapirusDisplay(object):
    def __init__(self, config, logFilename = None):
        self.zones = []
        self.boiler = None
        self.lock = False
        self.fullUpdate = True
        self.fontPath = "/usr/local/share/fonts/Righteous-Regular.ttf"
        self.logFile = logFilename
        self.my_papirus = Papirus(rotation=180)
        self.setup, self.mqtt, self.fullUpdateInterval = self.loadConfig(config)
        self.createLayout(self.setup, self.mqtt)
        if self.logFile:
            with open(self.logFile,"w+") as f:
                f.write("datetime;")
                for zone in self.zones:
                    f.write("{:}_{:};{:}_{:};{:}_{:};".format("setpoint",zone.getName(), "temperature",zone.getName(),"level",zone.getName()))
                f.write("{:};{:}\n".format("requestePower", "deliveredPower"))
        self.client = mqtt.Client()
        self.client.connect(self.mqtt["address"], self.mqtt["port"], 60)
        while True:
            time.sleep(self.fullUpdateInterval*60)
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
        draw.pieslice([10, heightOffset, 10 + fullSize, heightOffset + fullSize], 90, 270, fill=WHITE, outline=BLACK)
        draw.pieslice([x1, y1, x2, y2], 90, 270, fill=BLACK)

    def updateDeliveredPower(self, power, draw):
        heightOffset = 35
        fullSize = self.my_papirus.height-heightOffset*2
        percent = 0.01 * power
        pp = percent * percent
        offset = int(0.5 * fullSize * (1 - percent))
        draw.pieslice([10 + 2, heightOffset, 10 + fullSize + 2, heightOffset + fullSize], -90, 90, fill=WHITE, outline=BLACK)
        draw.pieslice([10 + offset + 2, heightOffset + offset, fullSize+10-offset+2, heightOffset + fullSize - offset], -90, 90, fill=BLACK)


    def updateZone(self, zone, index, draw):
        lineHeight = self.fontSize + 1
        lineWidth = self.my_papirus.width / 3
        totalHeight = (len(self.zones)-1) * lineHeight + self.largeFontSize+1
        freeSpace = self.my_papirus.height - totalHeight
        padding = freeSpace/3
        name = "{:}".format(zone.getLabel())
        text = "{:}/{:} ".format(zone.getTemperature(), zone.getSetpoint())
        tempText = "{:} ".format(zone.getTemperature(), zone.getSetpoint())
        temp = zone.getTemperature()
        sp = zone.getSetpoint()
        tempTooLow = temp != None and sp != None and temp < sp
        if index == 0:
            font = ImageFont.truetype(self.fontPath, self.largeFontSize)
            draw.text((self.my_papirus.width - lineWidth - self.fontSize * 3, padding), text, font=font, fill=BLACK)
            if tempTooLow:
                draw.text((self.my_papirus.width - lineWidth - self.fontSize * 3 -1, padding-1), tempText, font=font, fill=BLACK)
        else:
            font = ImageFont.truetype(self.fontPath, self.fontSize)
            draw.text((self.my_papirus.width - lineWidth - self.fontSize * 3, lineHeight * (index-1) + self.largeFontSize+1 + 2*padding), name, font=font, fill=BLACK)
            draw.text((self.my_papirus.width - lineWidth , lineHeight * (index-1) + self.largeFontSize+1 + 2*padding), text, font=font, fill=BLACK)
            if tempTooLow:
                draw.text((self.my_papirus.width - lineWidth -1 , lineHeight * (index-1) + self.largeFontSize+1 + 2*padding -1), tempText, font=font, fill=BLACK)

    def update(self):
        if not self.lock:
            self.lock = True
            i = 0
            image = Image.new('1', self.my_papirus.size, WHITE)
            draw = ImageDraw.Draw(image)
            for zone in self.zones:
                self.updateZone(zone, i, draw)
                i += 1
            self.updateRequestedPower(self.boiler.getRequestedPower(),draw)
            self.updateDeliveredPower(self.boiler.getDeliveredPower(),draw)
            self.my_papirus.display(image)
            if self.fullUpdate:
                self.my_papirus.update()
                self.fullUpdate = False
            else:
                self.my_papirus.partial_update()
            self.log()
            self.lock = False

    def createLayout(self, setup, mqtt):
        for zone in setup["zones"]:
            self.zones += [Zone(zone, mqtt, self.update)]
        self.boiler = Boiler(mqtt, self.update)
        lineHeight = 1.0 * self.my_papirus.height / len(self.zones)
        lineWidth = self.my_papirus.width / 3
        self.fontSize, dims = self.getFontSize([lineWidth, lineHeight], "44.4/44.4")
        self.largeFontSize, dims = self.getFontSize([lineWidth + self.fontSize * 3, lineHeight], "44.4/44.4")

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
        return setup, mqtt, float(config["fullUpdateInterval"])

    def log(self):
        if (self.logFile):
            hasNone = False
            for zone in self.zones:
                if zone.getSetpoint() == None or zone.getTemperature() == None or zone.getLevel() == None:
                    hasNone = True
            if self.boiler.getRequestedPower() == None or self.boiler.getDeliveredPower() == None:
                hasNone = True
            if not hasNone:
                with open(self.logFile,"a") as f:
                    now = datetime.now()
                    dtime = now.strftime("%Y-%m-%d %H:%M:%S")
                    f.write("{:};".format(dtime))
                    for zone in self.zones:
                        f.write("{:};{:};{:};".format(zone.getSetpoint(), zone.getTemperature(), zone.getLevel()))
                    f.write("{:};{:}\n".format(self.boiler.getRequestedPower(), self.boiler.getDeliveredPower()))


