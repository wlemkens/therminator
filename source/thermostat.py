#!/usr/bin/python3

# Project specific imports
from Scheduler.SchedulerFactory import SchedulerType
from Scheduler.SchedulerFactory import SchedulerFactory
from Controller.ControllerFactory import ControllerType
from Controller.ControllerFactory import ControllerFactory

# General imports

if __name__ == "__main__":
    schedulerFactory = SchedulerFactory()

    scheduler = schedulerFactory.createScheduler(SchedulerType.BASICSCHEDULER, ControllerType.PIDCONTROLLER, "/home/wim/projects/therminator/examples/setup.json", "/home/wim/projects/therminator/examples/basic schedule.json")

    scheduler.start()