import paho.mqtt.client as mqtt
import threading

import time

class Zone(object):
    def __init__(self, config, mqttConfig, on_update):
        self.offTemperature = 10
        self.offDelay = 10
        self.temperature = None
        self.setpoint = None
        self.level = None
        self.enabled = True
        self.name = config["id"]
        self.label = config["label"]
        self.topicTemp = "therminator/in/{:}_temperature".format(self.name)
        self.topicSP = "therminator/in/{:}_stored_setpoint".format(self.name)
        self.topicLvl = "therminator/in/{:}_level".format(self.name)
        self.topicEnabled = "therminator/in/{:}_enabled".format(self.name)
        self.icon = config["icon"]
        self.connect(mqttConfig)
        self.on_update = on_update
        self.tempEnabled = True
        self.enabledCheckThread = None

    def enabledCheck(self):
        print("Checking if {:} is enabled".format(self.name))
        if self.enabled != self.tempEnabled:
            print("Enabled status changed from  {:} to {:}".format(self.enabled, self.tempEnabled))
            self.enabled = self.tempEnabled
            self.update()

    def on_message(self, client, userdata, message):
        changed = False
        if message.topic == self.topicTemp:
            if self.temperature != float(message.payload):
                self.temperature = float(message.payload)
                self.update()
        elif message.topic == self.topicSP:
            if self.setpoint != float(message.payload):
                self.setpoint = float(message.payload)
                self.update()
        elif message.topic == self.topicLvl:
            if self.level != float(message.payload):
                self.level = float(message.payload)
                #self.update()
        elif message.topic == self.topicEnabled:
            self.tempEnabled = int((message.payload))
            if self.enabledCheckThread:
                self.enabledCheckThread.cancel()
            self.enabledCheckThread = threading.Timer(self.offDelay, self.enabledCheck)
            self.enabledCheckThread.start()

    def requestValues(self):
        topic = "therminator/request"
        requestMessageTemp = "\"{:}_temperature\"".format(self.name)
        requestMessageSP = "\"{:}_stored_setpoint\"".format(self.name)
        requestMessageLvl = "\"{:}_level\"".format(self.name)
        requestMessageEnabled = "\"{:}_enabled\"".format(self.name)
        self.client.publish(topic, requestMessageTemp)
        self.client.publish(topic, requestMessageSP)
        self.client.publish(topic, requestMessageLvl)
        self.client.publish(topic, requestMessageEnabled)

    def connect(self, mqttConfig):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(mqttConfig["address"], mqttConfig["port"], 60)
        self.client.loop_start()
        topics = [(self.topicTemp, 1), (self.topicSP, 1), (self.topicLvl, 1), (self.topicEnabled, 1)]
        self.client.loop_start()
        r = self.client.subscribe(topics)
        self.requestValues()

    def getTemperature(self):
        return self.temperature

    def getSetpoint(self):
        return self.setpoint

    def getName(self):
        return self.name

    def getLabel(self):
        return self.label

    def isEnabled(self):
        return self.enabled

    def update(self):
        self.on_update()

    def getLevel(self):
        return self.level
