from BoilerInterface.BoilerInterface import BoilerInterface
from Controller.PID import PID

import json

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
        self.PID = PID(pidParmaeters["p"], pidParmaeters["i"], pidParmaeters["d"],pidParmaeters["errorSumLimit"])
        self.connect(self.address, self.port, self.username, self.password)

    def connect(self, address, port, username, password):
        pass

    def setOutput(self, outputValue):
        outputValue *= self.gain
        outputValue = min(100,max(0, outputValue))
        print("Boiler level {:}%".format(outputValue))