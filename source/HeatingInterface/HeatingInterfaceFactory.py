from HeatingInterface.CentralHeatingInterface import CentralHeatingInterface
from HeatingInterface.RadiatorHeatingInterface import RadiatorHeatingInterface

from enum import Enum

class HeatingInterfaceType():
    CENTRALHEATINGINTERFACE = "central"
    RADIATORHEATINGINTERFACE = "radiator"

class HeatingInterfaceFactory(object):
    def createHeatingInterface(self, type, parameters = None):
        if type == HeatingInterfaceType.CENTRALHEATINGINTERFACE:
            return CentralHeatingInterface()
        elif type == HeatingInterfaceType.RADIATORHEATINGINTERFACE:
            return RadiatorHeatingInterface()
        else:
            raise ValueError("No heating interface of specified type", type, HeatingInterfaceType.RADIATORHEATINGINTERFACE)