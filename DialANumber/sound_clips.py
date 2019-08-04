#!/usr/bin/python3

import logging
import glob
import os
import random

def ReadGenres(dir):
    out = {}
    genre_dirs =  glob.glob(dir + "/*/")
    for d in  genre_dirs:
        clips = glob.glob(d + "*")
        genre = os.path.basename(os.path.dirname(d))
        logging.info("%s %s: %d", d, genre, len(clips))
        out[genre] = clips    
    return out

class SoundClips:

    def __init__(self, dir):
        self._genres = ReadGenres(dir)
        print (self._genres.keys())
        
    def Genres(self):
        return sorted(list(self._genres.keys()))

    def PlayRandom(self, genre):
        os.system("killall mpg123")
        clip = random.choice(self._genres[genre])
        os.system("mpg123 '%s'&" % clip)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sc = SoundClips("/home/pi/AudioClips")
    for genre in sc.Genres():
        sc.PlayRandom(genre)
