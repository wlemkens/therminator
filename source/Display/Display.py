from __future__ import print_function

from PIL import ImageFont, ImageDraw, Image
import time
import threading
from datetime import datetime

import json

import paho.mqtt.client as mqtt

from Entity.Zone import Zone
from Entity.Boiler import Boiler
from Entity.Exterior import Exterior
from Entity.Home import Home

class Display(object):

    def __init__(self, config, logFilename):
        self.zones = []
        self.boiler = None
        self.lock = False
        self.fullUpdate = True
        self.mode = None
        self.fontPath = "/usr/local/share/fonts/VoiceActivatedBB_reg.otf"
        self.boldFontPath = "/usr/local/share/fonts/VoiceActivatedBB_bold.otf"
        self.logFile = logFilename
        self.awayFontSize = 1
        self.delayedUpdateTimer = None
        self.setup, self.mqtt, self.fullUpdateInterval = self.loadConfig(config)
        self.createLayout(self.setup, self.mqtt)
        if self.logFile:
            with open(self.logFile,"w+") as f:
                f.write("datetime;")
                for zone in self.zones:
                    f.write("{:}_{:};{:}_{:};{:}_{:};".format("setpoint",zone.getName(), "temperature",zone.getName(),"level",zone.getName(),"status",zone.getName()))
                f.write("{:};{:};{:};{:};{:}\n".format("requestePower", "deliveredPower","returnTemperature","flowTemperature","exteriorTemperature"))
        self.client = mqtt.Client()
        self.client.connect(self.mqtt["address"], self.mqtt["port"], 60)
        self.away = False

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
            font = ImageFont.truetype(self.boldFontPath, fontsize)
            size = font.getsize(printstring)
            stringlength = size[0]
            stringwidth = size[1]

        #font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', fontsize-1)
        font = ImageFont.truetype(self.boldFontPath, fontsize-1)
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
        fullSize = min(self.getHeight()-heightPadding*2, self.getWidth()/3)
        heightPadding = (self.getHeight() - fullSize) / 2
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
        fullSize = min(self.getHeight()-heightPadding*2, self.getWidth()/3)
        heightPadding = (self.getHeight() - fullSize) / 2
        percent = 0.01 * power
        pp = percent * percent
        offset = int(0.5 * fullSize * (1 - percent))
        draw.pieslice([10 + 2, heightPadding - heighOffset, 10 + fullSize + 2, heightPadding + fullSize - heighOffset], -90, 90, fill=self.WHITE, outline=self.BLACK)
        draw.pieslice([10 + offset + 2, heightPadding + offset - heighOffset, fullSize + 10 - offset + 2, heightPadding + fullSize - offset - heighOffset], -90, 90, fill=self.BLACK)


    def updateZone(self, zone, index, draws):
        print("Updating zone '{:}'".format(zone.getName()))
        draw = draws[0]
        drawc = draws[1]
        lineHeight = self.fontSize + 1
        lineWidth = self.getWidth() / 3
        totalHeight = (len(self.zones)-1) * lineHeight + self.largeFontSize+1
        freeSpace = self.getHeight() - totalHeight
        padding = freeSpace/5
        name = "{:}".format(zone.getLabel())
        text = "{:}/{:} ".format(zone.getTemperature(), zone.getSetpoint())
        sptext = "/{:} ".format(zone.getSetpoint())
        tempText = "{:} ".format(zone.getTemperature())
        temp = zone.getTemperature()
        sp = zone.getSetpoint()
        tempTooLow = temp != None and sp != None and temp < sp
        textColor = self.BLACK
        if index == 0:
            paddingMult = 3
            font = ImageFont.truetype(self.fontPath, self.largeFontSize)
            boldFont = ImageFont.truetype(self.boldFontPath, self.largeFontSize)
            if not zone.isEnabled():
                size = font.getsize(tempText)
                x1 = self.getWidth() - lineWidth - self.fontSize * 3 - 2
                y1 = padding*paddingMult+2
                x2 = x1 + size[0]-4
                y2 = y1 + size[1]+1
                draw.text((x2, padding*paddingMult), sptext, font=font, fill=self.BLACK)
                draw.rectangle(((x1,y1), (x2,y2)),fill=self.BLACK,outline=self.BLACK)
                textColor = self.WHITE
                draw.text((self.getWidth() - lineWidth - self.fontSize * 3, padding*paddingMult), tempText, font=font, fill=textColor)
            else:
                if tempTooLow:
                    draw.text((self.getWidth() - lineWidth - self.fontSize * 3 -1, padding*paddingMult-1), tempText, font=boldFont, fill=textColor)
                    size = font.getsize(tempText)
                    draw.text((size[0]*.9 + self.getWidth() - lineWidth - self.fontSize * 3, padding*paddingMult), sptext, font=font, fill=self.BLACK)
                else:
                    draw.text((self.getWidth() - lineWidth - self.fontSize * 3, padding*paddingMult), text, font=font, fill=self.BLACK)
        else:
            paddingMult = 4
            font = ImageFont.truetype(self.fontPath, self.fontSize)
            boldFont = ImageFont.truetype(self.boldFontPath, self.fontSize)
            draw.text((self.getWidth() - lineWidth - self.fontSize * 3, lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding), name, font=font, fill=self.BLACK)
            #draw.text((self.getWidth() - lineWidth , lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding), text, font=font, fill=self.BLACK)
            textColor = self.BLACK
            if not zone.isEnabled():
                size = font.getsize(tempText)
                x1 = self.getWidth() - lineWidth -2
                y1 = lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding+2
                x2 = x1 + size[0]
                y2 = y1 + size[1]
                draw.text((x2, lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding), sptext, font=font, fill=self.BLACK)
                draw.rectangle(((x1,y1), (x2,y2)),fill=self.BLACK,outline=self.BLACK)
                textColor = self.WHITE
                #draw.text((self.getWidth() - lineWidth - self.fontSize * 3, padding*paddingMult), tempText, font=font, fill=textColor)
                draw.text((self.getWidth() - lineWidth , lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding), tempText, font=font, fill=textColor)
            else:
                if tempTooLow:
                    draw.text((self.getWidth() - lineWidth -1 , lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding-1), tempText, font=boldFont, fill=self.BLACK)
                    size = font.getsize(tempText)
                    draw.text((size[0] * 0.9 + self.getWidth() - lineWidth , lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding), sptext, font=font, fill=self.BLACK)
                else:
                    draw.text((self.getWidth() - lineWidth , lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding), text, font=font, fill=self.BLACK)

    def drawAway(self, draws):
        draw = draws[0]
        font = ImageFont.truetype(self.boldFontPath, self.awayFontSize)
        draw.text((self.getWidth()*0.1, self.getHeight()*0.1), "AWAY", font=font, fill=self.BLACK)

    def drawMode(self, draws, mode):
        draw = draws[0]
        font = ImageFont.truetype(self.boldFontPath, self.awayFontSize)
        draw.text((self.getWidth()*0.1, self.getHeight()*0.1), mode, font=font, fill=self.BLACK)

    def setToSleep(self):
        pass

    def updateClock(self, draw):
        font = ImageFont.truetype(self.fontPath, self.clockFontSize)
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        draw.text((self.getWidth()*0.1, self.clockFontSize), current_time, font=font, fill=self.BLACK)

    def drawModeSmall(self, draws, mode):
        if mode == None:
            mode = "no mode"
        draw = draws[0]
        font = ImageFont.truetype(self.fontPath, self.modeFontSize)
        x = self.getWidth()*0.1
        y = self.clockFontSize+self.modeFontSize/2
        draw.text((x, y), mode, font=font, fill=self.BLACK)

    def update(self):
        if not self.lock:
            self.lock = True
            if self.delayedUpdateTimer != None:
                self.delayedUpdateTimer.cancel()
                self.delayedUpdateTimer = None
            i = 0
            size = (self.getWidth(), self.getHeight())
            image = Image.new('1', size, self.WHITE)
            imagec = Image.new('1', size, self.WHITE)
            draw = ImageDraw.Draw(image)
            drawc = ImageDraw.Draw(imagec)
            print("Mode = '{:}'".format(self.home.getMode()))
            if self.home.isAway() or self.home.getMode() == 'away':
                if not self.mode == "away":
                    self.drawAway([draw,drawc])
                    self.mode = "away"
                    self.fullUpdate = True
                    self.display([image, imagec])
                    self.setToSleep()
            elif self.home.getMode() ==  'night':
                if not self.mode == "night":
                    self.drawMode([draw,drawc], "Night")
                    self.mode = "night"
                    self.fullUpdate = True
                    self.display([image, imagec])
                    self.setToSleep()
            else:
                self.mode = self.home.getMode()
                for zone in self.zones:
                    self.updateZone(zone, i, [draw,drawc])
                    i += 1
                self.updateRequestedPower(self.boiler.getRequestedPower(),draw)
                self.updateDeliveredPower(self.boiler.getDeliveredPower(),draw)
                self.updateExteriorTemperature(self.exterior.getTemperature(),draw)
                self.updateClock(draw)
                self.drawModeSmall([draw,drawc],self.mode)
                self.display([image, imagec])
            self.log()
            self.lock = False
        else:
            if self.delayedUpdateTimer:
                self.delayedUpdateTimer.cancel()
                self.delayedUpdateTimer = None
            self.delayedUpdateTimer = threading.Timer(self.fullUpdateInterval, self.delayedUpdate)

    def delayedUpdate(self):
        self.update()

    def display(self, image):
        pass

    def getWidth(self):
        pass

    def getHeight(self):
        pass

    def createLayout(self, setup, mqtt):
        self.awayFontSize, dims = self.getFontSize([self.getWidth()*0.8, self.getHeight()*0.8], "AWAY")
        self.clockFontSize = max(8,int(self.getHeight() * 0.03))
        self.modeFontSize = max(8,int(self.getHeight() * 0.07))
        self.home = Home(mqtt, self.update)
        for zone in setup["zones"]:
            self.zones += [Zone(zone, mqtt, self.update)]
        self.boiler = Boiler(mqtt, self.update)
        self.exterior = Exterior(mqtt, self.update)
        lineHeight = 1.0 * self.getHeight() / len(self.zones)
        lineWidth = self.getWidth() / 3
#        self.fontSize, dims = self.getFontSize([lineWidth, lineHeight], "44.4/44.4")
        self.fontSize, dims = self.getFontSize([lineWidth, lineHeight], "00.0/00.0")
#        self.largeFontSize, dims = self.getFontSize([lineWidth + self.fontSize * 3, lineHeight], "44.4/44.4")
        self.largeFontSize, dims = self.getFontSize([lineWidth + self.fontSize * 3, lineHeight], "00.0/00.0")


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
                        f.write("{:};{:};{:};{:};".format(zone.getSetpoint(), zone.getTemperature(), zone.getLevel(), zone.isEnabled()))
                    f.write("{:};{:};{:};{:};{:}\n".format(self.boiler.getRequestedPower(), self.boiler.getDeliveredPower(), self.boiler.getReturnTemperature(), self.boiler.getFlowTemperature(), self.exterior.getTemperature()))



