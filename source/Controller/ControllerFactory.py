from Controller.PIDController import PIDController
from HeatingInterface.HeatingInterfaceFactory import HeatingInterfaceFactory

from enum import Enum

class ControllerType(Enum):
    PIDCONTROLLER = 0

class ControllerFactory(object):
    def createController(self, type, interfaceType, parameters = None):
        interfaceFactory = HeatingInterfaceFactory()
        interface = interfaceFactory.createHeatingInterface(interfaceType)
        if type == ControllerType.PIDCONTROLLER:
            return PIDController(interface)
        else:
            raise ValueError("No controller of specified type")