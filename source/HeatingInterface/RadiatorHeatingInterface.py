import datetime
import time
import threading

from HeatingInterface.HeatingInterface import HeatingInterface
from MQTT.MqttProvider import MqttProvider

class RadiatorHeatingInterface(HeatingInterface):
    def __init__(self, name, config):
        print("Loading radiator heating interface '{:}'".format(name));
        self.setpointOFF = 10.0
        self.setpointDelay = 30
        self.address  = config["address"]
        self.port = config["port"]
        self.name = name
        self.volotileStatus = False
        self.stored_setpoint = self.setpointOFF
        self.storingTime = datetime.datetime.now()
        self.storingTimeout = self.setpointDelay + 30
        self.statusChangeThread = threading.Thread(target=self.statusChangeFunction)
        self.statusChangeDelay = 30
        if "username" in config.keys() and "password" in config.keys():
            self.username = config["username"]
            self.password = config["password"]
        else:
            self.username = None
            self.password = None
        self.temperature = None
        self.setpoint = None
        self.enabled = True
        self.client = MqttProvider(self.address, self.port)
        self.connect()
        self.statusChangedTime = datetime.datetime.now()
        self.statusChangeThread.start()

    def storeSetpoint(self, setpoint):
        if self.enabled or setpoint != self.setpointOFF:
            print(datetime.datetime.now())
            print("Storing setpoint {:} (was {:})".format(setpoint, self.stored_setpoint))
            topic = "therminator/out/{:}_stored_setpoint".format(self.name)
            topicIn = "therminator/in/{:}_stored_setpoint".format(self.name)
            self.stored_setpoint = setpoint
            self.client.publish(topic, setpoint)
            self.client.publish(topicIn, setpoint)
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

    def getStoredSetpoint(self):
        return self.stored_setpoint

    def setSetpoint(self, setpoint):
        print(datetime.datetime.now())
        print("Publishing setpoint {:} from {:} to {:}".format(setpoint, self.setpoint, setpoint))
        self.client.publish("therminator/out/{:}_setpoint".format(self.name), setpoint)
        self.setpoint = setpoint

    def setOutput(self, outputValue):
        pass

    def statusChangeFunction(self):
        while True:
            if (datetime.datetime.now() - self.statusChangedTime).total_seconds() > self.statusChangeDelay and self.volotileStatus != self.enabled:
                self.enabled = self.volotileStatus
                self.setStatus(self.enabled)
            time.sleep(2)
            print("Checking if status has change for {:}".format(self.name))


    def on_message(self, client, userdata, message):
        print(datetime.datetime.now())
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
            self.statusChangedTime = datetime.datetime.now()
            self.volotileStatus = int(message.payload) == 1
        print("enabled",self.enabled)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print ("subd")

    def on_connect(self, client, userdata, flags, rc):
        print(datetime.datetime.now())
        print ("Connected")

    def requestValues(self):
        topic = "therminator/request"
        requestMessageTemp = "\"{:}_temperature\"".format(self.name)
        requestMessageSP = "\"{:}_setpoint\"".format(self.name)
        requestMessageEnabled = "\"{:}_enabled\"".format(self.name)
        self.client.publish(topic, requestMessageTemp)
        self.client.publish(topic, requestMessageSP)
        self.client.publish(topic, requestMessageEnabled)

    def connect(self):
        self.topic_temp = "therminator/in/{:}_temperature".format(self.name)
        self.topic_sp = "therminator/in/{:}_setpoint".format(self.name)
        self.topic_enabled = "therminator/in/{:}_enabled".format(self.name)
        topics = [(self.topic_temp, 1), (self.topic_sp, 1),(self.topic_enabled,1)]
        self.client.subscribe(self, topics)
        self.requestValues()

    def isEnabled(self):
        return self.enabled
