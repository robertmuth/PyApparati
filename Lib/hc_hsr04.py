#!/usr/bin/python3
# hc sr04(+)
# ultrasound distance sensor
import time
import RPi.GPIO as GPIO


_TRIGGER_LENGTH_SEC = 0.00001

_SPEED_OF_SOUND_M_PER_SEC = 343


class DistanceSensor():

    def __init__(self, pin_echo, pin_trig):
        self._pin_echo = pin_echo
        self._pin_trig = pin_trig
        GPIO.setup(pin_trig, GPIO.OUT)
        GPIO.setup(pin_echo, GPIO.IN)
        #
        GPIO.output(pin_trig, False)

    def _Triger(self):
        GPIO.output(self._pin_trig, True)
        time.sleep(_TRIGGER_LENGTH_SEC)
        GPIO.output(self._pin_trig, False)

    def _ListenAndWait(self, time_out_sec=2.0):
        listen_dead_line = time.time() + time_out_sec
        pulse_start = time.time()
        pulse_end = time.time()
        while GPIO.input(self._pin_echo) == 0:
            pulse_start = time.time()
            if pulse_start > listen_dead_line:
                return None
        while GPIO.input(self._pin_echo) == 1:
            pulse_end = time.time()
            if pulse_end > listen_dead_line:
                return None

        return pulse_end - pulse_start

    def DistanceInMeter(self):
        self._Triger()
        duration = self._ListenAndWait()
        if duration is None:
            return None
        return _SPEED_OF_SOUND_M_PER_SEC * 0.5 * duration


if __name__ == "__main__":
    def main():
        GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
        sensor = DistanceSensor(5, 3)

        while True:
            print ("Distance %sm" % sensor.DistanceInMeter())
            time.sleep(1.0)
    main()
