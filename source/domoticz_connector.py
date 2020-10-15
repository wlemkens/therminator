import sys
import json
import paho.mqtt.client as mqtt

domoticzIn = "domoticz/in"
therminatorIn = "therminator/in"
scheduleTopic = "therminator/in/schedule"

domoticzOut = "domoticz/out"
therminatorOut = "therminator/out"

therminatorRequest = "therminator/request"

scheduleId = 13
ids = {
    167 : "living_temperature",
    180 : "badkamer_temperature",
    256 : "kamer_ariane_temperature",
    183 : "bureau_temperature",
    235 : "exterior_temperature",
    248 : "kamer_nathan_temperature",
    265 : "slaapkamer_temperature",

    136 : "living_setpoint",
    208 : "badkamer_setpoint",
    29 : "kamer_ariane_setpoint",
    112 : "bureau_setpoint",
    292 : "kamer_nathan_setpoint",

    132 : "living_level",
    204 : "badkamer_level",
    18 : "kamer_ariane_level",
    110 :  "bureau_level",
    290 : "kamer_nathan_level",

    189 : "living_enabled",
    190 : "badkamer_enabled",
    191 : "kamer_ariane_enabled",
    192 : "bureau_enabled",
    300 : "kamer_nathan_enabled",

    199 : "living_stored_setpoint",
    200 : "badkamer_stored_setpoint",
    201 : "kamer_ariane_stored_setpoint",
    202 : "bureau_stored_setpoint",
    301 : "kamer_nathan_stored_setpoint",

    216 : "away",
    scheduleId : "schedule"
}

schedules = {
    "10" : "standard",
    "20" : "holiday",
    "30" : "away",
    "40" : "homework",
    "50" : "test"
}
# Inverse lookup table
topics = {}
for key in ids.keys():
    topic = ids[key]
    topics[topic] = key

def getDomoticzId(topic):
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
    return "_setpoint" in topic or "_level" in topic

def parseBatteryTopic(wholeTopic):
    res = wholeTopic.rpartition("/")
    topic = res[2]
    return "therminator/in/"+topic.replace("_setpoint","").replace("_level","")

def on_message(client, userdata, message):
    if message.topic == domoticzOut:
        msg = json.loads(message.payload);
        id = msg["idx"]
        value = msg["nvalue"]
        if not value:
            if "svalue1" in msg:
                value = msg["svalue1"]
        if id == scheduleId:
            value = msg["svalue1"]
            schedule = schedules[value]
            client.publish(scheduleTopic, schedule)
        else:
            battery = 255
            if "Battery" in msg:
                battery = msg["Battery"]
            topic = getTherminatorTopic(id)
            if topic:
                client.publish(topic, value)
                if battery <= 100 and isBatteryTopic(topic):
                    batteryTopic = parseBatteryTopic(topic)
                    client.publish(batteryTopic, battery)
                print("Translating topic {:} -> Publishing on topic {:} : {:}".format(domoticzOut, topic, value))
    elif therminatorOut in message.topic:
        topic = parseTherminatorTopic(message.topic)
        id = getDomoticzId(topic)
        if id:
            value = str(message.payload,'utf-8')
            #value = float(message.payload)
            struct = {
                "idx" : id,
                "svalue" : value
            }
            jsonMsg = json.dumps(struct)
            client.publish(domoticzIn, jsonMsg)
            print("Translating topic {:} : {:} -> Publishing on topic {:} : {:}".format(topic, value, domoticzIn, jsonMsg))
    elif message.topic == therminatorRequest:
        topic = str(message.payload,'utf-8').strip('\"')
        id = getDomoticzId(topic)
        if id:
            struct = {
                "command" : "getdeviceinfo",
                "idx" : id
            }
            jsonMsg = json.dumps(struct)
            client.publish(domoticzIn, jsonMsg)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        configFilename = sys.argv[1]

        client = mqtt.Client()
        with open(configFilename) as f:
            config = json.load(f)

        client.on_message = on_message
        client.connect(config["address"], config["port"], 60)
        client.subscribe(therminatorOut+"/#", 2)
        client.subscribe(domoticzOut, 2)
        client.subscribe(therminatorRequest, 2)
        client.loop_forever()

    else:
        print("Usage {:} </path/to/mqtt.json>".format(sys.argv[0]))