import threading
import time
import logging

class Scheduler(threading.Thread) :
    def __init__(self):
        threading.Thread.__init__(self)
        logging.basicConfig(filename='/var/log/thermostat.log', level=logging.DEBUG)
        self.interval = 60
        self.nextCallTime = time.time()
        self.sensorNames = []

    def run(self):
        logging.error("Not implemeted")

    def zoneCount(self):
        return 0