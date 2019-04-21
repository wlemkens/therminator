from Scheduler.BasicScheduler import BasicScheduler
from Controller.ControllerFactory import ControllerFactory
from BoilerInterface.BoilerInterfaceFactory import BoilerInterfaceFactory
from Setup import Setup

from enum import Enum
import json

class SchedulerType(object):
    BASICSCHEDULER = "basic"

class SchedulerFactory(object):
    def loadSetup(self, filename):
        with open(filename) as f:
            return Setup(json.load(f))

    def createScheduler(self, config):
        schedulerType = config["scheduler"]["type"]
        controllerTypes = config["controllers"]
        setupFile = config["setup"]["configFile"]
        schedulerConfig = config["scheduler"]["configFile"]
        boilerType = config["boiler_controller"]["type"]
        boilerConfig = config["boiler_controller"]["configFile"]
        return self.setupScheduler(schedulerType, controllerTypes, setupFile, schedulerConfig, boilerType, boilerConfig)

    def setupScheduler(self, schedulerType, controllerTypes, setupFile, parameters, boilerType, boilerConfig):
        controllerFactory = ControllerFactory()
        boilerFactory = BoilerInterfaceFactory()
        setup = self.loadSetup(setupFile)
        if schedulerType == SchedulerType.BASICSCHEDULER:
            scheduler = BasicScheduler(parameters)
            for zone in setup.getZoneNames():
                controllerMeta = controllerTypes["default"]
                if zone in controllerTypes:
                    controllerMeta = controllerTypes[zone]

                for zoneType in setup.getZoneTypes(zone):
                    scheduler.addController(zone, controllerFactory.createController(controllerMeta, zone, zoneType))
            scheduler.addBoilerController(boilerFactory.createBoilerInterface(boilerType, boilerConfig))
            return scheduler
        else:
            raise ValueError("No scheduler of specified type")