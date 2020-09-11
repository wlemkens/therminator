from __future__ import print_function

from PIL import ImageFont, ImageDraw, Image
from waveshare_epd import epd7in5bc
import time

from Display import Display

class WaveshareDisplay(Display.Display):
    def __init__(self, config, logFilename = None):
        self.epd = epd7in5bc.EPD()
        self.epd.init()
        self.epd.Clear()
        self.WHITE = 1
        self.BLACK = 0
        super().__init__(config, logFilename)
        time.sleep(30)
        self.fullUpdate = True
        self.update()
        initCount = 0
        while True:
            time.sleep(self.fullUpdateInterval)
            self.fullUpdate = True

    def getWidth(self):
        return self.epd.width

    def getHeight(self):
        return self.epd.height

    def display(self, image):
        if self.fullUpdate:
            self.epd.display(self.epd.getbuffer(image[0]), self.epd.getbuffer(image[1]))
            self.fullUpdate = False

    def updateZone(self, zone, index, draws):
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
        if battery:
            batteryText = "{:}%".format(battery)
        else:
            print("No battery status for {:}".format(zone.getLabel()))
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

