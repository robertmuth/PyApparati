#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Input device helper

Input device helper for  /dev/input/event* devices.
Useful for many USB input devices, including:
keyboards, mice, touchscreen, joysticks

This is in the experimentation stage
https://www.kernel.org/doc/Documentation/input/event-codes.txt
http://www.infradead.org/~mchehab/kernel_docs_pdf/linux-input.pdf

https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
https://elixir.bootlin.com/linux/latest/source/include/uapi/asm-generic/ioctl.h
"""

import ctypes
import os
import sys
import struct
import collections

if sys.maxsize > 1 << 32:
    _EVENT_FORMAT = "@QQhhi"
else:
    _EVENT_FORMAT = "@IIhhi"

_EVENT_LENGTH = struct.calcsize(_EVENT_FORMAT)

EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03
EV_MSC = 0x04
EV_SW = 0x05
EV_LED = 0x11
EV_SND = 0x12
EV_REP = 0x14
EV_FF = 0x15
EV_PWR = 0x16
EV_FF_STATUS = 0x17
EV_MAX = 0x1f


def _ToStringMap(prefix):
    return {val: var
            for var, val in globals().items()
            if var.startswith(prefix)}


EV_TO_STRING_MAP = _ToStringMap("EV_")

Event = collections.namedtuple("Event", ["sec", "usec", "type", "code", "value"])
AbsInfo = collections.namedtuple("AbsInfo", ["value", "minimum", "maximum","fuzz","flat","resolution"])


def BytesToEvent(bytes: bytes) -> Event:
    return Event(*struct.unpack(_EVENT_FORMAT, bytes))


def EventToBytes(event: Event) -> bytes:
    return struct.pack(_EVENT_FORMAT, *event)

def BytesToAbsInfo(bytes: bytes) -> AbsInfo:
    return AbsInfo(*struct.unpack("iiiiii", bytes))





def _ToBits(val: str):
    ints = [int(x, 16) for x in val.split()]
    out = set()
    for n, i in enumerate(reversed(ints)):
        bit = n * 64
        while i != 0:
            if i & 1:
                out.add(bit)
            bit += 1
            i >>= 1
    return out

# IOCTL hacks
_IOCTL_DIR_NONE = 0
_IOCTL_DIR_READ = 2
_IOCTL_DIR_WRITE = 1

libc = ctypes.CDLL('libc.so.6')


# accurate for most platforms
def ioctl_magic(dir: int, type: int, nr: int, size: int):
    return nr | type << 8 | size << 16 | dir << 30


class HID(object):

    def __init__(self, path):
        self.properties = {}
        self.capabilities = {}
        self.absinfo = {}
        self.state = {}
        self.new_events = {}
        no = path.replace("/dev/input/event", "")
        for line in open("/sys/class/input/event%s/device/uevent" % no).readlines():
            tag, val = line.split("=", 1)
            val = val.strip()
            self.properties[tag] = val
            if tag == "EV":
                for c in _ToBits(val):
                    if c not in self.capabilities:
                        self.capabilities[c] = None
            elif tag == "LED":
                self.capabilities[EV_LED] = _ToBits(val)
            elif tag == "MSC":
                self.capabilities[EV_MSC] = _ToBits(val)
            elif tag == "ABS":
                self.capabilities[EV_ABS] = _ToBits(val)
            elif tag == "REL":
                self.capabilities[EV_REL] = _ToBits(val)
            elif tag == "KEY":
                self.capabilities[EV_KEY] = _ToBits(val)

        print(self.properties)
        print({EV_TO_STRING_MAP[k]: v for k, v in self.capabilities.items()})
        self.fd = os.open(path, os.O_RDWR, 0o666)
        for abs in self.capabilities[EV_ABS]:
            b = bytes(24)
            magic = ioctl_magic(_IOCTL_DIR_READ, ord('E'), 0x40 + abs, len(b))
            assert  0 == libc.ioctl(self.fd, magic, b)
            self.absinfo[abs] = BytesToAbsInfo(b)
        print (self.absinfo)

    def read_next_event(self) -> Event:
        bytes = os.read(self.fd, _EVENT_LENGTH)
        event = BytesToEvent(bytes)
        k = (event.type, event.code)
        self.state[k] = event
        self.new_events[k] = event
        return event


if __name__ == "__main__":
    import glob

    def DumpEvents(path):
        hid = HID(path)

        while True:
            event = hid.read_next_event()
            # print(event)
            print ("\n" * 20)
            for k, v in sorted(hid.state.items()):
                print (k, v.value)


    def DumpInputDevices():
        for d in glob.glob("/dev/input/event*"):
            print(d)
            try:
                hid = HID(d)
            except Exception as err:
                print (err)

    if len(sys.argv) == 2:
        print("dumping events for ", sys.argv[1])
        DumpEvents(sys.argv[1])
    else:
        DumpInputDevices()
