import paho.mqtt.subscribe as subscribe
import paho.mqtt.client as mqtt


from HeatingInterface.HeatingInterface import HeatingInterface

class RadiatorHeatingInterface(HeatingInterface):
    def __init__(self, name, config):
        self.address  = config["address"]
        self.port = config["port"]
        self.name = name
        if "username" in config.keys() and "password" in config.keys():
            self.username = config["username"]
            self.password = config["password"]
        else:
            self.username = None
            self.password = None
        self.temperature = None
        self.setpoint = None
        self.enabled = True
        self.client = mqtt.Client()
        self.connect(self.address, self.port, self.username, self.password)

    def getTemperature(self):
        return self.temperature

    def getSetpoint(self):
        return self.setpoint

    def setSetpoint(self, setpoint):
        self.client.publish("therminator/out/{:}_setpoint".format(self.name), setpoint)
        self.setpoint = setpoint

    def setOutput(self, outputValue):
        pass

    def on_message(self, client, userdata, message):
        if message.topic == self.topic_temp:
            self.temperature = float(message.payload)
        elif message.topic == self.topic_sp:
            self.setpoint = float(message.payload)
        #print("Received {:} : {:}".format(message.topic, message.payload))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print ("subd")

    def on_connect(self, client, userdata, flags, rc):
        print ("Connected")

    def requestValues(self):
        topic = "therminator/request"
        requestMessageTemp = "\"{:}_temperature\"".format(self.name)
        requestMessageSP = "\"{:}_setpoint\"".format(self.name)
        requestMessageEnabled = "\"{:}_enabled\"".format(self.name)
        self.client.publish(topic, requestMessageTemp)
        self.client.publish(topic, requestMessageSP)
        self.client.publish(topic, requestMessageEnabled)

    def connect(self, address, port, username, password):
        #self.client.connect(address, port, 60)
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        self.topic_temp = "therminator/in/{:}_temperature".format(self.name)
        self.topic_sp = "therminator/in/{:}_setpoint".format(self.name)
        self.topicEnabled = "therminator/in/{:}_enabled".format(self.name)
        topics = [(self.topic_temp, 1), (self.topic_sp, 1),(self.topicEnabled,1)]
        print("Subscribing to topics '{:}'".format(topics))
        self.client.on_message = self.on_message
        self.client.connect(address, port, 60)
        self.client.loop_start()
        r = self.client.subscribe(topics)
        self.requestValues()
        #self.client.loop_forever()

    def isEnabled(self):
        return self.enabled
