import paho.mqtt.client as mqtt

import time

class Home(object):
    def __init__(self, mqttConfig, on_update):
        self.away = False
        self.mode = None
        self.topicAway = "therminator/in/away"
        self.topicMode = "therminator/in/mode"
        self.connect(mqttConfig)
        self.on_update = on_update

    def on_message(self, client, userdata, message):
        if message.topic == self.topicAway:
            if self.away != int(message.payload):
                self.away = int(message.payload)
                self.update()
        if message.topic == self.topicMode:
            if self.mode != str(message.payload, 'utf-8'):
                self.mode = str(message.payload, 'utf-8')
                self.update()

    def requestValues(self):
        topic = "therminator/request"
        requestMessageAway = "\"away\""
        requestMessageMode = "\"mode\""
        self.client.publish(topic, requestMessageAway)
        self.client.publish(topic, requestMessageMode)

    def connect(self, mqttConfig):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(mqttConfig["address"], mqttConfig["port"], 60)
        self.client.loop_start()
        topics = [(self.topicAway, 1), (self.topicMode, 1)]
        self.client.loop_start()
        r = self.client.subscribe(topics)
        self.requestValues()

    def isAway(self):
        return self.away

    def update(self):
        self.on_update()

    def getMode(self):
        return self.mode
