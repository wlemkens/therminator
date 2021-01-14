import paho.mqtt.client as mqtt
import logging
import time

class MqttProvider:
    class __MqttProvider:
        def __init__(self, address, port, logFile):
            logging.basicConfig(filename=logFile, level=logging.DEBUG)
            self.subscribers = []
            self.client = mqtt.Client()
            self.client.on_message = self.on_message
            while(True):
                try:
                    self.client.connect(address, port, 60)
                    self.client.loop_start()
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
            self.client.publish(topic, message)

    instance = None

    def __init__(self, address, port, logFile):
        if not MqttProvider.instance:
            MqttProvider.instance = MqttProvider.__MqttProvider(address, port, logFile)

    def __getattr__(self, name):
        return getattr(self.instance, name)
