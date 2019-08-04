#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""


"""

import logging
from queue import Queue
from threading import Thread
import time
import RPi.GPIO as GPIO
import os

GPIO.setmode(GPIO.BCM)

from rotary_encoder import RotarySwitch
from menu import Menu
import paho.mqtt.client as mqtt


from dali_clock import LoadMorphFont,  DaliClock
from framebuffer import Framebuffer

from PIL import Image, ImageDraw, ImageFont


def SumWidth(imgs, spacing):
    width = -spacing
    for img in imgs:
        width += img.size[0] + spacing

    return width


def Offset(t, image_dim, object_dim, speed=4.0):
    deltax = image_dim[0] - object_dim[0]
    deltay = image_dim[1] - object_dim[1]
    offsetx = (t*speed) % (2.0 * deltax)
    if offsetx > deltax:
        offsetx = 2 * deltax - offsetx
    offsety = (t*speed) % (2.0 * deltay)
    if offsety > deltay:
        offsety = 2 * deltay - offsety
    return offsetx, offsety


def UpdateClock(t, clock, draw, dim):
    imgs = clock.GetBitmapsForTime(t, 20, .3)
    line1 = imgs[0:5]
    width1 = SumWidth(line1, 2)
    height = line1[0].size[1]
    line2 = imgs[6:]
    width2 = SumWidth(line2, 2)

    offset = Offset(t, dim, (width1,  2 * height + 2))
    x = offset[0]
    y = offset[1]
    for img in line1:
        draw.bitmap((x, y), img, fill="#fff")
        x += img.size[0] + 2

    x = (width1 - width2) / 2 + offset[0]
    y = height + 2 + offset[1]
    for img in line2:
        draw.bitmap((x, y), img, fill="#fff")
        x += img.size[0] + 2


MODE_CLOCK = "clock"
MODE_MENU = "menu"
TIME_QUANTUM = 0.04
ACTION_LEFT = "left"
ACTION_RIGHT = "right"
ACTION_BUTTON = "button"


_ENTRIES = [
    ("wnyc-fm", "play_radio/192.168.1.163",
     "http://www.wnyc.org/stream/wnyc-fm939/mp3.pls"),
    ("wnyc-am", "play_radio/192.168.1.163",
     "http://www.wnyc.org/stream/wnyc-am820/aac.pls"),
    ("stop",    "stop_radio/192.168.1.163", ""),
    ("kuaz-jazz", "play_radio/192.168.1.163",
     "http://streaming.azpm.org/kuaz192.mp3.m3u"),
    ("kuat", "play_radio/192.168.1.163",
     "http://streaming.azpm.org/kuat192.mp3.m3u"),
    ("on-the-media", "play_radio/192.168.1.163",
     "http://feeds.wnyc.org/onthemedia?format=rss"),
    ("american-life", "play_radio/192.168.1.163",
     "http://feed.thisamericanlife.org/talpodcast"),

    ("groovesalad", "play_radio/192.168.1.163",
     "http://somafm.com/groovesalad256.pls"),
    ("dronezone", "play_radio/192.168.1.163",
     "http://somafm.com/dronezone256.pls"),
    ("u80s",  "play_radio/192.168.1.163", "http://somafm.com/u80s256.pls"),
    ("defcon-radio", "play_radio/192.168.1.163", "http://somafm.com/defcon256.pls"),
    ("cliqhop", "play_radio/192.168.1.163", "http://somafm.com/cliqhop256.pls"),
    ("dubstep", "play_radio/192.168.1.163", "http://somafm.com/dubstep256.pls"),

    ("bootliquor", "play_radio/192.168.1.163",
     "http://somafm.com/bootliquor320.pls"),
    ("70s", "play_radio/192.168.1.163", "http://somafm.com/seventies320.pls"),
    ("lush", "play_radio/192.168.1.163", "http://somafm.com/lush130.pls"),
    ("secret-agent", "play_radio/192.168.1.163",
     "http://somafm.com/secretagent130.pls"),
    ("shutdown", None, None),
    ("reboot", None, None),
]


def main():
    counter = 3.0
    mode = MODE_CLOCK
    font, font_dim = LoadMorphFont("DaliFonts/", "F.xbm")
    print("FONT_DIM", font_dim)
    clock = DaliClock(font, font_dim, "%H:%M:%S")
    device = Framebuffer(1)
    image = Image.new("RGBA", (128, 128))
    draw = ImageDraw.Draw(image)
    menu_font = ImageFont.truetype("Fonts/code2000.ttf", 20)
    queue = Queue()

    menu = Menu(menu_font, 6, 128, 21, [
                e[0] for e in _ENTRIES], active_entry_index=0, y_offset=5)

    def on_connect(client, userdata, rc, dummy):
        print("connected to mqtt broker")

    mqtt_client = mqtt.Client("my-client")
    mqtt_client.on_connect = on_connect
    #mqtt_client.on_message = on_message
    while True:
        try:
            mqtt_client.connect("192.168.1.1", port=1883, keepalive=60)
            break
        except:
            pass

    mqtt_client.loop_start()

    def worker():

        while True:
            item = queue.get()
            if item is None:
                break
            nonlocal mode, counter
            counter = 3.0
            if mode != MODE_MENU:
                mode = MODE_MENU
                menu.active_entry_index = 0
            elif item == ACTION_BUTTON:
                entry = _ENTRIES[menu.active_entry_index]
                print (entry)
                if entry[0] == "shutdown":
                    device.off()
                    os.system("sudo shutdown now")
                elif entry[0] == "reboot":
                    device.off()
                    os.system("sudo reboot")
                else:
                    topic = entry[1]
                    url = entry[2]
                    mqtt_client.publish(topic, url)
            else:
                menu.move(item == ACTION_LEFT)

            start = time.time()
            draw.rectangle(((0, 0), image.size), fill=0)
            menu.draw(draw)
            stop = time.time()
            device.show(image)
            stop2 = time.time()
            print ("refresh %.3f %.3f" % (stop2 - start, stop - start))
            queue.task_done()

    t = Thread(target=worker)
    t.start()

    def _rotary_triggered(direction):
        nonlocal queue
        queue.put(ACTION_LEFT if direction else ACTION_RIGHT)

    rotary = RotarySwitch(15, 14, _rotary_triggered)

    def _button_triggered(direction):
        #nonlocal queue
        queue.put(ACTION_BUTTON)

    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(
        18, GPIO.FALLING, callback=_button_triggered, bouncetime=400)

    while True:
        # print ("LOOP", mode, counter)
        time.sleep(TIME_QUANTUM)
        if mode == MODE_MENU:
            counter -= TIME_QUANTUM
            if counter < 0.0:
                # print ("back to clock")
                mode = MODE_CLOCK
        elif mode == MODE_CLOCK:
            t = time.time()
            draw.rectangle(((0, 0), image.size), fill=0)
            UpdateClock(t, clock, draw, image.size)
            device.show(image)
        else:
            assert False


if __name__ == "__main__":
    import time
    logging.basicConfig(level=logging.INFO)
    try:
        main()
    except KeyboardInterrupt:
        pass
