import numpy as np
import datetime
from datetime import timedelta

from PIL import ImageFont, ImageDraw, Image

from Display.PapirusDisplay import PapirusDisplay

WHITE = 1
BLACK = 0

class PapirusTechnicalDisplay(PapirusDisplay):

    def __init__(self, config, logFilename = None):
        self.WHITE = 1
        self.historyWidth = self.my_papirus.height-35*2
        self.historyHeight = 35*2-15*2
        self.historyLength = 60
        self.history = []
        super(PapirusTechnicalDisplay, self).__init__(config, logFilename)

    def update(self):
        print("Updating techical")
        if not self.lock:
            self.lock = True
            i = 0
            image = Image.new('1', self.my_papirus.size, WHITE)
            draw = ImageDraw.Draw(image)
            for zone in self.zones:
                self.updateZone(zone, i, draw)
                i += 1
            self.updateRequestedPower(self.boiler.getRequestedPower(),draw,20)
            self.updateDeliveredPower(self.boiler.getDeliveredPower(),draw,20)
            self.my_papirus.display(image)
            if self.fullUpdate:
                self.my_papirus.update()
                self.fullUpdate = False
            else:
                self.my_papirus.partial_update()
            self.log()
            self.lock = False
        print("Updated technical")

    def collectInfo(self):
        bucketLength = 1.0 * self.historyLength / self.historyWidth
        now = datetime.datetime.now()
        start = now
        if len(self.history[0]) > 0:
            start = self.history[0][0]
        else:
             for i in range(self.historyWidth):
	             self.history += [(start + i * bucketLength, [])]
        bucketIndex = (now - start).total_seconds() / bucketLength
        if bucketIndex >= len(self.history):
            self.history[bucketIndex]


