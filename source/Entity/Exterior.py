import paho.mqtt.client as mqtt

class Boiler(object):
	def __init__(self, mqttConfig, on_update):
		self.temperature = None
		self.topic = "therminator/in/exterior_temperature"
		self.connect(mqttConfig)
		self.on_update = on_update

	def on_message(self, client, userdata, message):
		if message.topic == self.topic:
			self.temperature = float(message.payload)
		self.update()

	def requestValues(self):
		topic = "therminator/request"
		requestMessage = "\"exterior_temperature\""
		self.client.publish(topic, requestMessage)

	def connect(self, mqttConfig):
		self.client = mqtt.Client()
		self.client.on_message = self.on_message
		self.client.connect(mqttConfig["address"], mqttConfig["port"], 60)
		self.client.loop_start()
		topics = [(self.topic,1)]
		self.client.loop_start()
		r = self.client.subscribe(topics)

	def getTemperature(self):
		return self.temperature

	def update(self):
		self.on_update()
