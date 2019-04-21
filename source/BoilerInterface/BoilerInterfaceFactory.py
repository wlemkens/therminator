from BoilerInterface.MQTTBoilerInterface import MQTTBoilerInterface

from enum import Enum

class BoilerInterfaceType():
    MQTTBOILERINTERFACE = "mqtt"

class BoilerInterfaceFactory(object):
    def createBoilerInterface(self, type, parameters = None):
        if type == BoilerInterfaceType.MQTTBOILERINTERFACE:
            return MQTTBoilerInterface(parameters)
        else:
            raise ValueError("No boiler interface of specified type", type)