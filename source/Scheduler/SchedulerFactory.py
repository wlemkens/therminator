from Scheduler.BasicScheduler import BasicScheduler
from Controller.ControllerFactory import ControllerFactory
from Setup import Setup

from enum import Enum
import json

class SchedulerType(Enum):
    BASICSCHEDULER = 0

class SchedulerFactory(object):
    def loadSetup(self, filename):
        with open(filename) as f:
            return Setup(json.load(f))

    def createScheduler(self, schedulerType, controllerType, setupFile, parameters):
        controllerFactory = ControllerFactory()
        setup = self.loadSetup(setupFile)
        if schedulerType == SchedulerType.BASICSCHEDULER:
            scheduler = BasicScheduler(parameters)
            for zone in setup.getZoneNames():
                for zoneType in setup.getZoneTypes(zone):
                    scheduler.addController(zone, controllerFactory.createController(controllerType, zoneType))
            return scheduler
        else:
            raise ValueError("No scheduler of specified type")