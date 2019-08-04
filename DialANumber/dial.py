#!/usr/bin/python3

import logging
import os
import time
import glob
import signal
import datetime

import PiLib.audio_alsa as audio
import PiLib.bme280 as bme280
import PiLib.rotary_dial as rotary_dial
import PiLib.framebuffer as framebuffer

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

c2n = {
    "a": 2,
    "b": 2,
    "c": 2,    
    "d": 3,    
    "e": 3,    
    "f": 3,
    "g": 4,    
    "h": 4,    
    "i": 4,    
    "j": 5,    
    "k": 5,    
    "l": 5,    
    "m": 6,    
    "n": 6,    
    "o": 6,    
    "p": 7,    
    "q": 7,    
    "r": 7,    
    "s": 7,    
    "t": 8,    
    "u": 8,    
    "v": 8,    
    "w": 9,    
    "x": 9,
    "y": 9,    
    "z": 9,    
}

def C2N(s):
    return tuple([c2n[c] for c  in s.lower() ])

def Radio(a, b):
    return (a, "Radio", b)

def ShutdeonNow():
    return (a, "Radio", b)

ACTION_MAP = {
    (1,): ("", "Kill", None),
    (0, 0): ("Shutdown", "shutdown", None),
    (0,): Radio("SomaFM:SecretAgent", "http://somafm.com/secretagent130.pls"),
    C2N("N"): Radio("WNYC:fm:", "http://www.wnyc.org/stream/wnyc-fm939/mp3.pls"),
    C2N("J"): Radio("WBGO:Jazz", "http://wbgo.streamguys.net/listen.pls"),
    C2N("C"): Radio("KUAT:Classic", "http://streaming.azpm.org/kuat192.mp3.m3u"),
    #
    (9,): Radio("BBC: News", "http://bbcwssc.ic.llnwd.net/stream/bbcwssc_mp1_ws-eieuk"),
    #
    #
    (8,): Radio("KCSM:Jazz", "https://kcsm.org/KCSM-iTunes-SNS.pls"),
    #
    C2N("P"): Radio("Paradise:", "http://www.radioparadise.com/musiclinks/rp_192.m3u"),
    C2N("D"): Radio("SomaFM:DroneZone", "http://somafm.com/dronezone130.pls"),
    C2N("G"): Radio("SomaFM:GroveSalad", "http://somafm.com/startstream=groovesalad130.pls"),
}


MENU = [
    "1 <stop>",
    "2 KUAT",
    "3 Drone",
    "4 Groove",
    "5 WBGO",
    "6 WNYC",
    "7 Paradise",
    "8 KCSM",
    "9 BBC",
    "0 Secret",
]
 

def DateString():
    now = datetime.datetime.now()
    return now.strftime("  %d %b %Y  %H:%M")
    
class Task:

    def __init__(self):
        self._active_task = None
        self.message = None
    def Kill(self):
        if self._active_task:
            os.kill(self._active_task, signal.SIGKILL)
            self._active_task = None
        
    def Radio(self, url):
        self.Kill()
        self._active_task = os.spawnlp(os.P_NOWAIT, "cvlc", "-v", url)
        logging.info("JOB: %d", self._active_task)

    def Shutdown(self):
        os.system("sudo shutdown now")
        logging.info("Shutting down")
    
    def Dispatch(self, numbers):
        msg, action, args = ACTION_MAP.get(tuple(numbers), DEFAULT_ACTION)
        self.message = msg
        if msg is None:
            logging.info("no action matc forh: %s", numbers)
            return

        print ("ACTION: ", action)
        if action == "Kill":
            self.Kill()
        elif action == "Radio":
            self.Radio(args)
        elif action == "shutdown":
            self.Shutdown()

        else:
            logging.error("unknown action: [%s]", action)

class Actions:

    def __init__(self, video, audio, sensor):
        self.task = Task()
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
            if self.task.message:
                msg1, msg2 = self.task.message.split(":")
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
        
def main(video, audio, sensor):
    act = Actions(video, audio, sensor)
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
a = audio.Audio(glob.glob("PiLib/SoundNumbers/?.wav"))
s = bme280.SensorBME280()

webserver.RunServerInThread(8888, s)
main(v, a, s)
