import numpy as np
import datetime
from datetime import timedelta

class PID(object):
    def __init__(self, P, I, D, I_max):
        self.setpoint = 15.0
        self.P = P
        self.I = I
        self.D = D
        self.lastError = 0
        self.errorSum = 0
        self.historyRange = timedelta(minutes=5)
        self.errorHistory = [(datetime.datetime.now(),0)]
        self.errorSumLimit = I_max
        self.lastRuntime = datetime.datetime.now()

    def setSetpoint(self, setpoint):
        self.setpoint = setpoint

    def getSetpoint(self):
        return self.setpoint

    def getOutput(self, temperature):
        self.temperature = temperature
        return self.run()

    def interpolate(self, index, time):
        if index > 0:
            time0, error0 = self.errorHistory[index - 1]
            time1, error1 = self.errorHistory[index]
            alpha = (time - time0) / (time1 - time0)
            return error0 * (1 - alpha) + error1 * alpha
        else:
            return self.errorHistory[index][1] # Should only happen at initialization and then the value will be 0 anyway

    def getEarlierError(self):
        now = datetime.datetime.now()
        lastError = 0
        for i in range(len(self.errorHistory)):
            time, error = self.errorHistory[i]
            if time + self.historyRange >= now:
                lastError = self.interpolate(i, now - self.historyRange)
                self.errorHistory = self.errorHistory[i-1:] + [(now, self.setpoint - self.temperature)]
                break
        return lastError

    def run(self):
        now = datetime.datetime.now()
        dt = (datetime.datetime.now() - self.lastRuntime).total_seconds()
        temp = self.temperature
        if temp != None:
            error = self.setpoint - temp
            errorDif = 0
            if dt > 0:
                errorDif = (error - self.getEarlierError()) / self.historyRange.seconds
                self.errorSum += error * dt
                self.errorSum = max(min(self.errorSum, self.errorSumLimit), -self.errorSumLimit)
            self.lastError = error
            print(self.P * error, self.I * self.errorSum, self.D * errorDif)
            result = self.P * error + self.I * self.errorSum + self.D * errorDif
        else:
            result = 0
        self.lastRuntime = now
        return result
