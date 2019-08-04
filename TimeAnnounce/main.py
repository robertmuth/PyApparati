#!/usr/bin/env python3
# coding=utf-8
# https://github.com/ruisebastiao/pySUNXI

import SUNXI_GPIO as GPIO
import time


import time_announce

# PD0 =  LCD-D0 = pin 1
# GND = pin 2
# PD1 =  LCD-D1 = pin 4
# PD2 =  LCD-D2 = pin 3


SWITCH = GPIO.PD0

GPIO.init()

GPIO.setcfg(SWITCH, GPIO.IN)

langs = [
        time_announce.EN,
        time_announce.DE,
        time_announce.FR,
        time_announce.ES,
]


while True:
        x = GPIO.input(SWITCH)
        if  x == 0:
                time.sleep(.5)
                continue

        l = langs.pop(0)
        langs.append(l)
        time_announce.SayTime(l)


