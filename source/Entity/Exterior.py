from MQTT.MqttProvider import MqttProvider

class Exterior(object):
	def __init__(self, mqttConfig, on_update):
		self.temperature = None
		self.topic = "therminator/in/exterior_temperature"
		self.connect(mqttConfig)
		self.on_update = on_update

	def on_message(self, client, userdata, message):
		if message.topic == self.topic:
			if self.temperature != float(message.payload):
				self.temperature = float(message.payload)
				self.update()

	def requestValues(self):
		topic = "therminator/request"
		requestMessage = "\"exterior_temperature\""
		self.client.publish(topic, requestMessage)

	def connect(self, mqttConfig):
		self.client = MqttProvider(mqttConfig["address"], mqttConfig["port"])
		topics = [(self.topic,1)]
		self.client.subscribe(self, topics)
		self.requestValues()

	def getTemperature(self):
		return self.temperature

	def update(self):
		self.on_update()
