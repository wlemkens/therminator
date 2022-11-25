import threading
import time
import logging

class Scheduler(threading.Thread) :
    def __init__(self, log_level = logging.WARNING):
        threading.Thread.__init__(self)
        logging.basicConfig(filename='/var/log/thermostat.log', level=log_level)
        self.interval = 60
        self.nextCallTime = time.time()
        self.sensorNames = []

    def run(self):
        logging.error("Not implemeted")

    def zoneCount(self):
        return 0