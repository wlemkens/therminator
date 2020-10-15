# External imports
import json
import datetime
import time

# Project imports
from Scheduler.Scheduler import Scheduler

class Schedule():
    def __init__(self, schedule):
        self.schedule = schedule
        self.setpoints = {}
        self.mode = None

    def hasSetpointChanged(self, room):
        if not room in self.setpoints.keys():
            #print("Setpoint not present")
            return True
        #print("Current setpoint {:}, should be {:}".format(self.setpoints[room], self._currentSetpointTemperature_(room)))
        return self.setpoints[room] != self._currentSetpointTemperature_(room)

    def getNextChange(self, room):
        dayOfWeek = datetime.datetime.today().weekday()
        now = datetime.datetime.now()
        minutes = now.hour * 60 + now.minute
        dayType = self.schedule["weekschedule"][dayOfWeek]
        timeTable = self.schedule["daytypes"][dayType]
        for i in range(len(timeTable)):
            if (timeTable[i]["start"] > minutes):
                currentMode = timeTable[i-1]["mode"]
                currentTemperature = self.schedule["modes"][currentMode]["zones"][room]
                mode = timeTable[i]["mode"]
                temperature = self.schedule["modes"][mode]["zones"][room]
                if currentTemperature != temperature:
                    return timeTable[i]["start"] * 60, temperature
        mode = timeTable[-1]["mode"]
        temperature = self.schedule["modes"][mode]["zones"][room]
        return timeTable[-1]["start"] * 60, temperature


    def _currentSetpointTemperature_(self, room):
        dayOfWeek = datetime.datetime.today().weekday()
        now = datetime.datetime.now()
        minutes = now.hour * 60 + now.minute
        dayType = self.schedule["weekschedule"][dayOfWeek]
        timeTable = self.schedule["daytypes"][dayType]
        mode = "none"
        for i in range(len(timeTable)):
            if (timeTable[i]["start"] > minutes):
                mode = timeTable[i-1]["mode"]
                break
        if mode == "none":
            mode = timeTable[-1]["mode"]
        self.mode = mode
        temperatures = self.schedule["modes"][mode]["zones"]
        return temperatures[room]

    def getCurrentSetpointTemperature(self, room):
        self.setpoints[room] = self._currentSetpointTemperature_(room)
        return self.setpoints[room]


    def zoneCount(self):
        return len(self.schedule["modes"][0]["zones"])

    def getZoneNames(self):
        modes = list(self.schedule["modes"].keys())
        return self.schedule["modes"][modes[0]]["zones"].keys()

    def getMode(self):
        return self.mode

class BasicScheduler(Scheduler):
    def __init__(self, schedule, modes, dayttypes):
        super(BasicScheduler,self).__init__()
        self.schedule = None
        self.mode = None
        self.controller = {}
        self.boilerInterface = None
        self.loadConfig(schedule, modes, dayttypes)

    def loadConfig(self, schedule, modes, daytypes):
            self.schedule = Schedule({"weekschedule" : schedule,
                             "modes": modes,
                             "daytypes": daytypes})
            daytypes = daytypes
            for typename, daytype in daytypes.items():
                for period in daytype:
                    if ":" in str(period["start"]):
                        start = period["start"]
                        time = datetime.datetime.strptime(start, "%H:%M")
                        period["start"] = time.hour * 60 + time.minute
            self.mode = None

    def run(self):
        while True:
            self.nextCallTime += self.interval
            rooms = self.schedule.getZoneNames()
            total = 0
            mode = self.schedule.getMode()
            if mode != self.mode:
                self.mode = mode
                self.boilerInterface.setMode(mode)
            for room in rooms:
                for controller in self.controller[room]:
                    if (self.schedule.hasSetpointChanged(room)):
                        print("Setpoint has changed for room '{:}' to {:}".format(room, self.schedule.getCurrentSetpointTemperature(room)))
                        controller.setSetpoint(self.schedule.getCurrentSetpointTemperature(room) )
                    output = controller.getOutput()
                    total += max(0,output)
                    print ("Room '{:}' {:}/{:}°C output = {:}".format(room, controller.getTemperature(), controller.getSetpoint(), output))

            #            print(self.schedule.schedule)
            self.boilerInterface.setOutput(total)
            sleepTime = self.nextCallTime - time.time()
            if (sleepTime > 0):
                time.sleep(sleepTime)

    def zoneCount(self):
        return self.schedule.zoneCount()

    def getZoneNames(self):
        return self.schedule.getZoneNames()

    def addController(self, zoneName, controller):
        if (zoneName in self.controller):
            self.controller[zoneName] += [controller]
        else:
            self.controller[zoneName] = [controller]

    def addBoilerController(self, controller):
        self.boilerInterface = controller
