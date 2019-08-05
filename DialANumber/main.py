#!/usr/bin/python3

import logging
import os
import time
import glob
import signal
import datetime

import Pytorinox.audio_alsa as audio
import Pytorinox.bme280 as bme280
import Lib.rotary_dial as rotary_dial
import Pytorinox.framebuffer as framebuffer

import sound_clips
import video
import webserver

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

MAX_DELAY_BETWEEN_NUMBERS_SEC = 3

PIN_LIFTED = 15
PIN_TRIGGER = 14


DEFAULT_ACTION = (None, None, None)


# 2	ABC
# 3	DEF
# 4	GHI
# 5	JKL
# 6	MNO
# 7	PQRS (on older telephones, PRS)
# 8	TUV
# 9	WXYZ (on older telephones, WXY)

ACTION_MAP = {
     (0, 0): ("Shutdown", "shutdown", None),
}


MENU = [
]

 

def DateString():
    now = datetime.datetime.now()
    return now.strftime("  %d %b %Y  %H:%M")
    
class Task:

    def __init__(self, clips):
        self._active_task = None
        self.clips = clips
        self.start = 0
        self.message = None

    def GetMessage(self):
        if self.start + 5.0 < time.time():
            return None
        return self.message
        
    def Shutdown(self):
        os.system("sudo shutdown now")
        logging.info("Shutting down")
    
    def Dispatch(self, numbers):
        msg, action, args = ACTION_MAP.get(tuple(numbers), DEFAULT_ACTION)
        self.message = msg
        self.state = time.time()
        if msg is None:
            logging.info("no action match for: %s", numbers)
            return

        print ("ACTION: ", action)
        if action == "Clip":
            self.clips.PlayRandom(args)

        elif action == "shutdown":
            self.Shutdown()

        else:
            logging.error("unknown action: [%s]", action)

class Actions:

    def __init__(self, video, audio, sensor, clips):
        self.task = Task(clips)
        self.video = video
        self.audio = audio
        self.sensor = sensor
        self.activeNumbers = []
        self.last_dialed = 0.0
        self.dialing = False
        # text associated with the current activity
        self.pending = None

    # if there was not activity in a while
    # collect all accumulated numbers and trigger an action
    def MaybeCleanHistory(self, now):
        if self.dialing:
            return
        if not self.activeNumbers:
            return
        if self.last_dialed + MAX_DELAY_BETWEEN_NUMBERS_SEC > now:
            return
        logging.info("history cleaning %s", self.activeNumbers)
        # make existing number disappear visually
        src = chr(ord('0') +  self.activeNumbers[-1])
        dst = " "
        self.pending = [src, dst, 0.0]
        self.task.Dispatch(tuple(self.activeNumbers))
        self.activeNumbers = []

    def DialingActivity(self, num):
        if num == 0:
            self.dialing = True
            return
        if num < 0:
            return
        self.last_dialed = time.time()
        self.dialing = False
        num %= 10
        self.audio.Play("%s" % num)
        dst = chr(ord('0') + num)
        src = " "
        if self.activeNumbers:
            src = chr(ord('0') +  self.activeNumbers[-1])
        logging.info("DIALED: %d, active: %s", num, self.activeNumbers)
        self.pending = [src, dst, 0.0]
        self.activeNumbers.append(num)

    # Must be called periodically
    def Periodic(self):
        now = time.time()
        self.MaybeCleanHistory(now)
        if self.pending:
            logging.info("morphing: [%s] [%s] %.2f", *self.pending)
            self.video.Morphed(*self.pending)
            p = self.pending[2]
            if p == 1.0:
                self.pending = None
            else:
                self.pending[2] = min(1.0, p + 0.1)
        elif self.dialing or self.last_dialed + MAX_DELAY_BETWEEN_NUMBERS_SEC > now:
            if self.activeNumbers:
                pass
            else:
                self.video.Menu(MENU)
                #self.video.Message("Welcome",
                #               self.sensor.RenderMeasurements(),
                #               DateString())                
        else:
            m = self.task.GetMessage()
            if m:
                msg1, msg2 = m.split(":")
                self.video.Message(msg1, msg2, DateString())

            else:
                self.video.ShowTime(now, 10)                

class FPS:

    def __init__(self, now):
        self.n = 0
        self.measure = [now] * 120 

    def trigger(self, now):
        self.n += 1
        if self.n % len(self.measure) == 0:
            print ("fps: %f" % (len(self.measure) / (now - self.measure[0])))
        self.measure.pop(0)
        self.measure.append(now)
        
def main(video, audio, sensor, clips):
    global MENU, ACTION_MAP
    act = Actions(video, audio, sensor, clips)
    for n, g in enumerate(clips.Genres()):
        MENU.append("%d %s" % (n+1, g))
        ACTION_MAP[(n+1,)] = ("%s:" % g, "Clip", g)
    last_trigger = True
    last_resting = True
    lastchange = time.time()
    fps = FPS(time.time())
    rot = rotary_dial.RotaryDial(PIN_LIFTED, PIN_TRIGGER, act.DialingActivity)
    
    while True:
        act.Periodic()
        time.sleep(0.05)


logging.basicConfig(level=logging.INFO)
device = framebuffer.Framebuffer(1)
v = video.Video(device, 128, 64)
a = audio.Audio(glob.glob("../SoundNumbers/?.wav"))
d = bme280.I2CDevice(addr=0x76, debug=False)
s = bme280.SensorBME280(d)
c = sound_clips.SoundClips("/home/pi/AudioClips")

webserver.RunServerInThread(8888, s)
main(v, a, s, c)
