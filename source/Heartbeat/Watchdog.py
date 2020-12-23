import threading
import time

from MQTT.MqttProvider import MqttProvider

class Watchdog(threading.Thread):

    def __init__(self, type, dependencies, mqttConfig):
        self.type = type
        self.dependencies = dependencies
        self.brokenDependencies = []
        self.client = MqttProvider(mqttConfig["address"], mqttConfig["port"])
        self.heartbeatTopic = "therminator/heartbeat"
        self.client.subscribe(self, self.heartbeatTopic)
        self.responseTimeout = 20
        self.heartbeatInterval = 60
        self.heartbeatLoop()

    def run(self):
        while(True):
            self.requestPulse()
            time.sleep(self.heartbeatInterval - self.responseTimeout)

    def on_message(self, client, userdata, message):
        if message.topic == self.heartbeatTopic:
            payload = str(message.payload, "utf-8")
            if payload == "ping":
                self.client.publish(self.heartbeatTopic, type)
            elif payload in self.unconfirmedDependencies:
                self.unconfirmedDependencies.remove(payload)

    def requestPulse(self):
        self.brokenDependencies = []
        self.unconfirmedDependencies = self.dependencies
        self.client.publish(self.heartbeatTopic, "ping")
        time.sleep(self.responseTimeout)
        if len(self.unconfirmedDependencies) > 0:
            self.brokenDependencies = self.unconfirmedDependencies
            self.error = "{:} : Failed response from following depedencies {:}".format(self.type, self.brokenDependencies)))
            print(self.error)