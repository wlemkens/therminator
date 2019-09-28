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

