import threading

from MQTT.MqttProvider import MqttProvider
import logging
from datetime import datetime

class Zone(object):
    def __init__(self, config, mqttConfig, on_update, logFile, log_level = logging.WARNING):
        logging.basicConfig(filename=logFile, level=log_level)
        self.offTemperature = 10
        self.offDelay = 10
        self.temperature = None
        self.setpoint = None
        self.level = None
        self.enabled = True
        self.battery = None
        self.name = config["id"]
        self.label = config["label"]
        self.topicTemp = "therminator/in/{:}_temperature".format(self.name)
        self.topicSP = "therminator/in/{:}_setpoint".format(self.name)
        self.topicLvl = "therminator/in/{:}_level".format(self.name)
        self.topicEnabled = "therminator/in/{:}_enabled".format(self.name)
        self.topicBattery = "therminator/in/{:}_battery".format(self.name)
        self.icon = config["icon"]
        self.connect(mqttConfig, logFile)
        self.on_update = on_update
        self.tempEnabled = True
        self.enabledCheckThread = None

    def enabledCheck(self):
        logging.debug("Checking if {:} is enabled".format(self.name))
        if self.enabled != self.tempEnabled:
            logging.debug("{:} : Enabled status changed from  {:} to {:}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.enabled, self.tempEnabled))
            self.enabled = self.tempEnabled
            self.update()
        logging.debug("{:} : Checking {:} done".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.name))

    def on_message(self, client, userdata, message):
        changed = False
        if message.topic == self.topicTemp:
            if self.temperature != float(message.payload):
                self.temperature = float(message.payload)
                logging.debug("{:} : Temperature change detected {:}°C for {:}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.temperature, self.name))
                self.update()
        elif message.topic == self.topicSP:
            if self.setpoint != float(message.payload):
                self.setpoint = float(message.payload)
                logging.debug("{:} : Setpoint change detected {:}°C for {:}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.setpoint, self.name))
                self.update()
        elif message.topic == self.topicBattery:
            if self.battery != int(message.payload):
                self.battery = int(message.payload)
                logging.debug("{:} : Battery change detected {:}\% for {:}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.battery, self.name))
                self.update()
        elif message.topic == self.topicLvl:
            if self.level != float(message.payload):
                self.level = float(message.payload)
                logging.debug("{:} : Level change detected {:}\% for {:}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.level, self.name))
                #self.update()
        elif message.topic == self.topicEnabled:
            self.tempEnabled = int((message.payload))
            logging.debug("{:} : Status detected {:}\% for {:}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.tempEnabled, self.name))
            if self.enabledCheckThread:
                self.enabledCheckThread.cancel()
            self.enabledCheckThread = threading.Timer(self.offDelay, self.enabledCheck)
            self.enabledCheckThread.start()

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

    def connect(self, mqttConfig, logFile):
        self.client = MqttProvider(mqttConfig["address"], mqttConfig["port"], logFile)
        topics = [(self.topicTemp, 2), (self.topicSP, 2), (self.topicLvl, 2), (self.topicEnabled, 2), (self.topicBattery, 2)]
        self.client.subscribe(self, topics)
        self.requestValues()

    def getTemperature(self):
        return self.temperature

    def getSetpoint(self):
        return self.setpoint

    def getBattery(self):
        return self.battery

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
