#! /usr/bin/env python
import os
import math
import random
import requests
import tempfile
import ctypes
import argparse
from PIL import Image, ImageOps

class Weather:
    def __init__(self, emoji, name, overlay):
        self.emoji = emoji
        self.name = name
        self.overlay = overlay

class Layer:
    def __init__(self, image, position):
        self.image = image
        self.position = position

WEATHER_MAP = [
    Weather("☀️", "sunny", ""), # sunny
    Weather("☁️", "cloudy", ""), # cloudy
    Weather("⛅️", "partlycloudy", ""), # partly cloudy
    Weather("⛈", "stormy", "rainy"), # thunder + rain
    Weather("🌦", "cloudy", "rainy"), # partly cloudy + rain
    Weather("🌧", "rainy", "rainy"), # rainy
    Weather("🌨", "cloudy", "snowy"), # light snow
    Weather("❄", "snowy", "snowy"), # snowy
    Weather("🌩", "stormy", ""), # thunder
    Weather("🌫", "cloudy", "foggy") # foggy
]

BG_IMG = None
LAYERS = []

def get_teamsbg_path():
    return os.path.join(os.getenv('APPDATA'), 'Microsoft\\Teams\\Backgrounds\\Uploads')

def save_teamsbg():
    dir = get_teamsbg_path()
    img_thumb = BG_IMG.resize((280, 158))
    bg_path = os.path.join(dir, "wunderland.png")
    bgthumb_path = os.path.join(dir, "wunderland_thumb.png")
    BG_IMG.save(bg_path)
    img_thumb.save(bgthumb_path)

def set_wallpaper():
    dir = tempfile.gettempdir()
    path = os.path.join(dir, "wunderland.bmp")
    BG_IMG.save(path)
    SPI_SETDESKWALLPAPER = 0x0014
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path , 0)

"""
Get weather for current IP using wttr.in (https://github.com/chubin/wttr.in)  
"""
def get_weather():
    response = requests.get("http://wttr.in?format=\"%c\"")
    weather_response = response.content.decode("utf-8")[1:-1].strip()
    weather = [x for x in WEATHER_MAP if x.emoji == weather_response]
    return weather[0]

def get_random_position(grounded):
    x = random.randint(0, BG_IMG.size[0] - 1)
    bg_img_ground_equ = 50 * math.sin(0.0021 * (x + 200)) - 624
    y_on_curve = abs(int(bg_img_ground_equ))
    y = 0
    if grounded:
        y = random.randint(y_on_curve, BG_IMG.size[1] - 1)
    else:
        y = random.randint(0, y_on_curve - 1)
    return (x, y)

def add_cows():
    cow_img = Image.open('img/cow.png')
    cow_count = 6

    for x in range(0, cow_count):
        cow_img = ImageOps.mirror(cow_img)

        pos = get_random_position(True)
        cow_pos_x = int(pos[0] - (cow_img.size[0] / 2))
        cow_pos_y = int(pos[1] - (cow_img.size[1] - 50)) # -50 origin bottom offset

        LAYERS.append(Layer(cow_img, (cow_pos_x, cow_pos_y)))

def main():
    global BG_IMG
    
    weather = get_weather()
    BG_IMG = Image.open(f'img/wallpaper_{weather.name}.png')
    
    add_cows()
    LAYERS.sort(key=lambda x: x.position[1])

    for layer in LAYERS:
        BG_IMG.paste(layer.image, layer.position, mask=layer.image)
    
    if weather.overlay:
        overlay = Image.open(f'img/overlay_wallpaper_{weather.overlay}.png')
        BG_IMG.paste(overlay, mask=overlay)

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--teams', action='store_true', dest='teams', help='Saves Wunderland as Microsoft Teams background')
    parser.add_argument('-d', '--desktop', action='store_true', dest='desktop', help='Sets Wunderland as Desktop wallpaper')
    args = parser.parse_args()

    if args.teams:
        save_teamsbg()
        print("Microsoft Teams background saved")
    if args.desktop:
        set_wallpaper()
        print("Desktop wallpaper set")


if __name__ == "__main__":
    main()