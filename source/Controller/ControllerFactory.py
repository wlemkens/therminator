from .PIDController import PIDController
from HeatingInterface.HeatingInterfaceFactory import HeatingInterfaceFactory

import json

class ControllerType(object):
    PIDCONTROLLER = "pid"

class ControllerFactory(object):

    def createController(self, names, controllerMeta, zone, interfaceType, parameters = None):
        interfaceFactory = HeatingInterfaceFactory()
        config = {}
        with open(controllerMeta["configFile"]) as f:
            config = json.load(f)
        interface = interfaceFactory.createHeatingInterface(names, interfaceType, zone, config)
        if controllerMeta["type"] == ControllerType.PIDCONTROLLER:
            return PIDController(interface, config, zone)
        else:
            raise ValueError("No controller of specified type")
