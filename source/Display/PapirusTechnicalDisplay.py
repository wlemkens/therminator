from Display.PapirusDisplay import PapirusDisplay

class PapirusTechnicalDisplay(PapirusDisplay)

    def __init__(self, config, logFilename = None):
        super.(PapirusTechnicalDisplay, self).__init__(config, logFilename)

    def update(self):
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
