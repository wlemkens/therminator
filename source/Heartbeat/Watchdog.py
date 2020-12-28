import threading
import time
import logging

from MQTT.MqttProvider import MqttProvider

class Watchdog(threading.Thread):

    def __init__(self, moduleType, dependencies, mqttConfig, logFile):
        logging.basicConfig(filename=logFile, level=logging.DEBUG)
        self.moduleType = moduleType
        self.dependencies = dependencies
        self.brokenDependencies = []
        self.unconfirmedDependencies = dependencies
        self.client = MqttProvider(mqttConfig["address"], mqttConfig["port"])
        self.heartbeatTopic = "therminator/heartbeat"
        self.client.subscribe(self, [(self.heartbeatTopic,2)])
        self.responseTimeout = 20
        self.heartbeatInterval = 60
        self.onDependenciesComplete = None
        self.heartbeatThread = threading.Thread(target=self.heartbeatLoop, daemon=True)
        self.heartbeatThread.start()

    def heartbeatLoop(self):
        while(True):
            self.requestPulse()
            time.sleep(self.heartbeatInterval - self.responseTimeout)

    def on_message(self, client, userdata, message):
        if message.topic == self.heartbeatTopic:
            payload = str(message.payload, "utf-8")
            if payload == "ping":
                self.client.publish(self.heartbeatTopic, self.moduleType)
            elif payload in self.unconfirmedDependencies:
                self.unconfirmedDependencies.remove(payload)
                if len(self.unconfirmedDependencies) == 0:
                    self.onDependenciesComplete()

    def requestPulse(self):
        self.brokenDependencies = []
        self.unconfirmedDependencies = self.dependencies
        self.client.publish(self.heartbeatTopic, "ping")
        time.sleep(self.responseTimeout)
        if len(self.unconfirmedDependencies) > 0:
            self.brokenDependencies = self.unconfirmedDependencies
            self.error = "{:} : Failed response from following depedencies {:}".format(self.moduleType, self.brokenDependencies)
            logging.error(self.error)
