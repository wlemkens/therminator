from __future__ import print_function

from PIL import ImageFont, ImageDraw, Image
from waveshare_epd import epd7in5bc
import time
import logging
from datetime import datetime

from Heartbeat.Modules import Modules
from Display import Display

class WaveshareDisplay(Display.Display):
    def __init__(self, config, logFilename = None, syslog = None):
        logging.basicConfig(filename=syslog, level=logging.DEBUG)
        self.lastNetworkFailure = True
        self.lastDomoticzFailure = True
        self.lastBrokenDependencies = []
        self.networkFailure = False
        self.domoticzFailure = True
        self.iconSize = 20
        self.networkIcon = Image.open("/home/wim/projects/therminator/images/network.png").resize((self.iconSize, self.iconSize))
        self.domoticzIcon = Image.open("/home/wim/projects/therminator/images/domoticz.png").resize((self.iconSize, self.iconSize))
        self.connectorIcon = Image.open("/home/wim/projects/therminator/images/connector.png").resize((self.iconSize, self.iconSize))
        self.monitorIcon = Image.open("/home/wim/projects/therminator/images/monitor.png").resize((self.iconSize, self.iconSize))
        self.thermostatIcon = Image.open("/home/wim/projects/therminator/images/thermostat.png").resize((self.iconSize, self.iconSize))
        self.isSleeping = False
        self.epd = epd7in5bc.EPD()
        self.epd.init()
        self.epd.Clear()
        self.WHITE = 1
        self.BLACK = 0
        super().__init__(config, logFilename, syslog)
        self.pingTopic = "therminator/in/ping"
        self.client.subscribe(self, [(self.pingTopic, 2)])
        self.networkFailure = not self.ping("192.168.0.183")
        self.client.publish("therminator/request", "ping")
        time.sleep(30)
        self.fullUpdate = True
        self.update()
        initCount = 0
        while True:
            time.sleep(self.fullUpdateInterval)
            self.fullUpdate = True
            doUpdate = False
            if self.lastNetworkFailure != self.networkFailure:
                logging.debug("{:} Network status changed to {:}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.networkFailure))
                doUpdate = True
                self.lastNetworkFailure = self.networkFailure
            if self.lastDomoticzFailure != self.domoticzFailure:
                logging.debug("{:} Domoticz status changed to {:}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.domoticzFailure))
                doUpdate = True
                self.lastDomoticzFailure = self.domoticzFailure
            if self.lastBrokenDependencies != self.watchdog.brokenDependencies:
                logging.debug("{:} Dependency status changed to {:}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.watchdog.brokenDependencies))
                doUpdate = True
                self.lastBrokenDependencies = self.watchdog.brokenDependencies
            if doUpdate:
                self.update()
            time.sleep(10)
            self.networkFailure = not self.ping("192.168.0.183")
            logging.debug("{:} Network status : {:}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), not self.networkFailure))
            self.domoticzFailure = True
            logging.debug("{:} Requesting ping".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.client.publish("therminator/request", "ping")

    def setToSleep(self):
        try:
#            time.sleep(2)
            self.epd.sleep()
            self.isSleeping = True
        except:
            logging.error("{:} : Unexpected error:".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), sys.exc_info()[0])

    def getWidth(self):
        return self.epd.width

    def getHeight(self):
        return self.epd.height

    def display(self, image):
        logging.debug("{:} : display".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        if self.isSleeping:
            self.epd.init()
            self.isSleeping = False

        if self.fullUpdate:
            logging.debug("{:} : Full update".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.epd.display(self.epd.getbuffer(image[0]), self.epd.getbuffer(image[1]))
            self.fullUpdate = False
            logging.debug("{:} : Full update done".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def updateZone(self, zone, index, draws, images):
        logging.debug("{:} : Updating zone '{:}'".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), zone.getName()))
        draw = draws[0]
        drawc = draws[1]
        lineHeight = self.fontSize + 1
        lineWidth = self.getWidth() / 3
        totalHeight = (len(self.zones)-1) * lineHeight + self.largeFontSize+1
        freeSpace = self.getHeight() - totalHeight
        padding = freeSpace/5
        name = "{:}".format(zone.getLabel())
        sp = zone.getSetpoint()
        text = "{:} ".format(zone.getTemperature())
        sptext = " "
        if sp:
            text = "{:}/{:} ".format(zone.getTemperature(), zone.getSetpoint())
            sptext = "/{:} ".format(zone.getSetpoint())
        tempText = "{:} ".format(zone.getTemperature())
        temp = zone.getTemperature()
        sp = zone.getSetpoint()
        battery = zone.getBattery()
        batteryText = ""
        if battery != None:
            batteryText = "{:}%".format(battery)
        else:
            logging.debug("{:} : No battery status for {:}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), zone.getLabel()))
        tempTooLow = temp != None and sp != None and temp < sp
        textColor = self.BLACK
        if index == 0:
            paddingMult = 3
            font = ImageFont.truetype(self.fontPath, self.largeFontSize)
            boldFont = ImageFont.truetype(self.boldFontPath, self.largeFontSize)
            fullSize = font.getsize(text)
            smallFont = ImageFont.truetype(self.fontPath, int(self.largeFontSize*0.4))
            if not zone.isEnabled():
                size = font.getsize(tempText)
                x1 = self.getWidth() - lineWidth - self.fontSize * 3 - 2
                y1 = padding*paddingMult+2
                x2 = x1 + size[0]-4
                y2 = y1 + size[1]+1
                x = self.getWidth() - lineWidth - self.fontSize * 3
                y = padding*paddingMult
                draw.text((x2, padding*paddingMult), sptext, font=font, fill=self.BLACK)
                if tempTooLow:
                    drawc.rectangle(((x1,y1), (x2,y2)),fill=self.BLACK,outline=self.BLACK)
                    textColor = self.WHITE
                    drawc.text((x, y), tempText, font=font, fill=textColor)
                else:
                    draw.rectangle(((x1,y1), (x2,y2)),fill=self.BLACK,outline=self.BLACK)
                    textColor = self.WHITE
                    draw.text((x, y), tempText, font=font, fill=textColor)
#                draw.text((x-20,y+10+fullSize[1]), batteryText, font=smallFont, fill=textColor)
            else:
                x = self.getWidth() - lineWidth - self.fontSize * 3
                y = padding*paddingMult
                if tempTooLow:
                    draw.text((x, y), tempText, font=boldFont, fill=textColor)
                    size = font.getsize(tempText)
                    draw.text((size[0]*.9 + self.getWidth() - lineWidth - self.fontSize * 3, y), sptext, font=font, fill=self.BLACK)
                else:
                    draw.text((x, y), text, font=font, fill=self.BLACK)
            if battery and battery > 5:
                draw.text((x-20,y+5+fullSize[1]), batteryText, font=smallFont, fill=self.BLACK)
            else:
                drawc.text((x-20,y+5+fullSize[1]), batteryText, font=smallFont, fill=self.BLACK)
        else:
            paddingMult = 4
            font = ImageFont.truetype(self.fontPath, self.fontSize)
            fullSize = font.getsize(text)
            smallFont = ImageFont.truetype(self.fontPath, int(self.fontSize*0.4))
            boldFont = ImageFont.truetype(self.boldFontPath, self.fontSize)
            x = self.getWidth() - lineWidth - self.fontSize * 3
            y = lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding
            draw.text((x, y), name, font=font, fill=self.BLACK)
            textColor = self.BLACK
            tx = self.getWidth() - lineWidth
            ty = lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding
            if not zone.isEnabled():
                size = font.getsize(tempText)
                x1 = self.getWidth() - lineWidth -2
                y1 = lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding+2
                x2 = x1 + size[0]
                y2 = y1 + size[1]
                draw.text((x2, lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding), sptext, font=font, fill=self.BLACK)
                if tempTooLow:
                    drawc.rectangle(((x1,y1), (x2,y2)),fill=self.BLACK,outline=self.BLACK)
                    textColor = self.WHITE
                    drawc.text((tx, ty), tempText, font=font, fill=textColor)
                else:
                    draw.rectangle(((x1,y1), (x2,y2)),fill=self.BLACK,outline=self.BLACK)
                    textColor = self.WHITE
                    draw.text((tx, ty), tempText, font=font, fill=textColor)
            else:
                if tempTooLow:
                    draw.text((self.getWidth() - lineWidth, lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding), tempText, font=boldFont, fill=self.BLACK)
                    size = font.getsize(tempText)
                    draw.text((size[0] * 0.9 + self.getWidth() - lineWidth , lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding), sptext, font=font, fill=self.BLACK)
                else:
                    draw.text((tx, ty), text, font=font, fill=self.BLACK)
            if battery and battery > 5:
                draw.text((tx-30, ty-5+fullSize[1]), batteryText, font=smallFont, fill=self.BLACK)
            else:
                drawc.text((tx-30, ty-5+fullSize[1]), batteryText, font=smallFont, fill=self.BLACK)
        logging.debug("{:} : Updating zone done".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def drawDependencies(self, image):
        iconWidth = 20
        verticalOffset = 60
        horizontalOffset = iconWidth
        if self.networkFailure:
            image.paste(self.networkIcon, (horizontalOffset + 0 * iconWidth, verticalOffset, horizontalOffset + 1 * iconWidth,  verticalOffset + iconWidth))
        if self.domoticzFailure:
            image.paste(self.domoticzIcon, (horizontalOffset + 1 * iconWidth, verticalOffset, horizontalOffset + 2 * iconWidth,  verticalOffset + iconWidth))
        if Modules.CONNECTOR in self.watchdog.brokenDependencies:
            image.paste(self.connectorIcon, (horizontalOffset + 2 * iconWidth, verticalOffset, horizontalOffset + 3 * iconWidth,  verticalOffset + iconWidth))
        if Modules.MONITOR in self.watchdog.brokenDependencies:
            image.paste(self.monitorIcon, (horizontalOffset + 3 * iconWidth, verticalOffset, horizontalOffset + 4 * iconWidth,  verticalOffset + iconWidth))
        if Modules.THERMOSTAT in self.watchdog.brokenDependencies:
            image.paste(self.thermostatIcon, (horizontalOffset + 4 * iconWidth, verticalOffset, horizontalOffset + 5 * iconWidth,  verticalOffset + iconWidth))

    def on_message(self, client, userdata, message):
        if message.topic == self.pingTopic:
            self.domoticzFailure = False
