import json
import threading
from datetime import datetime, timedelta
import signal
import time

from MQTT.MqttProvider import MqttProvider

from Heartbeat.Modules import Modules
from Heartbeat.Watchdog import Watchdog


class Zone:
    def __init__(self, name, mqtt):
        self.name = name
        self.spTopicIn = "therminator/in/{:}_setpoint".format(name)
        self.statusTopicIn = "therminator/in/{:}_enabled".format(name)
        self.spTopicOut = "therminator/out/{:}_setpoint".format(name)
        self.storedSpTopicOut = "therminator/out/{:}_stored_setpoint".format(name)
        self.storedSpTopicIn = "therminator/in/{:}_stored_setpoint".format(name)
        self.heartbeatTopic = "therminator/heartbeat"
        self.heartbeatDependencies = []
        self.statusChangeThread = threading.Thread(target=self.statusChangeFunction, daemon=True)
        self.enabled = None
        self.volatileStatus = None
        self.setpoint = 0
        self.storedSetpoint = 0
        self.setpointOFF = 10
        self.statusChangeDelay = 60
        self.mqtt = mqtt
        self.statusChangedTime = datetime.now() - timedelta(0, 2*self.statusChangeDelay)
        self.subscribeToInputs()
        self.requestValues(name)
        self.statusChangeThread.start()

    def statusChangeFunction(self):
        while True:
            #print("statusChangeFunction({:})".format(self.name))
            if self.enabled == None or ((datetime.now() - self.statusChangedTime).total_seconds() > self.statusChangeDelay and self.volatileStatus != self.enabled):
                self.enabled = self.volatileStatus
                self.setStatus(self.enabled)
            time.sleep(2)

    def subscribeToInputs(self):
        self.mqtt.subscribe(self, (self.spTopicIn, 2))
        self.mqtt.subscribe(self, (self.statusTopicIn, 2))

    def requestValues(self, name):
        print("requestValues({:})".format(name))
        topic = "therminator/request"
        requestMessageSP = "\"{:}_setpoint\"".format(name)
        requestMessageEnabled = "\"{:}_enabled\"".format(name)
        self.mqtt.publish(topic, requestMessageEnabled)
        self.mqtt.publish(topic, requestMessageSP)

    def publishSetpoint(self, setpoint):
        print("publishSetpoint({:}) : {:}".format(setpoint, self.name))
        self.mqtt.publish(self.spTopicOut, setpoint)

    def storeSetpoint(self, setpoint):
        print("storeSetpoint({:}) : {:}".format(setpoint, self.name))
        if setpoint != self.setpointOFF:
            # Never store the off setpoint value since it might cause problems
            # when the order of messages is not kept
            self.storedSetpoint = setpoint
            print("Publishing store on in and out")
            self.mqtt.publish(self.storedSpTopicOut, setpoint)
            # This device does not trigger an domoticz/out event, so we need to create it ourselves
            self.mqtt.publish(self.storedSpTopicIn, setpoint)

    def setStatus(self, status):
        print("setStatus({:}) : {:}".format(status, self.name))
        if status:
            self.setAndPublishSetpoint(self.storedSetpoint)
        else:
            self.setAndPublishSetpoint(self.setpointOFF)

    def setAndPublishSetpoint(self, setpoint):
        print("setAndPublishSetpoint({:}) : {:}".format(setpoint, self.name))
        if self.setpoint != setpoint:
            self.setpoint = setpoint
            self.publishSetpoint(setpoint)

    def on_message(self, client, userdata, message):
        if (message.topic == self.spTopicIn):
            setpoint = float(message.payload)
            if setpoint != self.setpoint:
                if self.enabled:
                    print("Received setpoint {:} for enabled {:}".format(setpoint, self.name))
                    # If enabled, register the setpoint and forward it to the stored setpoint
                    self.setpoint = setpoint
                    self.storeSetpoint(setpoint)
                else:
                    print("Received setpoint {:} for disabled {:}".format(setpoint, self.name))
                    # If not enabled, only forward it to the stored setpoint and reset the setpoint to the off setpoint
                    self.storeSetpoint(setpoint)
                    self.publishSetpoint(self.setpointOFF)
        if (message.topic == self.statusTopicIn):
            self.statusChangedTime = datetime.now()
            self.volatileStatus = int(message.payload) == 1
            print("Received status change {:} for {:}".format(self.volatileStatus, self.name))

class Monitor:

    def __init__(self, configFilename):
        mqtt = {}
        setup = {}
        self.zones = []
        with open(configFilename) as f:
            config = json.load(f)
            with open(config["mqtt"]["configFile"]) as f2:
                mqtt = json.load(f2)
            with open(config["setup"]["configFile"]) as f2:
                setup = json.load(f2)
        self.mqtt = MqttProvider(mqtt["address"], mqtt["port"])
        self.loadZones(self.zones, setup, self.mqtt)
        self.watchdog = Watchdog(Modules.MONITOR, [Modules.CONNECTOR], config)
        signal.pause()
#        while True:
#            sleep(0.1)


    def loadZones(self, zones, config, mqtt):
            for zoneName in config["zones"].keys():
                if "radiator" in config["zones"][zoneName]:
                    zones += [Zone(zoneName, mqtt)]

