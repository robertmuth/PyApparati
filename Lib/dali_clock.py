#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
"""

import logging
import time

from typing import Dict, Tuple

from .morph_digits import SegmentedImage
from .xbm import ParseImage
from PIL import Image


def DumpMorph(img):
    for r in img:
        print("".join(r))


def ShowChar(data, img):
    w = len(img[0])
    for y, row in enumerate(img):
        for x in range(w):
            color = 0
            if len(row) > x and row[x] != " ":
                color = 1
            data[x + y * w] = color


def ImgToAscii(img: Image) -> str:
    w, h = img.size
    data = img.getdata()
    out = []
    for n, x in enumerate(data):
        if n % w == 0:
            out.append("")
        out[-1] += "*" if x else " "
    return "\n".join(out)


_MORPH_CHARS = {
    ":": "colon",
    "/": "slash",
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine"
}


def LoadMorphFont(prefix, suffix):
    font = {}
    wMax = 0
    hMax = 0
    for c in _MORPH_CHARS:
        fn = prefix + _MORPH_CHARS[c] + suffix
        logging.info("processing: %s", fn)
        img = ParseImage(open(fn).read())
        font[c] = SegmentedImage(img)
        dim = len(img[0]), len(img)
        logging.info("dimension: %dx%d" % dim)
        if dim[0] > wMax:
            wMax = dim[0]
        if dim[1] > hMax:
            hMax = dim[1]

    empty = [" "] * wMax
    font[" "] = SegmentedImage([empty] * hMax)
    # DumpMorph(font[" "].ToImage("*"))
    return font, (wMax, hMax)


class DaliString(object):

    def __init__(self, font: Dict[str, SegmentedImage], font_dim):
        self._font = font
        self._font_dim = font_dim
        self._morph_cache = {}

    def Morphed(self, c1, c2, step):
        key = (c1, c2, step)
        if key not in self._morph_cache:
            seg1 = self._font[c1]
            seg2 = self._font[c2]
            seg = seg1.Merge(seg2, step)
            w, h = seg.get_size()
            data = [0] * (w * h)
            seg.ToImageData(data)

            img = Image.new("1", seg.get_size())
            img.putdata(data)
            self._morph_cache[key] = img
        return self._morph_cache[key]

    def GetBitmapsForStrings(self, t1: str, t2: str, frac: float):
        assert len(t1) == len(t2)
        return [self.Morphed(c1, c2, frac) for c1, c2 in zip(t1, t2)]
    
    
class DaliClock(object):

    def __init__(self, font: Dict[str, SegmentedImage], font_dim, time_fmt="%H:%M:%S"):
        self._dali_string = DaliString(font, font_dim)
        self._time_fmt = time_fmt
        self._last_time_str = ""
        self._last_time_bitmaps = None

    def GetBitmapsForTime(self, secs: float, steps: int, resting: float):
        t1 = time.strftime(self._time_fmt, time.localtime(secs))
        t2 = time.strftime(self._time_fmt, time.localtime(secs + 1.0))
        if t2 == self._last_time_str:
            return self._last_time_bitmaps
        assert len(t1) == len(t2)
        # get the fractional part
        f = secs - int(secs)
        # the animation happens between [0: 1.0 - resting]
        f = f / (1.0 - resting)
        if f > 1.0:
            f = 1.0
        # snap fraction to steps to improve cache utilization
        frac = int(f * steps) / steps

        self._last_time_bitmaps = self._dali_string.GetBitmapsForStrings(t1, t2, frac)
        self._last_time_str = t1
        return self._last_time_bitmaps

if __name__ == "__main__":
    def main():
        font, font_dim = LoadMorphFont("DaliFonts/", "F.xbm")
        print("FONT_DIM", font_dim)
        # return
        clock = DaliClock(font, font_dim)
        while True:
            t = time.time()
            data = clock.GetBitmapsForTime(t, 20, .3)
            print(ImgToAscii(data[-1]))


    main()
