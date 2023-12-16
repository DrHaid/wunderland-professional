import os
import random
import tempfile
import ctypes
import logging
from PIL import Image
from sys import platform
from gooey import Gooey, GooeyParser
from pywal import wallpaper
from wunderland import Wunderland
from wunderland_gif_generator import WunderlandGIFGenerator


def get_teamsbg_path():
    return os.path.join(os.getenv('APPDATA'), 'Microsoft\\Teams\\Backgrounds\\Uploads')


def save_teamsbg(img: Image):
    if platform != "win32":
        logging.error(
            "Microsoft Teams background only supported on Windows :(")
        return
    logging.info("Saving Microsoft Teams background")
    dir = get_teamsbg_path()
    img_thumb = img.resize((280, 158))
    bg_path = os.path.join(dir, "wunderland.png")
    bgthumb_path = os.path.join(dir, "wunderland_thumb.png")
    img.save(bg_path)
    img_thumb.save(bgthumb_path)


def save_animated_teamsbg(gif_gen: WunderlandGIFGenerator):
    if platform != "win32":
        logging.error(
            "Microsoft Teams background only supported on Windows :(")
        return
    logging.info("Setting animated Microsoft Teams background")
    dir = get_teamsbg_path()
    img_thumb = gif_gen.get_frame(0).resize((280, 158))
    bgthumb_path = os.path.join(dir, "wunderland_gif_thumb.png")
    img_thumb.save(bgthumb_path)

    bggif_path = os.path.join(dir, "wunderland_gif.gif")
    gif_gen.save_gif(bggif_path)
    pre, _ = os.path.splitext(bggif_path)
    os.replace(bggif_path, pre + ".png")


def set_wallpaper(img: Image):
    logging.info("Setting desktop wallpaper")
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
    plasma = dbus.Interface(bus.get_object(
        'org.kde.plasmashell', '/PlasmaShell'), dbus_interface='org.kde.PlasmaShell')
    plasma.evaluateScript(jscript % (
        'org.kde.image', 'org.kde.image', '%s', img))


def place_images(wunderland: Wunderland, img_name: str, count: int, colorize: bool = False):
    for x in range(0, count):
        img = wunderland.get_image_from_name(img_name)
        if colorize:
            hex_color = [
                "#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])]
        pos = wunderland.get_random_position(True, (75, 10, 75, 100))
        wunderland.add_entity(
            wunderland=wunderland,
            image=img, position=pos,
            facing_right=(x % 2 == 0),
            color=hex_color[0] if colorize else None)


def place_online_images(wunderland: Wunderland, count: int):
    online_cows = wunderland.get_online_images(count - 1)
    for cow in online_cows:
        pos = wunderland.get_random_position(True, (75, 10, 75, 100))
        wunderland.add_entity(
            wunderland=wunderland,
            image=cow, position=pos,
            facing_right=False)

    leftovers = count - len(online_cows)
    if (leftovers) >= 0:
        place_images(wunderland=wunderland, img_name="cow", count=leftovers)


@Gooey(default_size=(635, 585),
       program_name='Wunderland Generator',
       program_description='Generate Wunderland desktop wallpaper and/or Microsoft Teams background',
       image_dir='gui')
def main():
    logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S',
                        format='[%(asctime)s]: %(message)s', level=logging.INFO)

    parser = GooeyParser()
    parser.add_argument('-t', '--teams', action='store_true', dest='teams',
                        help='Saves Wunderland as Microsoft Teams background', metavar='MS Teams background')
    parser.add_argument('-d', '--desktop', action='store_true', dest='desktop',
                        help='Sets Wunderland as Desktop wallpaper', metavar='Desktop wallpaper')
    parser.add_argument('-o', '--online', action='store_true', dest='online',
                        help='Use custom drawings from API', metavar='Online drawings')
    parser.add_argument('-c', '--count', type=int, dest='drawing_count', default=6,
                        help='Define how many drawings populate the Wunderland', metavar='Drawing count', widget='IntegerField')
    parser.add_argument('-a', '--animated', action='store_true', dest='animated',
                        help='Generates an animated Wunderland', metavar='Animate image')
    parser.add_argument('-l', '--location', type=str, dest='location', default=None,
                        help='Overwrite the location for the current weather', metavar='Weather location')
    parser.add_argument('-p', '--out-path', type=str, dest='path', default=None,
                        help='Save the Wunderland in a specified directory', metavar='Target directory', widget='DirChooser')
    args = parser.parse_args()

    logging.info("------------------------------")
    logging.info("------ Starting process ------")

    if not (args.teams or args.desktop or args.path):
        logging.warning(
            '⚠️ No saving method selected. No Wunderland will be generated')
        return

    wunderland = Wunderland(location_overwrite=args.location)

    # place cows
    if args.online:
        logging.info(
            "Populating the Wunderland with %s online drawings", args.drawing_count)
        place_online_images(wunderland=wunderland, count=args.drawing_count)
    else:
        logging.info("Populating the Wunderland with %s cows",
                     args.drawing_count)
        place_images(wunderland=wunderland, img_name="cow",
                     count=args.drawing_count)

    # generate wunderland
    gif_gen = None
    frame = None
    if args.animated:
        logging.info("Generating animated Wunderland")
        gif_gen = WunderlandGIFGenerator(wunderland=wunderland)
        gif_gen.generate_gif_frames(1000)
    else:
        logging.info("Generating Wunderland")
        frame = wunderland.get_frame()

    # saving
    if args.teams:
        if args.animated:
            save_animated_teamsbg(gif_gen)
        else:
            save_teamsbg(frame)

    if args.desktop:
        if args.animated:
            logging.error(
                'The animated Wunderland cannot be set as desktop wallpaper :(')
        else:
            set_wallpaper(frame)

    if args.path:
        path = args.path
        if not os.path.isdir(path):
            logging.error(
                'Cannot save Wunderland because given path is not a directory')
            return

        logging.info("Saving as image to '%s'", path)
        if args.animated:
            gif_gen.save_gif(os.path.join(path, "wunderland.gif"))
        else:
            frame.save(os.path.join(path, "wunderland.png"))

    logging.info("------ Process finished ------")


if __name__ == "__main__":
    main()
