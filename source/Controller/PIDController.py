import numpy as np
import datetime

from Controller.Controller import Controller

class PIDController(Controller):
    def __init__(self, heatingInterface, config, zone):
        localConfig = config["zone_parameters"][zone]
        self.setpoint = 15.0
        self.P = localConfig["p"]
        self.I = localConfig["i"]
        self.D = localConfig["d"]
        self.lastError = 0
        self.errorSum = 0
        self.errorSumLimit = localConfig["errorSumLimit"]
        self.lastRuntime = datetime.datetime.now()
        self.heatingInterface = heatingInterface

    def setSetpoint(self, setpoint):
        self.setpoint = setpoint
        return self.run()

    def run(self):
        dt = (datetime.datetime.now() - self.lastRuntime).total_seconds()
        temp = self.heatingInterface.getTemperature()
        error = self.setpoint - temp
        errorDif = 0
        if dt > 0:
            errorDif = (error - self.lastError) / dt
            self.errorSum += error * dt
            self.errorSum = max(min(self.errorSum, self.errorSumLimit), -self.errorSumLimit)
        self.lastError = error
        result = self.P * error + self.I * self.errorSum + self.D * errorDif
        return result
