#! /usr/bin/env python
import os
import math
import random
import requests
import tempfile
import ctypes
import argparse
from PIL import Image, ImageOps
from sys import platform
from pywal import wallpaper

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
    if platform != "win32":
        print("Microsoft Teams background only supported on Windows :(")
        return
    dir = get_teamsbg_path()
    img_thumb = BG_IMG.resize((280, 158))
    bg_path = os.path.join(dir, "wunderland.png")
    bgthumb_path = os.path.join(dir, "wunderland_thumb.png")
    BG_IMG.save(bg_path)
    img_thumb.save(bgthumb_path)
    print("Microsoft Teams background saved")

def set_wallpaper():
    dir = tempfile.gettempdir()
    path = os.path.join(dir, "wunderland.bmp")
    BG_IMG.save(path)

    if platform == "win32":
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)
    elif platform == "darwin":
        wallpaper.set_mac_wallpaper(path)
    else:
        desktop = wallpaper.get_desktop_env()
        if desktop == "KDE":
            set_kde_wallpaper(path)
        else:
            wallpaper.set_desktop_wallpaper(desktop, path)
    print("Desktop wallpaper set")

"""
special workaround for kde
"""
def set_kde_wallpaper(img):
    """Set the wallpaper on KDE Plasma"""
    # For whatever reason, it's not as simple as one would think.
    # Shoutouts to pashazz on GitHub, the author of this snippet
    # Taken from https://github.com/pashazz/ksetwallpaper
    jscript = """
    var allDesktops = desktops();
    print (allDesktops);
    for (i=0;i<allDesktops.length;i++) {
        d = allDesktops[i];
        d.wallpaperPlugin = "%s";
        d.currentConfigGroup = Array("Wallpaper", "%s", "General");
        d.writeConfig("Image", "file://%s")
        d.writeConfig("Image", "file://%s")
    }
    """
    import dbus
    bus = dbus.SessionBus()
    plasma = dbus.Interface(bus.get_object('org.kde.plasmashell', '/PlasmaShell'), dbus_interface='org.kde.PlasmaShell')
    plasma.evaluateScript(jscript % ('org.kde.image', 'org.kde.image', '%s', img))

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

def place_images(img: Image, count: int):
    for x in range(0, count):
        img = ImageOps.mirror(img)

        pos = get_random_position(True)
        pos_x = int(pos[0] - (img.size[0] / 2))
        pos_y = int(pos[1] - (img.size[1]))

        LAYERS.append(Layer(img, (pos_x, pos_y)))

def main():
    global BG_IMG
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    weather = get_weather()
    BG_IMG = Image.open(f'{ROOT_DIR}/img/wallpaper_{weather.name}.png')
    
    # place cows
    cow_img = Image.open(f'{ROOT_DIR}/img/cow_xmas.png')
    cow_count = 6
    place_images(cow_img, cow_count)

    LAYERS.sort(key=lambda x: x.position[1])

    for layer in LAYERS:
        BG_IMG.paste(layer.image, layer.position, mask=layer.image)
    
    if weather.overlay:
        overlay = Image.open(f'{ROOT_DIR}/img/overlay_wallpaper_{weather.overlay}.png')
        BG_IMG.paste(overlay, mask=overlay)

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--teams', action='store_true', dest='teams', help='Saves Wunderland as Microsoft Teams background')
    parser.add_argument('-d', '--desktop', action='store_true', dest='desktop', help='Sets Wunderland as Desktop wallpaper')
    args = parser.parse_args()

    if args.teams:
        save_teamsbg()
    if args.desktop:
        set_wallpaper()


if __name__ == "__main__":
    main()