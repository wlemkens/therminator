import threading
import time

class Scheduler(threading.Thread) :
    def __init__(self):
        threading.Thread.__init__(self)
        self.interval = 15
        self.nextCallTime = time.time()

    def run(self):
        print("ERROR : Not implemeted")

    def zoneCount(self):
        return 0