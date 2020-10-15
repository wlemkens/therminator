import json

from Scheduler.SchedulerFactory import SchedulerFactory

from MQTT.MqttProvider import MqttProvider


class ScheduleSwitcher(object):
    def __init__(self, config):
        self.topicSchedule = "therminator/in/schedule"
        schedulerType = config["scheduler"]["type"]
        controllerTypes = config["controllers"]
        setupFile = config["setup"]["configFile"]
        schedulerConfigFilename = config["scheduler"]["configFile"]
        self.scheduleName = config["scheduler"]["default"]
        boilerType = config["boiler_controller"]["type"]
        boilerConfig = config["boiler_controller"]["configFile"]
        mqttFile = config["mqtt"]["configFile"]
        with open(mqttFile) as f:
            mqttConfig = json.load(f)
        schedulerFactory = SchedulerFactory()

        with open(schedulerConfigFilename) as f:
            schedulerConfig = json.load(f)

        self.schedules = schedulerConfig["schedules"]
        schedule = self.schedules[self.scheduleName]
        self.modes = schedulerConfig["modes"]
        self.daytypes = schedulerConfig["daytypes"]
        self.scheduler = schedulerFactory.setupScheduler(schedulerType, controllerTypes, setupFile, schedule, self.modes, self.daytypes, boilerType, boilerConfig,mqttFile)
        self.connect(mqttConfig)
        self.scheduler.start()

    def selectSchedule(self, scheduleName):
        self.scheduler.loadConfig(self.schedules[scheduleName], self.modes, self.daytypes)

    def connect(self, mqttConfig):
        self.client = MqttProvider(mqttConfig["address"], mqttConfig["port"])
#        self.client.loop_start()
        topics = [(self.topicSchedule, 1)]
        r = self.client.subscribe(self, topics)
        self.client.publish("therminator/request","schedule")

    def on_message(self, client, userdata, message):
        if message.topic == self.topicSchedule:
            if self.scheduleName != str(message.payload,'utf-8'):
                self.scheduleName = str(message.payload,'utf-8')
                print("Switching to schedule '{:}'".format(self.scheduleName))
                self.selectSchedule(self.scheduleName)

