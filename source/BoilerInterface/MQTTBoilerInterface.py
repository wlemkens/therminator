from BoilerInterface.BoilerInterface import BoilerInterface
from Controller.PID import PID
from MQTT.MqttProvider import MqttProvider

import json
import logging

class MQTTBoilerInterface(BoilerInterface):

    def __init__(self, configFilename):
        config = None
        with open(configFilename) as f:
            config = json.load(f)
        logging.debug(config)
        self.address  = config["address"]
        self.port = config["port"]
        if "username" in config.keys() and "password" in config.keys():
            self.username = config["username"]
            self.password = config["password"]
        else:
            self.username = None
            self.password = None
        self.returnTemperature = 0
        self.waterTemperature = 0
        self.gain = config["gain"]
        pidParmaeters = config["pid"]
        self.PID = PID(pidParmaeters["p"], pidParmaeters["i"], pidParmaeters["d"],pidParmaeters["errorSumLimit"],pidParmaeters["historyRange"])
        logFile = "/var/log/thermostat.log"
        self.client = MqttProvider(self.address, self.port, logFile, "Boiler")
        self.client.publish("therminator/out/boiler_output", 1)
        logging.debug("Boiler connected to MQTT at '{:}'".format(self.address))


    def setOutput(self, outputValue):
        outputValue *= self.gain
        outputValue = min(100,max(0, outputValue))
        logging.debug("Outputing '{:}'".format(outputValue))
        self.client.publish("therminator/out/boiler_output", float(outputValue))

    def setMode(self, mode):
        logging.debug("Switching to mode '{:}'".format(mode))
        self.client.publish("therminator/out/mode", mode)
        self.client.publish("therminator/in/mode", mode)

