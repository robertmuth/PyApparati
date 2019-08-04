#!/usr/bin/python3
# coding=utf-8
import sys
import time
import os

# speaking clock
# https://en.wikipedia.org/wiki/Speaking_clock

# English
# http://www.phworld.org/sounds/modern/timetemp/
# "at the tone time will 8 25 and 10 seconds/exactly"

# German
#
# French
# http://www.horlogeparlante.com/
#"il sera seize heur cinq minute tres second"


# Spanish
#  al oír la señal serán las 14 horas 30 minutos
# Cuando oiga la señal serán (exactamente) las diez y diez
# Cuando suene  la señal, serán"
# Al oír el tono serán las 11:59 y 20 segundos.

EN = ("en-GB", ". . At the tone. Time will be %d, %d, and exactly %d seconds.")
DE = ("de-DE", ". . Beim nächsten Gongschlag ist es %d Uhr, %d Minuten und %d Sekunden.")
FR = ("fr-FR", ". . Au prochaine top il sera %d heures, %d minutes, %d secondes.")
ES = ("es-ES", ". . Al oír el tono serán las %d horas, %d minutos y %d segundos.")


def SuitableTimeInTheFuture(delta):
    earliest = delta + time.time()
    for i in range(10):
        now = time.localtime(i + earliest)
        print (now.tm_sec, now.tm_sec % 10)
        if now.tm_sec % 10 == 0:
            return now
    assert False


def Gong(now):
    while time.localtime() < now:
        time.sleep(0.5)
    os.system("aplay ../Sounds/Tone.wav")


def SayTime(lang):
    now = SuitableTimeInTheFuture(7)
    text = lang[1] % (now.tm_hour, now.tm_min, now.tm_sec)
    cmd = "pico2wave --lang=%s --wave=/tmp/xxx.wav   '%s'" % (lang[0], text)
    os.system(cmd.encode("utf-8"))
    os.system("sox -G /tmp/xxx.wav  /tmp/yyy.wav channels 1 rate 44100")
    os.system("aplay /tmp/yyy.wav")
    Gong(now)


if __name__ == "__main__":
    SayTime(ES)
    SayTime(DE)
    SayTime(EN)
    SayTime(FR)
