import paho.mqtt.client as mqtt

class Zone(object):
	def __init__(self, name, config, mqttConfig, on_update):
		self.temperature = None
		self.setpoint = None
		self.name = name
		self.topicTemp = "therminator/in/{:}_temperature".format(name)
		self.topicSP = "therminator/in/{:}_setpoint".format(name)
		self.icon = config["icon"]
		self.connect(mqttConfig)
		self.on_update = on_update

	def on_message(self, client, userdata, message):
		if message.topic == self.topicTemp:
			self.temperature = float(message.payload)
		elif message.topic == self.topicSp:
			self.setpoint = float(message.payload)
		self.update()

	def requestValues(self):
		topic = "therminator/request"
		requestMessageTemp = "\"{:}_temperature\"".format(self.name)
		requestMessageSP = "\"{:}_setpoint\"".format(self.name)
		self.client.publish(topic, requestMessageTemp)
		self.client.publish(topic, requestMessageSP)
		print("Requesting")

	def connect(self, mqttConfig):
		self.client = mqtt.Client()
		self.client.on_message = self.on_message
		self.client.connect(mqttConfig["address"], mqttConfig["port"], 60)
		self.client.loop_start()
		topics = [(self.topicTemp,1),(self.topicSP,1)]
		self.client.loop_start()
		r = self.client.subscribe(topics)
		self.requestValues()
                

	def getTemperature(self):
		return self.temperature

	def getSetpoint(self):
		return self.setpoint

	def getName(self):
		return self.name

	def isEnabled(self):
		return True

	def update(self):
		print("Updating1")
		self.on_update()
