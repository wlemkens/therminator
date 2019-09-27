from __future__ import print_function

from waveshare_epd import epd7in5bc
import time

from Display import Display

WHITE = 1
BLACK = 0


class PapirusDisplay(Display):
    def __init__(self, config, logFilename = None):
        self.epd = epd7in5bc.EPD()
        self.epd.init()
        self.epd.Clear()
        time.sleep(1)
        while True:
            time.sleep(self.fullUpdateInterval*60)
            self.fullUpdate = True

    def getWidth(self):
        return self.epd.width

    def getHeight(self):
        return self.epd.height

    def display(self, image):
        if not self.lock:
            self.epd.display(self.epd.getbuffer(image[0]), self.epd.getbuffer(image[1]))

