from .CentralHeatingInterface import CentralHeatingInterface
from .RadiatorHeatingInterface import RadiatorHeatingInterface

from enum import Enum

class HeatingInterfaceType():
    CENTRALHEATINGINTERFACE = "central"
    RADIATORHEATINGINTERFACE = "radiator"

class HeatingInterfaceFactory(object):

    def __init__(self):
        pass

    def createHeatingInterface(self, names, type, zone, parameters = None):
        name = zone
        if name in names:
            baseName = name
            index = 1
            name = baseName + str(index)
            while name in names:
                index += 1
                name = baseName + str(index)
        names += [name]
        if type == HeatingInterfaceType.CENTRALHEATINGINTERFACE:
            return CentralHeatingInterface(name, parameters)
        elif type == HeatingInterfaceType.RADIATORHEATINGINTERFACE:
            return RadiatorHeatingInterface(name, parameters)
        else:
            raise ValueError("No heating interface of specified type", type, HeatingInterfaceType.RADIATORHEATINGINTERFACE)
