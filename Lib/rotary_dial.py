#!/usr/bin/env python3

import logging
import time

import RPi.GPIO as GPIO


def CleanupTriggers(now, triggers):
    print ("")
    for t in triggers:
        delta = now - t[0]
        if delta < 0.05: continue
        print (delta, t[1])

class RotaryDial(object):

    def __init__(self, pin_lifted, pin_trigger, cb_dialed):
        self._pin_lifted = pin_lifted
        self._pin_trigger = pin_trigger
        self._cb_dialed = cb_dialed
        self._idle = True
        GPIO.setup(pin_lifted, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_trigger, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # do not change these lightly - these were carefully tweaked
        GPIO.add_event_detect(pin_lifted, GPIO.BOTH, callback=self._lifted, bouncetime=25)
        GPIO.add_event_detect(pin_trigger, GPIO.RISING, callback=self._trigger, bouncetime=10)
        self._triggers = []
        
    def _lifted(self, pin):
        now = time.time()
        idle =  GPIO.input(pin)
        if idle == self._idle:
            return
        self._idle = idle
        logging.info("idle: %d", idle)
        # we just became idle
        if self._idle:
            self._cb_dialed(len(self._triggers))
        else:
            self._cb_dialed(0)
        self._triggers = []


    def _trigger(self, pin):
        ts = time.time()
        if not self._idle:
            v  = GPIO.input(pin)
            if v:
                self._triggers.append((ts, v))
        
if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    GPIO.setmode(GPIO.BCM)
    def dialed(n):
        print ("dialed", n)
        
    def main():
        rot = RotaryDial(15, 14, dialed)
        time.sleep(100)

    main()
