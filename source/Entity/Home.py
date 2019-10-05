import paho.mqtt.client as mqtt

import time

class Home(object):
    def __init__(self, mqttConfig, on_update):
        self.away = False
        self.topicAway = "therminator/in/away"
        self.connect(mqttConfig)
        self.on_update = on_update

    def on_message(self, client, userdata, message):
        if message.topic == self.topicAway:
            if self.away != bool(message.payload):
                self.away = bool(message.payload)
                self.update()

    def requestValues(self):
        topic = "therminator/request"
        requestMessageAway = "\"away\""
        self.client.publish(topic, requestMessageAway)

    def connect(self, mqttConfig):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(mqttConfig["address"], mqttConfig["port"], 60)
        self.client.loop_start()
        topics = [(self.topicTemp, 1), (self.topicSP, 1), (self.topicLvl, 1), (self.topicEnabled, 1)]
        self.client.loop_start()
        r = self.client.subscribe(topics)
        self.requestValues()

    def isAway(self):
        return self.away

    def update(self):
        self.on_update()
