from __future__ import print_function

from papirus import Papirus
import time

from Display import Display

WHITE = 1
BLACK = 0


class PapirusDisplay(Display):
    def __init__(self, config, logFilename = None):
        Display.__init__(config, logFilename)
        self.my_papirus = Papirus(rotation=180)
        while True:
            time.sleep(self.fullUpdateInterval*60)
            self.fullUpdate = True

    def getWidth(self):
        return self.my_papirus.width

    def getHeight(self):
        return self.my_papirus.height

    def display(self, image):
        if not self.lock:
            self.my_papirus.display(image[0])
            if self.fullUpdate:
                self.my_papirus.update()
                self.fullUpdate = False
            else:
                self.my_papirus.partial_update()

