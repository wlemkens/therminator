from __future__ import print_function

from papirus import Papirus
import time

from Display import Display

class PapirusDisplay(Display.Display):

    def __init__(self, config, logFilename):
        self.my_papirus = Papirus(rotation=180)
        self.WHITE = 1
        self.BLACK = 0
        super().__init__(config, logFilename)
        while True:
            time.sleep(self.fullUpdateInterval*60)
            self.fullUpdate = True

    def getWidth(self):
        return self.my_papirus.width

    def getHeight(self):
        return self.my_papirus.height

    def display(self, image):
        self.my_papirus.display(image[0])
        if self.fullUpdate:
            self.my_papirus.update()
            self.fullUpdate = False
        else:
            self.my_papirus.partial_update()
