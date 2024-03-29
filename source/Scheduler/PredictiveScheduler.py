#!/usr/bin/python
# -*- coding: UTF-8 -*-

# External imports
import json
import datetime
import time

# Project imports
from .Scheduler import Scheduler
from .BasicScheduler import Schedule
from .heating_coefficient import *
import logging

class PredictiveScheduler(Scheduler):
    def __init__(self, filename):
        super(PredictiveScheduler,self).__init__()
        self.schedule = None
        self.mode = None
        self.controller = {}
        self.boilerInterface = None
        self.loadConfig(filename)
        self.h = None
        self.h_loss = None
        self.loadLog(self.logDirectory)
        self.nbSimSteps = 10
        logging.debug("Using predictive scheduler")

    def loadLog(self, directory):
        self.h, self.h_loss = calculateCoefficientsFromBestLog(directory)

    def loadConfig(self, filename):
        with open(filename) as f:
            self.schedule = Schedule(json.load(f))
            daytypes = self.schedule.schedule["daytypes"]
            self.logDirectory = self.schedule.schedule["log_directory"]
            for typename, daytype in daytypes.items():
                for period in daytype:
                    if ":" in str(period["start"]):
                        start = period["start"]
                        time = datetime.datetime.strptime(start, "%H:%M")
                        period["start"] = time.hour * 60 + time.minute
#                        print("{:} -> {:}".format(start, period["start"]))

    def run(self):
        while True:
            self.nextCallTime += self.interval
            rooms = self.schedule.getZoneNames()
            total = 0
            for room in rooms:
                for controller in self.controller[room]:
                    spTime, nextSetpointTemperature = self.schedule.getNextChange(room)
                    temperature = controller.getTemperature()
                    currentSP = controller.getStoredSetpoint()
                    hasChanged = self.schedule.hasSetpointChanged(room)
                    scheduledSP = self.schedule.getCurrentSetpointTemperature(room)
                    #TMP debugging
                    externalTemperature = self.exterior.getTemperature()
                    if externalTemperature != None and temperature != None:
                        futureTemp = simulateFutureTemperature(spTime, nextSetpointTemperature, temperature, externalTemperature, self.h_loss[room], self.h[room], self.nbSimSteps)
                        logging.debug(">Future temperature for {:} is {:}°C".format(room, futureTemp))

                    if ((currentSP != None and nextSetpointTemperature > currentSP and temperature != None) or hasChanged):
                        if hasChanged:
                            controller.setSetpoint(scheduledSP)
                        else:
                            externalTemperature = self.exterior.getTemperature()
                            if externalTemperature != None:
                                forFutureSP = calculateSetpoint(spTime, nextSetpointTemperature, temperature, externalTemperature, self.h_loss[room], self.h[room])
                                logging.debug("Minimum required temperature for {:} is {:}°C".format(room, forFutureSP))
                                if (forFutureSP > currentSP and currentSP < nextSetpointTemperature):
                                    controller.setSetpoint(nextSetpointTemperature)
                        mode = self.schedule.getMode()
                        if mode != self.mode:
                            self.mode = mode
                            self.boilerInterface.setMode(mode)

                    if controller.isEnabled():
                        output = controller.getOutput()
                        total += max(0,output)
                        logging.debug ("Room '{:}' {:}/{:}°C output = {:}".format(room, controller.getTemperature(), controller.getSetpoint(), output))
                    else:
                        logging.debug ("Room '{:}' {:}/{:}°C disabled".format(room, controller.getTemperature(), controller.getSetpoint()))

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

    def addExterior(self, exterior):
        self.exterior = exterior
