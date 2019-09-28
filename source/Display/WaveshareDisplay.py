from __future__ import print_function

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
        time.sleep(1)
        initCount = 0
        while initCount < 3:
            time.sleep(1)
            self.fullUpdate = True
            initCount += 1
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
            if not zone.isEnabled():
                size = font.getsize(tempText)
                x1 = self.getWidth() - lineWidth - self.fontSize * 3 - 2
                y1 = padding*paddingMult+2
                x2 = x1 + size[0]-4
                y2 = y1 + size[1]+1
                draw.text((x2, padding*paddingMult), sptext, font=font, fill=self.BLACK)
                if tempTooLow:
                    drawc.rectangle(((x1,y1), (x2,y2)),fill=self.BLACK,outline=self.BLACK)
                    textColor = self.WHITE
                    drawc.text((self.getWidth() - lineWidth - self.fontSize * 3, padding*paddingMult), tempText, font=font, fill=textColor)
                else:
                    draw.rectangle(((x1,y1), (x2,y2)),fill=self.BLACK,outline=self.BLACK)
                    textColor = self.WHITE
                    draw.text((self.getWidth() - lineWidth - self.fontSize * 3, padding*paddingMult), tempText, font=font, fill=textColor)
            else:
                if tempTooLow:
                    draw.text((self.getWidth() - lineWidth - self.fontSize * 3 -1, padding*paddingMult-1), tempText, font=font, fill=textColor)
                draw.text((self.getWidth() - lineWidth - self.fontSize * 3, padding*paddingMult), text, font=font, fill=self.BLACK)
        else:
            paddingMult = 4
            font = ImageFont.truetype(self.fontPath, self.fontSize)
            draw.text((self.getWidth() - lineWidth - self.fontSize * 3, lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding), name, font=font, fill=self.BLACK)
            textColor = self.BLACK
            if not zone.isEnabled():
                size = font.getsize(tempText)
                x1 = self.getWidth() - lineWidth -2
                y1 = lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding+2
                x2 = x1 + size[0]
                y2 = y1 + size[1]
                draw.text((x2, padding*paddingMult), sptext, font=font, fill=self.BLACK)
                if tempTooLow:
                    drawc.rectangle(((x1,y1), (x2,y2)),fill=self.BLACK,outline=self.BLACK)
                    textColor = self.WHITE
                    draw.text((self.getWidth() - lineWidth - self.fontSize * 3, padding*paddingMult), tempText, font=font, fill=textColor)
                else:
                    draw.rectangle(((x1,y1), (x2,y2)),fill=self.BLACK,outline=self.BLACK)
                    textColor = self.WHITE
                    draw.text((self.getWidth() - lineWidth - self.fontSize * 3, padding*paddingMult), tempText, font=font, fill=textColor)
            else:
                if tempTooLow:
                    draw.text((self.getWidth() - lineWidth -1 , lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding-1), text, font=font, fill=self.BLACK)
                draw.text((self.getWidth() - lineWidth , lineHeight * (index-1) + self.largeFontSize+1 + paddingMult*padding), text, font=font, fill=self.BLACK)
