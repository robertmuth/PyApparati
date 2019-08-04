#!/usr/bin/env python3

import RPi.GPIO as GPIO

class RotaryDial(object):

    def __init__(self, pin_lifted, pin_trigger, cb_dialed):
        self._pin_lifted = pin_lifted
        self._pin_trigger = pin_trigger
        self._cb_dialed = cb_dialed
        GPIO.setup(pin_lifted, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pin_trigger, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin_lifted, GPIO.BOTH, callback=self._lifted, bouncetime=200)
        GPIO.add_event_detect(pin_trigger, GPIO.BOTH, callback=self._trigger, bouncetime=80)
        self._count = 0
        
    def _lifted(self, pin):
        if self._count > 0:
            self._cb_dialed(self._count)
            self._count = 0
        else:
            self._cb_dialed(0)

    def _trigger(self, pin):
        lifted = GPIO.input(self._pin_lifted) == GPIO.LOW
        if lifted:
            self._count += 1
        self._cb_dialed(-1)            
        
        
if __name__ == "__main__":
    import time
    GPIO.setmode(GPIO.BCM)
    def dialed(n):
        print ("dialed", n)
        
    def main():
        rot = RotaryDial(15, 14, dialed)
        time.sleep(100)

    main()
