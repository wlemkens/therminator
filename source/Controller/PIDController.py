import numpy as np
import datetime

from Controller.Controller import Controller
from Controller.PID import PID

class PIDController(Controller):
    def __init__(self, heatingInterface, config, zone):
        localConfig = config["zone_parameters"][zone]
        self.PID = PID(localConfig["p"], localConfig["i"], localConfig["d"], localConfig["errorSumLimit"])
        self.PID.setSetpoint(15.0)
        self.heatingInterface = heatingInterface

    def setSetpoint(self, setpoint):
        self.PID.setSetpoint(setpoint)
        self.heatingInterface.setSetpoint(setpoint)

    def getOutput(self):
        self.PID.setSetpoint(self.heatingInterface.getSetpoint())
        return self.PID.getOutput(self.heatingInterface.getTemperature())

    def getSetpoint(self):
        return self.heatingInterface.getSetpoint()

    def getTemperature(self):
        return self.heatingInterface.getTemperature()