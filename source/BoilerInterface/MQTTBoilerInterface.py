from BoilerInterface.BoilerInterface import BoilerInterface
from Controller.PID import PID

import json
import paho.mqtt.client as mqtt


class MQTTBoilerInterface(BoilerInterface):

    def __init__(self, configFilename):
        config = None
        with open(configFilename) as f:
            config = json.load(f)
        print(config)
        self.address  = config["address"]
        self.port = config["port"]
        if "username" in config.keys() and "password" in config.keys():
            self.username = config["username"]
            self.password = config["password"]
        else:
            self.username = None
            self.password = None
        self.returnTemperature = 0
        self.waterTemperature = 0
        self.gain = config["gain"]
        pidParmaeters = config["pid"]
        self.PID = PID(pidParmaeters["p"], pidParmaeters["i"], pidParmaeters["d"],pidParmaeters["errorSumLimit"],pidParmaeters["historyRange"])
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connect(self.address, self.port, self.username, self.password)

    def connect(self, address, port, username, password):
        self.client.connect(address, port, 60)
        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        #client.subscribe("therminator//#")
        #self.client.loop_forever()

    def setOutput(self, outputValue):
        outputValue *= self.gain
        outputValue = min(100,max(0, outputValue))
        self.client.publish("therminator/out/boiler_output", outputValue)

    def setMode(self, mode):
        print("Switching to mode '{:}'".format(mode))
        self.client.publish("therminator/out/mode", mode)
        self.client.publish("therminator/in/mode", mode)


    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("$SYS/#")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
