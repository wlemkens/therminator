from .BasicScheduler import BasicScheduler
from .PredictiveScheduler import PredictiveScheduler
from Controller.ControllerFactory import ControllerFactory
from BoilerInterface.BoilerInterfaceFactory import BoilerInterfaceFactory
from Entity.Exterior import Exterior
from Setup import Setup

from enum import Enum
import json

class SchedulerType(object):
    BASICSCHEDULER = "basic"
    PREDICTIVESCHEDULER = "predictive"

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
        mqttFile = config["mqtt"]["configFile"]
        return self.setupScheduler(schedulerType, controllerTypes, setupFile, schedulerConfig, boilerType, boilerConfig,mqttFile)

    def setupScheduler(self, schedulerType, controllerTypes, setupFile, schedule, modes, daytypes, boilerType, boilerConfig, mqttFile):
        controllerFactory = ControllerFactory()
        boilerFactory = BoilerInterfaceFactory()
        setup = self.loadSetup(setupFile)
        if schedulerType == SchedulerType.BASICSCHEDULER:
            scheduler = BasicScheduler(schedule, modes, daytypes)
            for zone in setup.getZoneNames():
                controllerMeta = controllerTypes["default"]
                if zone in controllerTypes:
                    controllerMeta = controllerTypes[zone]

                for zoneType in setup.getZoneTypes(zone):
                    scheduler.addController(zone, controllerFactory.createController(scheduler.sensorNames, controllerMeta, zone, zoneType))
            scheduler.addBoilerController(boilerFactory.createBoilerInterface(boilerType, boilerConfig))
            return scheduler
        elif schedulerType == SchedulerType.PREDICTIVESCHEDULER:
            scheduler = PredictiveScheduler(schedule, modes, daytypes)
            for zone in setup.getZoneNames():
                controllerMeta = controllerTypes["default"]
                if zone in controllerTypes:
                    controllerMeta = controllerTypes[zone]

                for zoneType in setup.getZoneTypes(zone):
                    scheduler.addController(zone, controllerFactory.createController(scheduler.sensorNames, controllerMeta, zone, zoneType))
            scheduler.addBoilerController(boilerFactory.createBoilerInterface(boilerType, boilerConfig))
            with open(mqttFile) as f:
                mqttConfig = json.load(f)
                scheduler.addExterior(Exterior(mqttConfig, None))
            return scheduler
        else:
            raise ValueError("No scheduler of specified type")
