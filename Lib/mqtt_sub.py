#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import paho.mqtt.client as mqtt


def on_connect(client, userdata, rc, dummy):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

    # client.subscribe("$SYS/#")
    client.subscribe("test")
    client.publish("house/main-light", "OFF")

    # The callback for when a PUBLISH message is received from the server.


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


client = mqtt.Client("my-client")
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.1.1", port=1883, keepalive=60)
# client.loop_start()
# client.loop_stop()
client.loop_forever()
print ("end")


if __name__ == "__main__":
    pass
