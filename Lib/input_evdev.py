#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Input device helper

Input device helper for  /dev/input/event* devices.
Useful for many USB input devices, including:
keyboards, mice, touchscreen, joysticks

This is in the experimentation stage
https://www.kernel.org/doc/Documentation/input/event-codes.txt

https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
"""

import evdev

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


class HID(object):
    """
    Does all the book keeping for events

    This class can be used in two modes:
    """

    def __init__(self, capabilities):
        # read-only
        self.code_type_to_name = {}
        self.leds = {}
        self.abs_info = {}  # evdev.AbsInfo

        for key, val in capabilities.items():
            ev_type = key[-1]
            for v in val:
                # deal with:
                # TYPE ('EV_ABS', 3)
                #   CODE (('ABS_X', 0), AbsInfo(value=1745, min=0, max=4095, fuzz=0, flat=0, resolution=0))

                if ev_type == evdev.ecodes.EV_ABS:
                    names, ev_code = v[0]
                    self.abs_info[(ev_type, ev_code)] = v[-1]
                else:
                    names, ev_code = v

                if type(names) != list:
                    names = [names]
                self.code_type_to_name[(ev_type, ev_code)] = names
                if ev_type == evdev.ecodes.EV_LED:
                    self.leds[ev_code] = names
        #
        self.state = {}
        self.new_events = {}

    def clear_new_events(self):
        self.new_events.clear()

    def process_event(self, event: evdev.InputEvent):
        k = (event.type, event.code)
        self.state[k] = event
        self.new_events[k] = event


if __name__ == "__main__":
    import sys


    def DumpEvents(path):
        device = evdev.InputDevice(path)
        capabilities = device.capabilities(True)
        print(device.name, device.phys)
        for key, val in capabilities.items():
            print("TYPE", key)
            for v in val:
                print("   CODE", v)
        hid = HID(capabilities)
        for event in device.read_loop():
            hid.process_event(event)
            print("\n" * 20)
            for k, v in sorted(hid.state.items()):
                print(hid.code_type_to_name[k][0], v.value)

    if len(sys.argv) == 2:
        print("dumping events for ", sys.argv[1])
        DumpEvents(sys.argv[1])
    else:
        if len(evdev.list_devices()) == 0:
            print("no devices found - maybe you need to be root")
        else:
            print("Not device path specified. Available devices:")

        for path in evdev.list_devices():
            device = evdev.InputDevice(path)
            print(path, device.name, device.phys, list(device.capabilities(True).keys()))
