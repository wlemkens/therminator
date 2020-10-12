from MQTT.MqttProvider import MqttProvider

class Boiler(object):
	def __init__(self, mqttConfig, on_update):
		self.requestedPower = 0
		self.deliveredPower = 0
		self.returnTemperature = 0
		self.flowTemperature = 0
		self.topicReq = "therminator/out/boiler_output"
		self.topicDel = "therminator/in/boiler_output"
		self.topicRet = "therminator/in/return_temperature"
		self.topicFlow = "therminator/in/flow_temperature"
		self.connect(mqttConfig)
		self.on_update = on_update

	def on_message(self, client, userdata, message):
		if message.topic == self.topicReq:
			if self.requestedPower != float(message.payload):
				self.requestedPower = float(message.payload)
				self.update()
		elif message.topic == self.topicDel:
			if self.deliveredPower != float(message.payload):
				self.deliveredPower = float(message.payload)
				self.update()
		if message.topic == self.topicRet:
			if self.returnTemperature != float(message.payload):
				self.returnTemperature = float(message.payload)
		elif message.topic == self.topicFlow:
			if self.flowTemperature != float(message.payload):
				self.flowTemperature = float(message.payload)

	def requestValues(self):
		topic = "therminator/request"
		requestMessageTemp = "\"{:}_temperature\"".format(self.name)
		requestMessageSP = "\"{:}_setpoint\"".format(self.name)
		requestMessageRet = "\"{:}_temperature\"".format(self.name)
		requestMessageFlow = "\"{:}_setpoint\"".format(self.name)
		self.client.publish(topic, requestMessageTemp)
		self.client.publish(topic, requestMessageSP)
		self.client.publish(topic, requestMessageRet)
		self.client.publish(topic, requestMessageFlow)

	def connect(self, mqttConfig):
		self.client = MqttProvider(mqttConfig["address"], mqttConfig["port"])
		topics = [(self.topicReq,1),(self.topicDel,1),(self.topicRet,1),(self.topicFlow,1)]
		self.client.subscribe(self, topics)

	def getRequestedPower(self):
		return self.requestedPower

	def getDeliveredPower(self):
		return self.deliveredPower

	def getReturnTemperature(self):
		return self.returnTemperature

	def getFlowTemperature(self):
		return self.flowTemperature

	def update(self):
		self.on_update()
