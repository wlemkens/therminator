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
        self.client = mqtt.Client()
        self.connect(self.address, self.port, self.username, self.password)

    def getTemperature(self):
        return self.temperature

    def getSetpoint(self):
        return self.setpoint

    def setSetpoint(self, setpoint):
        self.setpoint = setpoint

    def setOutput(self, outputValue):
        pass

    def on_message(self, client, userdata, message):
        if message.topic == self.topic_temp:
            self.temperature = float(message.payload)
        elif message.topic == self.topic_sp:
            self.setpoint = float(message.payload)
        #print("Received {:} : {:}".format(message.topic, self.temperature))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print ("subd")

    def on_connect(self, client, userdata, flags, rc):
        print ("Connected")

    def connect(self, address, port, username, password):
        #self.client.connect(address, port, 60)
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        self.topic_temp = "therminator/in/{:}_temperature".format(self.name)
        self.topic_sp = "therminator/in/{:}_setpoint".format(self.name)
        topics = [(self.topic_temp, 1), (self.topic_sp, 1)]
        print("Subscribing to topics '{:}'".format(topics))
        self.client.on_message = self.on_message
        self.client.connect(address, port, 60)
        self.client.loop_start()
        r = self.client.subscribe(topics)
        #self.client.loop_forever()
