#!/usr/bin/python3

# Project specific imports
from Scheduler.SchedulerFactory import SchedulerType
from Scheduler.SchedulerFactory import SchedulerFactory
from Controller.ControllerFactory import ControllerType
from Controller.ControllerFactory import ControllerFactory

# General imports
import sys
import json

if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        schedulerFactory = SchedulerFactory()
        config = {}
        with open(filename) as f:
            config = json.load(f)
        scheduler = schedulerFactory.createScheduler(config)

        scheduler.start()
    else:
        print("Usage {:} </path/to/config.json>".format(sys.argv[0]))