import paho.mqtt.client as mqtt

class Boiler(object):
	def __init__(self, mqttConfig, on_update):
		self.requestedPower = 0
		self.deliveredPower = 0
		self.topicReq = "therminator/out/boiler_output"
		self.topicDel = "therminator/in/boiler_output"
		self.connect(mqttConfig)
		self.on_update = on_update

	def on_message(self, client, userdata, message):
		if message.topic == self.topicReq:
			self.requestedPower = float(message.payload)
		elif message.topic == self.topicDel:
			self.deliverdPower = float(message.payload)
		self.update()

	def requestValues(self):
		topic = "therminator/request"
		requestMessageTemp = "\"{:}_temperature\"".format(self.name)
		requestMessageSP = "\"{:}_setpoint\"".format(self.name)
		self.client.publish(topic, requestMessageTemp)
		self.client.publish(topic, requestMessageSP)

	def connect(self, mqttConfig):
		self.client = mqtt.Client()
		self.client.on_message = self.on_message
		self.client.connect(mqttConfig["address"], mqttConfig["port"], 60)
		self.client.loop_start()
		topics = [(self.topicReq,1),(self.topicDel,1)]
		self.client.loop_start()
		r = self.client.subscribe(topics)

	def getRequestedPower(self):
		return self.requestedPower

	def getDeliveredPower(self):
		return self.deliveredPower

	def update(self):
		self.on_update()
