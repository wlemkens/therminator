import paho.mqtt.subscribe as subscribe
import paho.mqtt.client as mqtt

import datetime
import time

from HeatingInterface.HeatingInterface import HeatingInterface

class RadiatorHeatingInterface(HeatingInterface):
    def __init__(self, name, config):
        self.setpointOFF = 15.0
        self.setpointDelay = 30
        self.address  = config["address"]
        self.port = config["port"]
        self.name = name
        self.stored_setpoint = self.setpointOFF
        self.storingTime = datetime.datetime.now()
        self.storingTimeout = self.setpointDelay + 30
        if "username" in config.keys() and "password" in config.keys():
            self.username = config["username"]
            self.password = config["password"]
        else:
            self.username = None
            self.password = None
        self.temperature = None
        self.setpoint = None
        self.enabled = True
        self.client = mqtt.Client()
        self.connect(self.address, self.port, self.username, self.password)

    def storeSetpoint(self, setpoint):
        if self.enabled or setpoint != self.setpointOFF:
            print("Storing setpoint {:}".format(setpoint))
            topic = "therminator/out/{:}_stored_setpoint".format(self.name)
            self.stored_setpoint = setpoint
            self.client.publish(topic, setpoint)
            if not self.enabled:
                self.setSetpoint(self.setpointOFF)
        else:
            print("Skipping setpoint {:}".format(setpoint))

    def setStatus(self, status):
        if status:
            self.setSetpoint(self.stored_setpoint)
        else:
            self.setSetpoint(self.setpointOFF)

    def getTemperature(self):
        return self.temperature

    def getSetpoint(self):
        return self.setpoint

    def setSetpoint(self, setpoint):
        print("Publishing setpoint {:}".format(setpoint))
        self.client.publish("therminator/out/{:}_setpoint".format(self.name), setpoint)
        self.setpoint = setpoint

    def setOutput(self, outputValue):
        pass

    def on_message(self, client, userdata, message):
        print("Received {:} : {:}".format(message.topic, message.payload))
        if message.topic == self.topic_temp:
            self.temperature = float(message.payload)
        elif message.topic == self.topic_sp:
            if self.enabled:
                self.setpoint = float(message.payload)
                self.storeSetpoint(float(message.payload))
            else:
                self.storeSetpoint(float(message.payload))

        elif message.topic == self.topic_enabled:
            enabled = int(message.payload) == 1
            if self.enabled != enabled:
                self.enabled = enabled
                self.setStatus(self.enabled)
        print("enabled",self.enabled)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print ("subd")

    def on_connect(self, client, userdata, flags, rc):
        print ("Connected")

    def requestValues(self):
        topic = "therminator/request"
        requestMessageTemp = "\"{:}_temperature\"".format(self.name)
        requestMessageSP = "\"{:}_setpoint\"".format(self.name)
        requestMessageEnabled = "\"{:}_enabled\"".format(self.name)
        self.client.publish(topic, requestMessageTemp)
        self.client.publish(topic, requestMessageSP)
        self.client.publish(topic, requestMessageEnabled)

    def connect(self, address, port, username, password):
        #self.client.connect(address, port, 60)
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        self.topic_temp = "therminator/in/{:}_temperature".format(self.name)
        self.topic_sp = "therminator/in/{:}_setpoint".format(self.name)
        self.topic_enabled = "therminator/in/{:}_enabled".format(self.name)
        topics = [(self.topic_temp, 1), (self.topic_sp, 1),(self.topic_enabled,1)]
        print("Subscribing to topics '{:}'".format(topics))
        self.client.on_message = self.on_message
        self.client.connect(address, port, 60)
        self.client.loop_start()
        r = self.client.subscribe(topics)
        self.requestValues()
        #self.client.loop_forever()

    def isEnabled(self):
        return self.enabled
