import datetime
import time
import threading

from HeatingInterface.HeatingInterface import HeatingInterface
from MQTT.MqttProvider import MqttProvider
import logging

class RadiatorHeatingInterface(HeatingInterface):
    def __init__(self, name, config):
        logging.basicConfig(filename='/var/log/thermostat.log', level=logging.DEBUG)
        logging.debug("Loading radiator heating interface '{:}'".format(name));
        self.address  = config["address"]
        self.port = config["port"]
        self.name = name
        if "username" in config.keys() and "password" in config.keys():
            self.username = config["username"]
            self.password = config["password"]
        else:
            self.username = None
            self.password = None
        self.temperature = None
        self.setpoint = None
        self.client = MqttProvider(self.address, self.port)
        self.connect()

    def getTemperature(self):
        return self.temperature

    def getSetpoint(self):
        return self.setpoint

    def setSetpoint(self, setpoint):
        self.client.publish("therminator/out/{:}_setpoint".format(self.name), setpoint)
        self.setpoint = setpoint

    def setOutput(self, outputValue):
        pass

    def on_message(self, client, userdata, message):
        if message.topic == self.topic_temp:
            self.temperature = float(message.payload)
        elif message.topic == self.topic_sp:
            self.setpoint = float(message.payload)

    def requestValues(self):
        topic = "therminator/request"
        requestMessageTemp = "\"{:}_temperature\"".format(self.name)
        requestMessageSP = "\"{:}_stored_setpoint\"".format(self.name)
        self.client.publish(topic, requestMessageTemp)
        self.client.publish(topic, requestMessageSP)

    def connect(self):
        self.topic_temp = "therminator/in/{:}_temperature".format(self.name)
        self.topic_sp = "therminator/in/{:}_stored_setpoint".format(self.name)
        topics = [(self.topic_temp, 2), (self.topic_sp, 2)]
        self.client.subscribe(self, topics)
        self.requestValues()
