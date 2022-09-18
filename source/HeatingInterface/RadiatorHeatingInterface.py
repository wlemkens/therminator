import datetime
import time
import threading

from .HeatingInterface import HeatingInterface
from MQTT.MqttProvider import MqttProvider
import logging

class RadiatorHeatingInterface(HeatingInterface):
    def __init__(self, name, config):
        logFile = '/var/log/thermostat.log'
        logging.basicConfig(filename=logFile, level=logging.DEBUG)
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
        self.enabled = False
        self.client = MqttProvider(self.address, self.port, logFile)
        self.connect()

    def getTemperature(self):
        return self.temperature

    def getSetpoint(self):
        return self.setpoint

    def getEnabled(self):
        #logging.debug("Radiator heating interface '{:}' enabled = {:}".format(self.name, self.enabled));
        return self.enabled

    def setSetpoint(self, setpoint):
        if self.setpoint != setpoint:
            self.client.publish("therminator/out/{:}_setpoint".format(self.name), setpoint)
            self.setpoint = setpoint

    def setOutput(self, outputValue):
        pass

    def on_message(self, client, userdata, message):
        topic = "Invalid"
        value = "Invalid"
        try:
            topic = message.topic
            value = message.payload
            if message.topic == self.topic_temp:
                logging.debug("{:} : Received message {:} on topic {:}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message.topic, message.payload))
                self.temperature = float(message.payload)
            elif message.topic == self.topic_sp:
                logging.debug("{:} : Received message {:} on topic {:}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message.topic, message.payload))
                self.setpoint = float(message.payload)
            elif message.topic == self.topic_enabled:
                logging.debug("{:} : Received message {:} on topic {:}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message.topic, message.payload))
                self.enabled = int(message.payload)
        except Exception as e:
            logging.error("{:} : topic : {:}, value = {:}, Error {:}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), topic, value, e))

    def requestValues(self):
        topic = "therminator/request"
        requestMessageTemp = "\"{:}_temperature\"".format(self.name)
        requestMessageEnabled = "\"{:}_enabled\"".format(self.name)
        requestMessageSP = "\"{:}_setpoint\"".format(self.name)
        self.client.publish(topic, requestMessageTemp)
        self.client.publish(topic, requestMessageEnabled)
        self.client.publish(topic, requestMessageSP)

    def connect(self):
        self.topic_temp = "therminator/in/{:}_temperature".format(self.name)
        self.topic_enabled = "therminator/in/{:}_enabled".format(self.name)
        self.topic_sp = "therminator/in/{:}_setpoint".format(self.name)
        topics = [(self.topic_temp, 2), (self.topic_sp, 2), (self.topic_enabled, 2)]
        self.client.subscribe(self, topics)
        self.requestValues()
