import threading
import time

class Scheduler(threading.Thread) :
    def __init__(self):
        threading.Thread.__init__(self)
        self.interval = 60
        self.nextCallTime = time.time()
        self.sensorNames = []

    def run(self):
        print("ERROR : Not implemeted")

    def zoneCount(self):
        return 0