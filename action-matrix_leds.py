#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from matrixio_hal import everloop
from collections import deque
import time

red = everloop.Image()
blue = everloop.Image()
black = everloop.Image()
for i in range(0, len(red.leds)):
    red.leds[i].red = 20
    blue.leds[i].blue = 20

def on_message(client, userdata, msg):
    print(msg.topic)
    if msg.topic == 'hermes/asr/startListening':
        red.render()
    elif msg.topic == 'hermes/hotword/toggleOn':
        black.render()
    elif msg.topic == 'hermes/tts/say':
        blue.render()

def on_connect(client, userdata, flags, rc):
    print('subscribing ....')
    client.subscribe('hermes/hotword/toggleOn')
    client.subscribe('hermes/asr/startListening')
    client.subscribe('hermes/tts/say')

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect('localhost', 1883, 60)
client.loop_forever()
