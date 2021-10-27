import numpy as np
import datetime

from .Controller import Controller
from .PID import PID

class PIDController(Controller):
    def __init__(self, heatingInterface, config, zone):
        localConfig = config["zone_parameters"][zone]
        self.PID = PID(localConfig["p"], localConfig["i"], localConfig["d"], localConfig["errorSumLimit"],localConfig["historyRange"])
        self.PID.setSetpoint(15.0)
        self.heatingInterface = heatingInterface

    def setSetpoint(self, setpoint):
        self.PID.setSetpoint(setpoint-0.1)
        self.heatingInterface.setSetpoint(setpoint)

    def getOutput(self):
        if self.heatingInterface.getEnabled():
            sp = self.heatingInterface.getSetpoint()
            if sp:
                self.PID.setSetpoint(sp-0.1)
                return self.PID.getOutput(self.heatingInterface.getTemperature())
        return 0

    def getSetpoint(self):
        return self.heatingInterface.getSetpoint()

    def getTemperature(self):
        return self.heatingInterface.getTemperature()
