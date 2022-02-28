import os
import random
import math
from typing import Tuple
import requests
from PIL import Image, ImageOps


class Weather:
    def __init__(self, emoji, name, overlay):
        self.emoji = emoji
        self.name = name
        self.overlay = overlay

class Wunderland:
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

    def get_image_from_name(self, img_name: str):
        return Image.open(f'{self.ROOT_DIR}/img/{img_name}.png')

    """
    Get weather for current IP using wttr.in (https://github.com/chubin/wttr.in)  
    """
    def get_weather(self, weather_str: str) -> Weather:
        response = requests.get("http://wttr.in?format=\"%c\"")
        w = response.content.decode("utf-8")[1:-1].strip() if not weather_str else weather_str
        weather = [x for x in self.WEATHER_MAP if x.emoji == w]
        return weather[0]

    """
    Get random position on wunderland.
    """
    def get_random_position(self, grounded: bool, origin: Tuple = None, radius: int = None) -> Tuple:
        def max(a, b):
            if a >= b:
                return a
            else:
                return b

        def min(a, b):
            if a < b:
                return a
            else:
                return b
        
        if origin:
            x_min = int(max(origin[0] - radius, 0))
            x_max = int(min(origin[0] + radius, self.BG_IMG.size[0] - 1))
            x = random.randint(x_min, x_max)
        else:
            x = random.randint(0, self.BG_IMG.size[0] - 1)

        bg_img_ground_equ = 50 * math.sin(0.0021 * (x + 200)) - 624     # basically magic
        y_on_curve = abs(int(bg_img_ground_equ))

        if origin:
            y_min = int(max(origin[1] - radius, y_on_curve if grounded else 0))
            y_max = int(min(origin[1] + radius, self.BG_IMG.size[1] - 1 if grounded else y_on_curve))
            y = random.randint(y_min, y_max)
        else:
            if grounded:
                y = random.randint(y_on_curve, self.BG_IMG.size[1] - 1)
            else:
                y = random.randint(0, y_on_curve - 1)
        
        return (x, y)

    """
    Add a WunderlandEntity to this Wunderland instance 
    """
    def add_entity(self, wunderland, image: Image, position: Tuple, facing_right: bool):
        entity = WunderlandEntity(wunderland=wunderland, image=image, position=position, facing_right=facing_right)
        self.wunderland_entities.append(entity)

    """
    Render frame of the Wunderland.
    """
    def get_frame(self) -> Image:
        self.wunderland_entities.sort(key=lambda x: x.position[1])
        frame = self.BG_IMG.copy()

        for entity in self.wunderland_entities:
            # use image bottom center as pivot
            pos_x = int(entity.position[0] - (entity.image.size[0] / 2))
            pos_y = int(entity.position[1] - (entity.image.size[1]))
            frame.paste(entity.image, (pos_x, pos_y), mask=entity.image)

        if self.weather.overlay:
            overlay = Image.open(f'{self.ROOT_DIR}/img/overlay_wallpaper_{self.weather.overlay}.png')
            frame.paste(overlay, mask=overlay)
        
        return frame

    """
    Update all WunderlandEntity positions. delta_time is time since last update.
    """
    def do_animation_step(self, delta_time: float):
        for entity in self.wunderland_entities:
            entity.move(delta_time)

    def __init__(self, weather_str = None):
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.weather = self.get_weather(weather_str)
        self.BG_IMG = Image.open(f'{self.ROOT_DIR}/img/wallpaper_{self.weather.name}.png')
        self.wunderland_entities = []


class WunderlandEntity:
    def __init__(self, wunderland: Wunderland, image: Image, position: Tuple, facing_right: bool):
        self.wunderland = wunderland
        self.image = image
        self.position = position
        self.facing_right = False    # initially all images are facing left
        self.target_position = None
        self.timeout = None
        
        self.flip_img(facing_right=facing_right)

    def flip_img(self, facing_right: bool):
        if self.facing_right != facing_right:
            self.image = ImageOps.mirror(self.image)
            self.facing_right = facing_right

    def move(self, delta_time: float):
        if not self.target_position:
            self.target_position = self.wunderland.get_random_position(True, self.position, 200)
            self.timeout = 0

        dist = delta_time * 10
        if self.timeout <= 0:
            vec = (self.target_position[0] - self.position[0], self.target_position[1] - self.position[1])
            len = math.sqrt(vec[0] * vec[0] + vec[1] * vec[1])
            unit = (vec[0] / len, vec[1] / len)
            self.position = (self.position[0] + unit[0] * dist, self.position[1] + unit[1] * dist)
            self.flip_img(unit[0] >= 0)

        else: 
            self.timeout = self.timeout - delta_time

        if math.dist(self.position, self.target_position) < 10:
            self.timeout = random.random() * 15 + 5
            self.target_position = self.wunderland.get_random_position(True, self.position, 200)
        