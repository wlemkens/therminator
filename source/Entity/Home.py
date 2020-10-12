from MQTT.MqttProvider import MqttProvider

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
        self.client = MqttProvider(mqttConfig["address"], mqttConfig["port"])
        topics = [(self.topicAway, 1), (self.topicMode, 1)]
        self.client.subscribe(self, topics)
        self.requestValues()

    def isAway(self):
        return self.away

    def update(self):
        self.on_update()

    def getMode(self):
        return self.mode
