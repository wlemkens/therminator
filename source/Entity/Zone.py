import paho.mqtt.client as mqtt

import time

class Zone(object):
    def __init__(self, config, mqttConfig, on_update):
        self.setpointOFF = 15.0
        self.temperature = None
        self.setpoint = None
        self.stored_setpoint = self.setpointOFF
        self.level = None
        self.enabled = True
        self.name = config["id"]
        self.label = config["label"]
        self.topicTemp = "therminator/in/{:}_temperature".format(self.name)
        self.topicSP = "therminator/in/{:}_setpoint".format(self.name)
        self.topicLvl = "therminator/in/{:}_level".format(self.name)
        self.topicEnabled = "therminator/in/{:}_enabled".format(self.name)
        self.icon = config["icon"]
        self.connect(mqttConfig)
        self.on_update = on_update

    def setSetpoint(self, setpoint):
        topic = "therminator/out/{:}_setpoint".format(self.name)
        self.client.publish(topic, setpoint)

    def storeSetpoint(self, setpoint):
        topic = "therminator/out/{:}_stored_setpoint".format(self.name)
        self.stored_setpoint = self.setpoint
        self.client.publish(topic, setpoint)

    def setStatus(self, status):
        if status:
            self.setSetpoint(self.stored_setpoint)
        else:
            self.storingSetpoint = True
            self.storeSetpoint(self.setpoint)
            self.setSetpoint(self.setpointOFF)
            time.sleep(5)
            self.storingSetpoint = False

    def on_message(self, client, userdata, message):
        if message.topic == self.topicTemp:
            self.temperature = float(message.payload)
        elif message.topic == self.topicSP:
            if self.enabled:
                self.setpoint = float(message.payload)
            else:
                if not self.storingSetpoint:
                    self.storeSetpoint(float(message.payload))
        elif message.topic == self.topicLvl:
            self.level = float(message.payload)
        elif message.topic == self.topicEnabled:
            self.enabled = float(message.payload)
            self.setStatus(self.enabled)
        self.update()

    def requestValues(self):
        topic = "therminator/request"
        requestMessageTemp = "\"{:}_temperature\"".format(self.name)
        requestMessageSP = "\"{:}_setpoint\"".format(self.name)
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
