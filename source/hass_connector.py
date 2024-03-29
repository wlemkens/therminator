import sys
import json
import paho.mqtt.client as mqtt
import logging
import datetime
import time

from Heartbeat.Modules import Modules
from Heartbeat.Watchdog import Watchdog

zwaveOut = "zwave/"
therminatorIn = "therminator/in/"
scheduleTopic = "therminator/in/schedule"

zwaveIn = "zwave/"
zigbeeIn = "homeassistant/sensor/"
hassIn = "home-assistant/"
therminatorOut = "therminator/out"
boilerOut = "home/ems-esp/boiler_cmd_burnerpower"

therminatorRequest = "therminator/request"

scheduleId = 13
ids = {
    "living_temperature" : "living_temperature",
    "badkamer_temperature" : "badkamer_temperature",
    "ariane_temperature" : "kamer_ariane_temperature",
    "bureau_temperature" : "bureau_temperature",
    "exterior_temperature" : "exterior_temperature",
    "nathan_temperature" : "kamer_nathan_temperature",
    "slaapkamer_temperature" : "slaapkamer_temperature",

    12 : "living_temperature-radiator",
    215 : "badkamer_temperature-radiator",
    33 : "kamer_ariane_temperature-radiator",
    117 : "bureau_temperature-radiator",
    304 : "kamer_nathan_temperature-radiator",

    "nodeID_30/67/0/setpoint/1" : "living_setpoint",
    "nodeID_50/67/1/setpoint/1" : "badkamer_setpoint",
    "nodeID_32/67/0/setpoint/1" : "kamer_ariane_setpoint",
    "nodeID_19/67/0/setpoint/1" : "bureau_setpoint",
    "nodeID_31/67/0/setpoint/1" : "kamer_nathan_setpoint",

    # 189 : "living_enabled",
    # 190 : "badkamer_enabled",
    # 257 : "kamer_ariane_enabled",
    # 192 : "bureau_enabled",
    # 300 : "kamer_nathan_enabled",

    "nodeID_30/64/0/mode" : "living_enabled",
    "nodeID_50/64/1/mode" : "badkamer_enabled",
    "nodeID_32/64/0/mode" : "kamer_ariane_enabled",
    "nodeID_19/64/0/mode" : "bureau_enabled",
    "nodeID_31/64/0/mode" : "kamer_nathan_enabled",

    509607953 : "living_battery",
    325058577 : "bureau_battery",
    526385169 : "kamer_nathan_battery",
    543162385 : "kamer_ariane_battery",
    559939601 : "badkamer_battery",

    "boiler_output" : "input_number.boiler_output",

    216 : "away",
    346 : "ping",
    scheduleId : "schedule"
}

schedules = {
    "10" : "standard",
    "60" : "standard 2",
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
#    logging.debug("Received {:}".format(message))
    if zwaveIn in message.topic:
        #logging.debug("Received {:} : {:}".format(message.topic, message.payload))
        # We got a setpoint change
        msg = json.loads(message.payload);
        parts = message.topic.split("/")
        topic = getTherminatorTopic("/".join(parts[1:]))
        if topic:
            #logging.debug("Received {:} : {:}".format(message.topic, message.payload))
            logging.debug("ZWI Received {:} : {:}".format(message.topic, message.payload))

            value = msg["value"]
            #logging.debug("Topic {:} value {:}".format(topic, value))
            if topic:
                client.publish(topic, value, retain=True)
                logging.debug("{:} : Translating topic {:} -> Publishing on topic {:} : {:}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message.topic, topic, value))
    elif zigbeeIn in message.topic:
        # We got a message from zigbee
        # - door status change (ignored)
        # - temperatures
        logging.debug("ZI Received {:} : {:}".format(message.topic, message.payload))

        parts = message.topic.split("/")
        topic = getTherminatorTopic(parts[-2])
        type = parts[-1]
        if topic and type == "state":
            value = message.payload
            client.publish(topic, value, retain=True)
            logging.debug("{:} : Translating topic {:} -> Publishing on topic {:} : {:}".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message.topic, topic, value))
    elif hassIn in message.topic:
        logging.debug("HI Received {:} : {:}".format(message.topic, message.payload))

        # We got a message from Home Assistant
        # - zone status change
        # - schedule type change
        parts = message.topic.split("/")
        type = parts[1]
        value = message.payload
        # topic = parts[2]
        if type == "schedule":
            client.publish(scheduleTopic, value, retain=True)
            logging.debug("{:} : Translating topic {:} -> Publishing on topic {:} : {:}".format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message.topic, scheduleTopic, value))

    elif therminatorOut in message.topic:
        logging.debug("TO Received {:} : {:}".format(message.topic, message.payload))
        # We got a message from the thermostat
        # - scheduled setpoint change
        topic = parseTherminatorTopic(message.topic)
        id = getHassId(topic)
        logging.debug("Topic id {:} : {:}".format(topic, id))
        if topic:
            if topic == "boiler_output":
                value = str(message.payload, 'utf-8')
                client.publish(boilerOut, value, retain=True)
                logging.info("{:} : Translating topic {:} : {:} -> Publishing on topic {:} : {:}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), topic, value, boilerOut, value))
            elif id:
                value = str(message.payload,'utf-8')
                client.publish(zwaveOut+id+"/set", value, retain=True)
                logging.info("{:} : Translating topic {:} : {:} -> Publishing on topic {:} : {:}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), topic, value, zwaveOut+id+"/set", value))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        logging.basicConfig(filename='/var/log/connector.log', level=logging.DEBUG)
        #logging.basicConfig(filename='/var/log/connector.log', level=logging.INFO)
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
                watchdog = Watchdog(Modules.CONNECTOR, [], config, "/var/log/connector.log")
                client.loop_forever()
            except Exception as e:
                print("Failled connecting to mqtt : {:}".format(e))
                time.sleep(10)

    else:
        logging.info("Usage {:} </path/to/mqtt.json>".format(sys.argv[0]))
