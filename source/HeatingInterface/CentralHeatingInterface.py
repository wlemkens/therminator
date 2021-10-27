from .HeatingInterface import HeatingInterface

class CentralHeatingInterface(HeatingInterface):
    def __init__(self, name, config):
        self.name = name

    def getTemperature(self):
        return None

    def setOutput(self, outputValue):
        pass
