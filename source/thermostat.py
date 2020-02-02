#!/usr/bin/python3

# Project specific imports
from Scheduler.ScheduleSwitcher import ScheduleSwitcher

# General imports
import sys
import json

if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        config = {}
        with open(filename) as f:
            config = json.load(f)
        scheduleSwitcher = ScheduleSwitcher(config)
    else:
        print("Usage {:} </path/to/config.json>".format(sys.argv[0]))