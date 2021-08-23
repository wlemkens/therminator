import sys
import json
import paho.mqtt.client as mqtt
import logging
import datetime
import time

from Heartbeat.Modules import Modules
from Heartbeat.Watchdog import Watchdog

zwaveOut = "OpenZWave/1/command/setvalue/"
therminatorIn = "therminator/in"
scheduleTopic = "therminator/in/schedule"

zwaveIn = "OpenZWave/1/node/"
zigbeeIn = "zigbee2mqtt/"
hassIn = "home-assistant/"
therminatorOut = "therminator/out"
boilerOut = "home/ems-esp/boiler_cmd_burnerpower"

therminatorRequest = "therminator/request"

scheduleId = 13
ids = {
    "Living thermometer" : "living_temperature",
    "Badkamer thermomete" : "badkamer_temperature",
    "Ariane thermometer" : "kamer_ariane_temperature",
    "Bureau thermometer" : "bureau_temperature",
    "Buiten thermometer" : "exterior_temperature",
    "Nathan thermometer" : "kamer_nathan_temperature",
    "Slaapkamer thermometer" : "slaapkamer_temperature",

    12 : "living_temperature-radiator",
    215 : "badkamer_temperature-radiator",
    33 : "kamer_ariane_temperature-radiator",
    117 : "bureau_temperature-radiator",
    304 : "kamer_nathan_temperature-radiator",

    281475485319186 : "living_setpoint",
    281475535650834 : "badkamer_setpoint",
    281475518873618 : "kamer_ariane_setpoint",
    281475300769810 : "bureau_setpoint",
    281475502096402 : "kamer_nathan_setpoint",

    # 189 : "living_enabled",
    # 190 : "badkamer_enabled",
    # 257 : "kamer_ariane_enabled",
    # 192 : "bureau_enabled",
    # 300 : "kamer_nathan_enabled",

    508559380 : "living_enabled",
    558891028 : "badkamer_enabled",
    542113812 : "kamer_ariane_enabled",
    324010004 : "bureau_enabled",
    525336596 : "kamer_nathan_enabled",

    509607953 : "living_battery",
    325058577 : "bureau_battery",
    526385169 : "kamer_nathan_battery",
    543162385 : "kamer_ariane_battery",
    559939601 : "badkamer_battery",

    216 : "away",
    346 : "ping",
    scheduleId : "schedule"
}

schedules = {
    "10" : "standard",
    "20" : "holiday",
    "30" : "away",
    "40" : "homework",
    "50" : "homework2"
}
# Inverse lookup table
topics = {}
for key in ids.keys():
    topic = ids[key]
    topics[topic] = key

def getHassId(topic):
    if topic in topics:
        return topics[topic]
    return None

def getTherminatorTopic(id):
    if id in ids:
        return "therminator/in/"+ids[id]
    return None

def parseTherminatorTopic(wholeTopic):
    parts = wholeTopic.split("/")
    return parts[-1]

def isBatteryTopic(topic):
    return "_setpoint" in topic \
           or "_level" in topic \
           or "_heating" in topic \
           or "_temperature-radiator" in topic

def parseBatteryTopic(wholeTopic):
    res = wholeTopic.rpartition("/")
    topic = res[2]
    return "therminator/in/"+topic.replace("_setpoint","").replace("_level","")+"_battery"

def getValue(message):
    try:
        if "Value" in message:
            value = message["Value"]
            try:
                if "Selected_id" in value:
                    return value["Selected_id"]
            except:
                pass
            return value
    except Exception:
        return None

def on_message(client, userdata, message):
    if zwaveIn in message.topic:
        # We got a setpoint change
        msg = json.loads(message.payload);
        if "ValueIDKey" in msg:
            id = msg["ValueIDKey"]
            value = getValue(msg)

            topic = getTherminatorTopic(id)
            if topic:
                client.publish(topic, value)
                logging.debug("{:} : Translating topic {:} -> Publishing on topic {:} : {:}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message.topic, topic, value))
    elif zigbeeIn in message.topic:
        # We got a message from zigbee
        # - door status change (ignored)
        # - temperatures
        parts = message.topic.split("/")
        topic = getTherminatorTopic(parts[1])
        if topic:
            msg = json.loads(message.payload);
            value = msg["temperature"]
            client.publish(topic, value)
            logging.debug("{:} : Translating topic {:} -> Publishing on topic {:} : {:}".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message.topic, topic, value))
    elif hassIn in message.topic:
        # We got a message from Home Assistant
        # - zone status change
        # - schedule type change
        parts = message.topic.split("/")
        type = parts[1]
        value = message.payload
        # topic = parts[2]
        if type == "schedule":
            client.publish(scheduleTopic, value)
            logging.debug("{:} : Translating topic {:} -> Publishing on topic {:} : {:}".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message.topic, scheduleTopic, value))

    elif therminatorOut in message.topic:
        # We got a message from the thermostat
        # - scheduled setpoint change
        topic = parseTherminatorTopic(message.topic)
        id = getHassId(topic)
        if id:
            if id == "boiler_output":
                value = str(message.payload, 'utf-8')
                client.publish(boilerOut, value)
            else:
                value = str(message.payload,'utf-8')
                client.publish(zwaveOut, value)
                logging.debug("{:} : Translating topic {:} : {:} -> Publishing on topic {:} : {:}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), topic, value, zwaveOut, value))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        logging.basicConfig(filename='/var/log/domoticz_connector.log', level=logging.DEBUG)
        configFilename = sys.argv[1]

        client = mqtt.Client()
        with open(configFilename) as f:
            config = json.load(f)

        while(True):
            try:
                client.on_message = on_message
                client.connect(config["address"], config["port"], 60)
                client.subscribe(therminatorOut+"/#", 2)
                client.subscribe(zwaveIn+"#", 2)
                client.subscribe(zigbeeIn+"#", 2)
                client.subscribe(hassIn+"#", 2)
                watchdog = Watchdog(Modules.CONNECTOR, [], config, "/var/log/domoticz_connector.log")
                client.loop_forever()
            except Exception as e:
                print("Failled connecting to mqtt : {:}".format(e))
                time.sleep(10)

    else:
        logging.debug("Usage {:} </path/to/mqtt.json>".format(sys.argv[0]))
