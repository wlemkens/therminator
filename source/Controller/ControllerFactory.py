from Controller.PIDController import PIDController

from enum import Enum

class ControllerType(Enum):
    PIDCONTROLLER = 0

class ControllerFactory(object):
    def createController(self, type, parameters = None):
        if type == ControllerType.PIDCONTROLLER:
            return PIDController()
        else:
            raise ValueError("No controller of specified type")