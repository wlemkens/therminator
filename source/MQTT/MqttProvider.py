import paho.mqtt.client as mqtt
import logging
import time
from datetime import datetime, timedelta

class MqttProvider:
    class __MqttProvider:
        def __init__(self, address, port, logFile):
            logging.basicConfig(filename=logFile, level=logging.DEBUG)
            logging.debug("{:} : Instance...".format(datetime.now().strftime("%H:%M:%S")))
            self.subscribers = []
            self.client = mqtt.Client()
            self.client.on_message = self.on_message
            connecting = True
            while(connecting):
                try:
                    logging.debug("{:} : Connecting...".format(datetime.now().strftime("%H:%M:%S")))
                    self.client.connect(address, port, 60)
                    self.client.loop_start()
                    connecting = False
                    logging.info("{:} : MQTT Connected".format(datetime.now().strftime("%H:%M:%S")))
                except:
                    logging.warning("{:} Failed to connect to mqtt".format(datetime.now().strftime("%H:%M:%S")))
                    time.sleep(10)


        def on_message(self, client, userdata, message):
            for subscriber in self.subscribers:
                subscriber.on_message(client, userdata, message)

        def subscribe(self, subscriber, topic, qos):
            if not subscriber in self.subscribers:
                self.subscribers += [subscriber]
            self.client.subscribe(topic, qos)

        def subscribe(self, subscriber, topics):
            # Note : Only subscribe(topic, qos) seems to take qos into account according to the documentation
            if not subscriber in self.subscribers:
                self.subscribers += [subscriber]
            if isinstance(topics, list):
                for topic in topics:
                    self.client.subscribe(topic[0], topic[1])
            else:
                self.client.subscribe(topics[0], topics[1])

        def publish(self, topic, message):
            logging.debug("{:} : Publishing on topic {:} value {:}".format(datetime.now().strftime("%H:%M:%S"), topic, message))
            self.client.publish(topic, message)

    instance = None

    def __init__(self, address, port, logFile, name = None):
        if name:
            logging.debug("{:} : Getting MQTT instance for {:}".format(datetime.now().strftime("%H:%M:%S"), name))
        if not MqttProvider.instance:
            logging.debug("{:} : Creating MQTT instance".format(datetime.now().strftime("%H:%M:%S")))
            MqttProvider.instance = MqttProvider.__MqttProvider(address, port, logFile)

    def __getattr__(self, name):
        return getattr(self.instance, name)
