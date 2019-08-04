#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

"""

import logging

from PIL import Image, ImageDraw, ImageFont

import PiLib.dali_clock as dali_clock

# ("tiny.ttf", 6),
# ("ProggyTiny.ttf", 16),
# ("creep.bdf", 16),
# ("miscfs_.ttf ", 12),
# ("FreePixel.ttf", 12)]:



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

def SumWidth(imgs, spacing):
    width = -spacing
    for img in imgs:
        width +=  img.size[0] + spacing
    return width
                        

class Video:

    def __init__(self, device, w, h):
        self._device = device
        self._last_screen = None
        self._font = ImageFont.truetype("Fonts/code2000.ttf", 30)
        self._menu_font = ImageFont.truetype("Fonts/code2000.ttf", 12)
        font_dali = dali_clock.LoadMorphFont("PiLib/DaliFonts/", "E.xbm")
        self._dali_string = dali_clock.DaliString(*font_dali)
        font_clock = dali_clock.LoadMorphFont("PiLib/DaliFonts/", "G.xbm")
        self._dali_clock = dali_clock.DaliClock(*font_clock, "%H:%M")
        self._image = Image.new("RGB", (w, h))
        self._draw = ImageDraw.Draw(self._image)

    def Morphed(self, c1, c2, frac):
        bitmaps = self._dali_string.GetBitmapsForStrings(c1, c2, frac)
        assert len(bitmaps) == 1
        self._last_screen = (c1, c2, frac)
        self._Clear()
        self._draw.bitmap((40,0), bitmaps[0], fill="blue")
        self._device.show(self._image)

    def ShowTime(self, t, steps):
        self._Clear()
        self._last_screen = None
        bitmaps = self._dali_clock.GetBitmapsForTime(t, steps, 0)
        width = SumWidth(bitmaps, 2)
        height = bitmaps[0].size[1]
        offset = Offset(t, self._image.size, (width, height)) 
        x = offset[0]
        y = offset[1]
        for img in bitmaps:
            self._draw.bitmap((x,y), img, fill="#111")
            x += img.size[0] + 2
        self._device.show(self._image)                                                                         
        
    def _Clear(self):
        self._draw.rectangle(((0,0), self._image.size), fill="#000")

        
    def Message(self, msg1, msg2, msg3):
        if self._last_screen == (msg1, msg2, msg3):
            return
        self._last_screen = (msg1, msg2, msg3)
        self._Clear()
        self._draw.text((0, 0), msg1, fill="yellow", font=self._font)
        self._draw.text((0, 35), msg2, fill="yellow")
        self._draw.text((0, 50), msg3, fill="yellow")
        self._device.show(self._image)        

    def Menu(self, msgs):
        self._last_screen = msgs
        self._Clear()
        for i, msg in enumerate(msgs):
            x = 0
            y = i * 12
            if i >= 5:
                x += 64
                y -= 60 
            self._draw.text((x, y), msg, fill="yellow", font=self._menu_font)
        self._device.show(self._image)        
            
if __name__ == "__main__":
    import PiLib.framebuffer as framebuffer
    import time
    
    def main():
        logging.basicConfig(level=logging.INFO)
        fb = framebuffer.Framebuffer(1)
        logging.info("Size %s %d", fb.size, fb.bits_per_pixel)
        video = Video(fb, 128, 64)
        video.Message("Welcome", "0123456789012345", "0123456789012345")

        chars = [" ", "0", " ", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        font, font_dim = dali_clock.LoadMorphFont("PiLib/DaliFonts/", "E.xbm")
        for n, c1 in enumerate(chars):
            c2 = chars[(n + 1) % len(chars)]
            for step in range(21):
                video.Morphed(c1, c2, step/ 20.0)

    
        time.sleep(1.5)
        for i in range(1000):
            video.ShowTime(time.time(), 10)
            time.sleep(0.2)


        device.off()
            

    main()
