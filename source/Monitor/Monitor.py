import json
import threading
from datetime import datetime, timedelta
import signal
import time

from MQTT.MqttProvider import MqttProvider

from Heartbeat.Modules import Modules
from Heartbeat.Watchdog import Watchdog

import logging


class Zone:
    def __init__(self, name, mqtt):
        logging.basicConfig(filename='/var/log/setpoint_monitor.log', level=logging.DEBUG)
        logging.debug("{:} Loading setpoint monitor zone".format(datetime.now().strftime("%H:%M:%S")))
        self.name = name
        self.spTopicIn = "therminator/in/{:}_setpoint".format(name)
        self.statusTopicIn = "therminator/in/{:}_enabled".format(name)
        self.spTopicOut = "therminator/out/{:}_setpoint".format(name)
        self.heatingTopicOut = "therminator/out/{:}_heating".format(name)
        self.statusChangeThread = threading.Thread(target=self.statusChangeFunction, daemon=True)
        self.enabled = None
        self.volatileStatus = None
        self.setpoint = 0
        self.statusChangeDelay = 60
        self.mqtt = mqtt
        self.statusChangedTime = datetime.now() - timedelta(0, 2*self.statusChangeDelay)
        logging.debug("{:} Starting zone thread".format(datetime.now().strftime("%H:%M:%S")))
        self.statusChangeThread.start()
        self.subscribeToInputs()
        logging.debug("{:} Setpoint monitor zone loaded".format(datetime.now().strftime("%H:%M:%S")))

    def statusChangeFunction(self):
        while True:
            #logging.debug("statusChangeFunction({:})".format(self.name))
            if (self.enabled == None and self.volatileStatus != None) or ((datetime.now() - self.statusChangedTime).total_seconds() > self.statusChangeDelay and self.volatileStatus != self.enabled):
                logging.debug("{:} : Changing status for {:} to '{:}'".format(datetime.now().strftime("%H:%M:%S"), self.name, self.volatileStatus))
                self.enabled = self.volatileStatus
                self.setStatus(self.enabled)
            time.sleep(2)

    def subscribeToInputs(self):
        self.mqtt.subscribe(self, (self.spTopicIn, 2))
        self.mqtt.subscribe(self, (self.statusTopicIn, 2))

    def requestValues(self, name):
        logging.debug("{:} : requestValues({:})".format(datetime.now().strftime("%H:%M:%S"), name))
        topic = "therminator/request"
        requestMessageSP = "\"{:}_setpoint\"".format(name)
        requestMessageEnabled = "\"{:}_enabled\"".format(name)
        self.mqtt.publish(topic, requestMessageEnabled)
        self.mqtt.publish(topic, requestMessageSP)

    def publishSetpoint(self, setpoint):
        logging.debug("{:} : publishSetpoint({:}) : {:}".format(datetime.now().strftime("%H:%M:%S"), setpoint, self.name))
        self.mqtt.publish(self.spTopicOut, setpoint)

    def setStatus(self, status):
        logging.debug("{:} : setStatus({:}) : {:}".format(datetime.now().strftime("%H:%M:%S"), status, self.name))
        if status == "True" or status == 1 or status == True:
            self.mqtt.publish(self.heatingTopicOut, 1)
        else:
            self.mqtt.publish(self.heatingTopicOut, 0)

    def setAndPublishSetpoint(self, setpoint):
        logging.debug("{:} : setAndPublishSetpoint({:}) : {:}".format(datetime.now().strftime("%H:%M:%S"), setpoint, self.name))
        if self.setpoint != setpoint:
            self.setpoint = setpoint
            self.publishSetpoint(setpoint)

    def on_message(self, client, userdata, message):
        if (message.topic == self.spTopicIn):
            setpoint = float(message.payload)
            self.setAndPublishSetpoint(setpoint)
        if (message.topic == self.statusTopicIn):
            self.statusChangedTime = datetime.now()
            self.volatileStatus = int(message.payload) == 1
            logging.debug("{:} : Received status change {:} for {:}".format(datetime.now().strftime("%H:%M:%S"), self.volatileStatus, self.name))

class Monitor:

    def __init__(self, configFilename):
        logFile = "/var/log/setpoint_monitor.log"
        logging.basicConfig(filename=logFile, level=logging.DEBUG)
        logging.debug("{:} Loading setpoint monitor".format(datetime.now().strftime("%H:%M:%S")))
        mqtt = {}
        self.setup = {}
        self.zones = []
        with open(configFilename) as f:
            config = json.load(f)
            with open(config["mqtt"]["configFile"]) as f2:
                mqtt = json.load(f2)
            with open(config["setup"]["configFile"]) as f2:
                self.setup = json.load(f2)
        self.mqtt = MqttProvider(mqtt["address"], mqtt["port"], logFile)
        self.firstContact = True
        self.watchdog = Watchdog(Modules.MONITOR, [Modules.CONNECTOR], mqtt, logFile)
        self.watchdog.onDependenciesComplete = self.onDependenciesComplete
        signal.pause()
#        while True:
#            sleep(0.1)

    def onDependenciesComplete(self):
        if self.firstContact:
            logging.debug("{:} : Loading monitor")
            self.firstContact = False
            self.loadZones(self.zones, self.setup, self.mqtt)
            logging.debug("{:} : Monitor running")


    def loadZones(self, zones, config, mqtt):
            for zoneName in config["zones"].keys():
                if "radiator" in config["zones"][zoneName]:
                    zones += [Zone(zoneName, mqtt)]

