from Scheduler.BasicScheduler import BasicScheduler
from Controller.ControllerFactory import ControllerFactory

from enum import Enum

class SchedulerType(Enum):
    BASICSCHEDULER = 0

class SchedulerFactory(object):
    def createScheduler(self, schedulerType, controllerType, parameters):
        controllerFactory = ControllerFactory()
        if schedulerType == SchedulerType.BASICSCHEDULER:
            scheduler = BasicScheduler(parameters)
            for zone in scheduler.getZoneNames():
                scheduler.addController(zone, controllerFactory.createController(controllerType))
            return scheduler
        else:
            raise ValueError("No scheduler of specified type")