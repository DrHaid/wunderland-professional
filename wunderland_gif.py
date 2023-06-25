#! /usr/bin/env python
import os
import random
from PIL import Image
from sys import platform

import numpy as np
from wunderland import Wunderland
from wunderland_wallpaper import place_online_images

def get_teamsbg_path():
    return os.path.join(os.getenv('APPDATA'), 'Microsoft\\Teams\\Backgrounds\\Uploads')

def save_teamsbg(thumb: Image, gif_file: str):
    if platform != "win32":
        print("Microsoft Teams background only supported on Windows :(")
        return
    dir = get_teamsbg_path()
    img_thumb = thumb.resize((280, 158))
    bgthumb_path = os.path.join(dir, "wunderland_gif_thumb.png")
    img_thumb.save(bgthumb_path)
    try:
        os.rename(gif_file, os.path.join(dir, "wunderland_gif.png"))
    except FileExistsError:
        os.remove(os.path.join(dir, "wunderland_gif.png"))
        os.rename(gif_file, os.path.join(dir, "wunderland_gif.png"))
    print("Microsoft Teams background saved")

LENGTH = 2000

def main():
    wunderland = Wunderland()
    # place cows
    place_online_images(wunderland=wunderland, count=12)
    for e in range(12):
        wunderland.wunderland_entities[e].timeout = 0 if (e % 2 == 0) else random.random() * 3

    frames = []
    for x in range(int(LENGTH / 2)):
        wunderland.do_animation_step(delta_time=0.04)
        wunderland_frame = wunderland.get_frame()
        frames.append(wunderland_frame)

    frames_reversed = frames.copy()
    frames_reversed.reverse()
    frames = frames + frames_reversed

    frames[0].save(fp="wunderland_gif.gif", format='GIF', append_images=frames, save_all=True, duration=LENGTH * 0.025)

    save_teamsbg(frames[0], "wunderland_gif.gif")

if __name__ == "__main__":
    main()