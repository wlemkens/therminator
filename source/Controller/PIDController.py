import numpy as np
import datetime

from Controller.Controller import Controller

class PIDController(Controller):
    def __init__(self, heatingInterface):
        self.setpoint = 15.0
        self.P = 1.0
        self.I = 0.01
        self.D = 0.001
        self.lastError = 0
        self.errorSum = 0
        self.errorSumLimit = 10
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
