# External imports
import json
import datetime
import time

# Project imports
from Scheduler.Scheduler import Scheduler

class Schedule():
    def __init__(self, schedule):
        self.schedule = schedule

    def getNextChange(self):
        pass

    def getCurrentSetpointTemperature(self, room):
        dayOfWeek = datetime.datetime.today().weekday()
        now = datetime.datetime.now()
        minutes = now.hour * 60 + now.minute
        dayType = self.schedule["weekschedule"][dayOfWeek]
        timeTable = self.schedule["daytypes"][dayType]
        mode = "none"
        for i in range(len(timeTable)):
            if (timeTable[i]["start"] > minutes):
                mode = timeTable[i-1]["mode"]
        temperatures = self.schedule["modes"][mode]["zones"]
        return temperatures[room]

    def zoneCount(self):
        return len(self.schedule["modes"][0]["zones"])

    def getZoneNames(self):
        modes = list(self.schedule["modes"].keys())
        return self.schedule["modes"][modes[0]]["zones"].keys()

class BasicScheduler(Scheduler):
    def __init__(self, filename):
        super(BasicScheduler,self).__init__()
        self.schedule = None
        self.controller = {}
        self.loadConfig(filename)

    def loadConfig(self, filename):
        with open(filename) as f:
            self.schedule = Schedule(json.load(f))

    def run(self):
        print("Run start")
        while True:
            self.nextCallTime += self.interval
            rooms = ["living", "bathroom", "bedroom"]
            for room in rooms:
                for controller in self.controller[room]:
                    output = controller.setSetpoint(self.schedule.getCurrentSetpointTemperature(room) )
                    print (room, output)
            time.sleep(self.nextCallTime - time.time())

    def zoneCount(self):
        return self.schedule.zoneCount()

    def getZoneNames(self):
        return self.schedule.getZoneNames()

    def addController(self, zoneName, controller):
        if (zoneName in self.controller):
            self.controller[zoneName] += [controller]
        else:
            self.controller[zoneName] = [controller]