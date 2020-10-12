import paho.mqtt.client as mqtt

class MqttProvider:
    class __MqttProvider:
        def __init__(self, address, port):
            self.subscribers = []
            self.client = mqtt.Client()
            self.client.on_message = self.on_message
            self.client.connect(address, port, 60)
            self.client.loop_start()

        def on_message(self, client, userdata, message):
            for subscriber in self.subscribers:
                subscriber.on_message(client, userdata, message)

        def subscribe(self, subscriber, topics):
            if not subscriber in self.subscribers:
                self.subscribers += [subscriber]
            if isinstance(topics, list):
                self.client.subscribe(topics)
            else:
                self.client.subscribe([topics])

        def publish(self, topic, message):
            self.client.publish(topic, message)

    instance = None

    def __init__(self, address, port):
        if not MqttProvider.instance:
            MqttProvider.instance = MqttProvider.__MqttProvider(address, port)

    def __getattr__(self, name):
        return getattr(self.instance, name)