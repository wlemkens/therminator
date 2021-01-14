#!/usr/bin/python3

# General imports
import sys
import json

from Monitor.Monitor import Monitor

zones = []

if __name__ == "__main__":
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        Monitor(filename)

    else:
        print("Usage {:} </path/to/config.json>".format(sys.argv[0]))

