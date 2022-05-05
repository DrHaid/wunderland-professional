#! /usr/bin/env python
import os
import math
import random
import tempfile
import ctypes
import argparse
from PIL import Image, ImageOps
from sys import platform
from pywal import wallpaper
from wunderland import Wunderland


def get_teamsbg_path():
    return os.path.join(os.getenv('APPDATA'), 'Microsoft\\Teams\\Backgrounds\\Uploads')

def save_teamsbg(img: Image):
    if platform != "win32":
        print("Microsoft Teams background only supported on Windows :(")
        return
    dir = get_teamsbg_path()
    img_thumb = img.resize((280, 158))
    bg_path = os.path.join(dir, "wunderland.png")
    bgthumb_path = os.path.join(dir, "wunderland_thumb.png")
    img.save(bg_path)
    img_thumb.save(bgthumb_path)
    print("Microsoft Teams background saved")

def set_wallpaper(img: Image):
    dir = tempfile.gettempdir()
    path = os.path.join(dir, "wunderland.bmp")
    img.save(path)

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


def place_images(wunderland: Wunderland, img_name: str, count: int, colorize: bool = False):
    for x in range(0, count):
        img = wunderland.get_image_from_name(img_name)
        if colorize:
            hex_color = ["#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])]
        pos = wunderland.get_random_position(True)
        wunderland.add_entity(
            wunderland=wunderland, 
            image=img, position=pos, 
            facing_right=(x % 2 == 0), 
            color=hex_color[0] if colorize else None)   

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--teams', action='store_true', dest='teams', help='Saves Wunderland as Microsoft Teams background')
    parser.add_argument('-d', '--desktop', action='store_true', dest='desktop', help='Sets Wunderland as Desktop wallpaper')
    parser.add_argument('-c', '--cows', type=int, dest='cow_count', default=6, help='Define how many cows populate the Wunderland')
    parser.add_argument('-l', '--location', type=str, dest='location', default=None, help='Overwrite the location for the current weather')
    args = parser.parse_args()

    wunderland = Wunderland(location_overwrite=args.location)

    # place cows
    place_images(wunderland=wunderland, img_name="cow", count=args.cow_count)
    frame = wunderland.get_frame()

    if args.teams:
        save_teamsbg(frame)
    if args.desktop:
        set_wallpaper(frame)


if __name__ == "__main__":
    main()