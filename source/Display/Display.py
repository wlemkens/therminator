from __future__ import print_function

from PIL import ImageFont, ImageDraw, Image
import time
from datetime import datetime

import json

import paho.mqtt.client as mqtt

from Entity.Zone import Zone
from Entity.Boiler import Boiler
from Entity.Exterior import Exterior

class Display(object):

    def __init__(self, config, logFilename):
        self.zones = []
        self.boiler = None
        self.lock = False
        self.fullUpdate = True
        self.fontPath = "/usr/local/share/fonts/Righteous-Regular.ttf"
        self.logFile = logFilename
        self.setup, self.mqtt, self.fullUpdateInterval = self.loadConfig(config)
        self.createLayout(self.setup, self.mqtt)
        if self.logFile:
            with open(self.logFile,"w+") as f:
                f.write("datetime;")
                for zone in self.zones:
                    f.write("{:}_{:};{:}_{:};{:}_{:};".format("setpoint",zone.getName(), "temperature",zone.getName(),"level",zone.getName()))
                f.write("{:};{:};{:};{:}\n".format("requestePower", "deliveredPower","returnTemperature","flowTemperature"))
        self.client = mqtt.Client()
        self.client.connect(self.mqtt["address"], self.mqtt["port"], 60)

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

    def updateExteriorTemperature(self, temperature, draw):
        lineHeight = self.fontSize + 1
        lineWidth = self.getWidth() / 3
        totalHeight = (len(self.zones)-1) * lineHeight + self.largeFontSize+1
        freeSpace = self.getHeight() - totalHeight
        padding = freeSpace/5
        fontSize = int((self.largeFontSize + self.fontSize) / 2)
        font = ImageFont.truetype(self.fontPath, fontSize)
        text = "{:}°C".format(temperature)
        size = font.getsize(text)
        x = self.getWidth() - lineWidth - self.fontSize * 3 + (lineWidth + self.fontSize * 3 - size[0]) / 2
        draw.text((x, padding), text, font=font, fill=self.BLACK)

    def updateRequestedPower(self, power, draw, heighOffset = 0):
        heightPadding = 35
        fullSize = self.getHeight()-heightPadding*2
        percent = 0.01 * power
        pp = percent * percent
        offset = int(0.5 * fullSize * (1 - percent))
        x1 = 10 + offset
        y1 = heightPadding + offset - heighOffset
        x2 = fullSize + 10 - offset
        y2 = heightPadding + fullSize - offset - heighOffset
        draw.pieslice([10, heightPadding - heighOffset, 10 + fullSize, heightPadding + fullSize - heighOffset], 90, 270, fill=self.WHITE, outline=self.BLACK)
        draw.pieslice([x1, y1, x2, y2], 90, 270, fill=self.BLACK)

    def updateDeliveredPower(self, power, draw, heighOffset = 0):
        heightPadding = 35
        fullSize = self.getHeight()-heightPadding*2
        percent = 0.01 * power
        pp = percent * percent
        offset = int(0.5 * fullSize * (1 - percent))
        draw.pieslice([10 + 2, heightPadding - heighOffset, 10 + fullSize + 2, heightPadding + fullSize - heighOffset], -90, 90, fill=self.WHITE, outline=self.BLACK)
        draw.pieslice([10 + offset + 2, heightPadding + offset - heighOffset, fullSize + 10 - offset + 2, heightPadding + fullSize - offset - heighOffset], -90, 90, fill=self.BLACK)


    def updateZone(self, zone, index, draw):
        lineHeight = self.fontSize + 1
        lineWidth = self.getWidth() / 3
        totalHeight = (len(self.zones)-1) * lineHeight + self.largeFontSize+1
        freeSpace = self.getHeight() - totalHeight
        padding = freeSpace/5
        name = "{:}".format(zone.getLabel())
        text = "{:}/{:} ".format(zone.getTemperature(), zone.getSetpoint())
        tempText = "{:} ".format(zone.getTemperature(), zone.getSetpoint())
        temp = zone.getTemperature()
        sp = zone.getSetpoint()
        tempTooLow = temp != None and sp != None and temp < sp
        if index == 0:
            paddingMult = 3
            font = ImageFont.truetype(self.fontPath, self.largeFontSize)
            draw.text((self.getWidth() - lineWidth - self.fontSize * 3, padding*paddingMult), text, font=font, fill=self.BLACK)
            textColor = self.BLACK
            if not zone.isEnabled():
                size = font.getsize(tempText)
                x1 = self.getWidth() - lineWidth - self.fontSize * 3 - 2
                y1 = padding*paddingMult+2
                x2 = x1 + size[0]-4
                y2 = y1 + size[1]+1
                draw.rectangle(((x1,y1), (x2,y2)),fill=self.BLACK,outline=self.BLACK)
                textColor = self.WHITE
                draw.text((self.my_papirus.width - lineWidth - self.fontSize * 3, padding*paddingMult), tempText, font=font, fill=textColor)
            if tempTooLow:
                draw.text((self.my_papirus.width - lineWidth - self.fontSize * 3 -1, padding*paddingMult-1), tempText, font=font, fill=textColor)
        else:
            paddingMult = 4
            font = ImageFont.truetype(self.fontPath, self.fontSize)
            draw.text((self.my_papirus.width - lineWidth - self.fontSize * 3, lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding), name, font=font, fill=self.BLACK)
            draw.text((self.my_papirus.width - lineWidth , lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding), text, font=font, fill=self.BLACK)
            textColor = self.BLACK
            if not zone.isEnabled():
                size = font.getsize(tempText)
                x1 = self.my_papirus.width - lineWidth -2
                y1 = lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding+2
                x2 = x1 + size[0]
                y2 = y1 + size[1]
                draw.rectangle(((x1,y1), (x2,y2)),fill=self.BLACK,outline=self.BLACK)
                textColor = self.WHITE
                draw.text((self.my_papirus.width - lineWidth, lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding), tempText, font=font, fill=textColor)
            if tempTooLow:
                draw.text((self.my_papirus.width - lineWidth -1 , lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding -1), tempText, font=font, fill=textColor)

    def update(self):
        if not self.lock:
            self.lock = True
            i = 0
            size = (self.getWidth(), self.getHeight())
            image = Image.new('1', size, self.WHITE)
            draw = ImageDraw.Draw(image)
            for zone in self.zones:
                self.updateZone(zone, i, draw)
                i += 1
            self.updateRequestedPower(self.boiler.getRequestedPower(),draw)
            self.updateDeliveredPower(self.boiler.getDeliveredPower(),draw)
            self.updateExteriorTemperature(self.exterior.getTemperature(),draw)
            self.display([image])
            self.log()
            self.lock = False

    def display(self, image):
        pass

    def getWidth(self):
        pass

    def getHeight(self):
        pass

    def createLayout(self, setup, mqtt):
        for zone in setup["zones"]:
            self.zones += [Zone(zone, mqtt, self.update)]
        self.boiler = Boiler(mqtt, self.update)
        self.exterior = Exterior(mqtt, self.update)
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
            if self.boiler.getRequestedPower() == None or self.boiler.getDeliveredPower() == None or self.boiler.getReturnTemperature() == None or self.boiler.getFlowTemperature() == None:
                hasNone = True
            if not hasNone:
                with open(self.logFile,"a") as f:
                    now = datetime.now()
                    dtime = now.strftime("%Y-%m-%d %H:%M:%S")
                    f.write("{:};".format(dtime))
                    for zone in self.zones:
                        f.write("{:};{:};{:};".format(zone.getSetpoint(), zone.getTemperature(), zone.getLevel()))
                    f.write("{:};{:};{:};{:}\n".format(self.boiler.getRequestedPower(), self.boiler.getDeliveredPower(), self.boiler.getReturnTemperature(), self.boiler.getFlowTemperature()))


