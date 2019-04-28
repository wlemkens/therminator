import numpy as np
import datetime

class PID(object):
    def __init__(self, P, I, D, I_max):
        self.setpoint = 15.0
        self.P = P
        self.I = I
        self.D = D
        self.lastError = 0
        self.errorSum = 0
        self.errorSumLimit = I_max
        self.lastRuntime = datetime.datetime.now()

    def setSetpoint(self, setpoint):
        self.setpoint = setpoint

    def getOutput(self, temperature):
        self.temperature = temperature
        return self.run()

    def run(self):
        dt = (datetime.datetime.now() - self.lastRuntime).total_seconds()
        temp = self.temperature
        if temp != None:
            error = self.setpoint - temp
            errorDif = 0
            if dt > 0:
                errorDif = (error - self.lastError) / dt
                self.errorSum += error * dt
                self.errorSum = max(min(self.errorSum, self.errorSumLimit), -self.errorSumLimit)
            self.lastError = error
            result = self.P * error + self.I * self.errorSum + self.D * errorDif
        else:
            result = 0
        return result
