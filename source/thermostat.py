#!/usr/bin/python3

# Project specific imports
from Scheduler.ScheduleSwitcher import ScheduleSwitcher

# General imports
import sys
import json
import logging
import datetime

if __name__ == "__main__":
    if len(sys.argv) == 2:
        log_level = logging.INFO;
        logging.basicConfig(filename='/var/log/thermostat.log', level=log_level)
        logging.info(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Starting thermostat")
        filename = sys.argv[1]
        config = {}
        with open(filename) as f:
            config = json.load(f)
        scheduleSwitcher = ScheduleSwitcher(config, log_level)
    else:
        print("Usage {:} </path/to/config.json>".format(sys.argv[0]))