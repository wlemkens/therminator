
class Setup(object):
    def __init__(self, setup):
        self.setup = setup

    def zoneCount(self):
        return len(self.setup["zones"])

    def getZoneNames(self):
        zones = list(self.setup["zones"].keys())
        return zones

    def getZoneTypes(self, zoneName):
        return self.setup["zones"][zoneName]
