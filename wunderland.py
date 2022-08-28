import os
import random
import math
import io
import json
import base64
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
        Weather("❄️", "snowy", "snowy"), # snowy
        Weather("🌩", "stormy", ""), # thunder
        Weather("🌫", "cloudy", "foggy") # foggy
    ]

    def get_image_from_name(self, img_name: str):
        return Image.open(f'{self.ROOT_DIR}/img/{img_name}.png')

    def get_image_from_base64(self, img_base64: str):
        im_bytes = base64.b64decode(img_base64)
        im_file = io.BytesIO(im_bytes)
        img = Image.open(im_file)
        img = img.resize((164, 164))
        return img

    """
    Get custom drawn cows from API.
    """
    def get_online_images(self, count: int):
        response = requests.get(f'https://drhaid.com/api/cows/random/{count}')
        data = json.loads(response.content)
        return [self.get_image_from_base64(cow["image_data"].replace("data:image/png;base64,", "")) for cow in data]

    """
    Get weather for current IP using wttr.in (https://github.com/chubin/wttr.in)  
    """
    def get_weather(self, weather_str: str = None, location_overwrite: str = None) -> Weather:
        location = "" if not location_overwrite else location_overwrite
        response = requests.get(f'http://wttr.in/{location}?format=%c')
        w = response.content.decode("utf-8").strip() if not weather_str else weather_str
        weather = [x for x in self.WEATHER_MAP if x.emoji == w]
        return weather[0]

    """
    Get random position on wunderland.
    """
    def get_random_position(self, grounded: bool, padding: Tuple = (0, 0, 0, 0), origin: Tuple = None, radius: int = None) -> Tuple:
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
            x_min = int(max(origin[0] - radius, 0 + padding[0]))
            x_max = int(min(origin[0] + radius, self.BG_IMG.size[0] - 1 - padding[2]))
            x = random.randint(x_min, x_max)
        else:
            x = random.randint(0 + padding[0], self.BG_IMG.size[0] - 1 - padding[2])

        bg_img_ground_equ = 50 * math.sin(0.0021 * (x + 200)) - 624     # basically magic
        y_on_curve = abs(int(bg_img_ground_equ))

        if origin:
            y_min = int(max(origin[1] - radius, y_on_curve + padding[1] if grounded else 0 + padding[1]))
            y_max = int(min(origin[1] + radius, self.BG_IMG.size[1] - 1 - padding[3] if grounded else y_on_curve - padding[3]))
            y = random.randint(y_min, y_max)
        else:
            if grounded:
                y = random.randint(y_on_curve + padding[1], self.BG_IMG.size[1] - 1 - padding[3])
            else:
                y = random.randint(0 + padding[1], y_on_curve - 1 - padding[3])
        
        return (x, y)

    """
    Add a WunderlandEntity to this Wunderland instance 
    """
    def add_entity(self, wunderland, image: Image, position: Tuple, facing_right: bool, color: str = None):
        entity = WunderlandEntity(
            wunderland=wunderland, 
            image=image, position=position, 
            facing_right=facing_right, 
            color=color)
        self.wunderland_entities.append(entity)

    """
    Render frame of the Wunderland.
    """
    def get_frame(self) -> Image:
        self.wunderland_entities.sort(key=lambda x: x.position[1])
        frame = self.BG_IMG.copy()

        for entity in self.wunderland_entities:
            bbox = entity.image.getbbox()
            pivot_x = ((bbox[2] - bbox[0]) / 2) + bbox[0]
            pivot_y = ((bbox[3] - bbox[1]) / 2) + bbox[1]
            pos_x = int(entity.position[0] - pivot_x)
            pos_y = int(entity.position[1] - pivot_y)
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

    def __init__(self, weather_str = None, location_overwrite=None):
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.weather = self.get_weather(weather_str, location_overwrite)
        self.BG_IMG = Image.open(f'{self.ROOT_DIR}/img/wallpaper_{self.weather.name}.png')
        self.wunderland_entities = []


class WunderlandEntity:
    def __init__(self, wunderland: Wunderland, image: Image, position: Tuple, facing_right: bool, color: str):
        self.wunderland = wunderland
        self.image = self.tint_image(image, color) if color else image
        self.position = position
        self.facing_right = False    # initially all images are facing left
        self.target_position = None
        self.timeout = None
        
        self.flip_img(facing_right=facing_right)

    """
    Tint input image using hex color.
    """
    def tint_image(self, src: Image, color: str) -> Image:
        src.load()
        r, g, b, alpha = src.split()
        gray = ImageOps.grayscale(src)
        result = ImageOps.colorize(gray, (0, 0, 0, 0), color) 
        result.putalpha(alpha)
        return result

    """
    Change image facing direction.
    """
    def flip_img(self, facing_right: bool):
        if self.facing_right != facing_right:
            self.image = ImageOps.mirror(self.image)
            self.facing_right = facing_right

    def move(self, delta_time: float):
        if not self.target_position:
            self.target_position = self.wunderland.get_random_position(True, origin=self.position, radius=200)
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
            self.target_position = self.wunderland.get_random_position(True, origin=self.position, radius=200)
        