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
        return self.PID.getOutput(self.heatingInterface.getTemperature())
