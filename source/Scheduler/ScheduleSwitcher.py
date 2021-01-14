import json
import time

from Scheduler.SchedulerFactory import SchedulerFactory

from Heartbeat.Modules import Modules
from Heartbeat.Watchdog import Watchdog
from MQTT.MqttProvider import MqttProvider

import logging

class ScheduleSwitcher(object):
    def __init__(self, config):
        logging.basicConfig(filename='/var/log/thermostat.log', level=logging.DEBUG)
        self.topicSchedule = "therminator/in/schedule"
        self.schedulerType = config["scheduler"]["type"]
        self.controllerTypes = config["controllers"]
        self.setupFile = config["setup"]["configFile"]
        schedulerConfigFilename = config["scheduler"]["configFile"]
        self.scheduleName = config["scheduler"]["default"]
        self.boilerType = config["boiler_controller"]["type"]
        self.boilerConfig = config["boiler_controller"]["configFile"]
        self.mqttFile = config["mqtt"]["configFile"]
        with open(self.mqttFile) as f:
            mqttConfig = json.load(f)

        with open(schedulerConfigFilename) as f:
            schedulerConfig = json.load(f)

        self.schedules = schedulerConfig["schedules"]
        self.schedule = self.schedules[self.scheduleName]
        self.modes = schedulerConfig["modes"]
        self.daytypes = schedulerConfig["daytypes"]
        logFile = "/var/log/thermostat.log"
        self.connect(mqttConfig, logFile)
        self.firstContact = True
        self.watchdog = Watchdog(Modules.THERMOSTAT, [Modules.CONNECTOR, Modules.MONITOR], mqttConfig, logFile)
        self.watchdog.onDependenciesComplete = self.onDependenciesComplete
        while True:
            time.sleep(1000)

    def onDependenciesComplete(self):
        if self.firstContact:
            logging.debug("Loading scheduler")
            self.firstContact = False
            schedulerFactory = SchedulerFactory()
            self.scheduler = schedulerFactory.setupScheduler(self.schedulerType, self.controllerTypes, self.setupFile, self.schedule, self.modes, self.daytypes, self.boilerType, self.boilerConfig, self.mqttFile)
            topics = [(self.topicSchedule, 1)]
            r = self.client.subscribe(self, topics)
            self.client.publish("therminator/request","schedule")
            self.scheduler.start()

    def selectSchedule(self, scheduleName):
        self.scheduler.loadConfig(self.schedules[scheduleName], self.modes, self.daytypes)

    def connect(self, mqttConfig, logFile):
        self.client = MqttProvider(mqttConfig["address"], mqttConfig["port"], logFile)
#        self.client.loop_start()

    def on_message(self, client, userdata, message):
        if message.topic == self.topicSchedule:
            if self.scheduleName != str(message.payload,'utf-8'):
                self.scheduleName = str(message.payload,'utf-8')
                logging.debug("Switching to schedule '{:}'".format(self.scheduleName))
                self.selectSchedule(self.scheduleName)

