import os
import random
import math
from typing import Tuple
import requests
from PIL import Image, ImageOps

class WunderlandEntity:
    def __init__(self, image: Image, position: Tuple, facing_right: bool):
        self.image = image
        self.position = position
        self.facing_right = facing_right
        
        if not self.facing_right:
            self.image = ImageOps.mirror(self.image) 

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

    """
    Get weather for current IP using wttr.in (https://github.com/chubin/wttr.in)  
    """
    def get_weather(self, weather_str: str) -> Weather:
        response = requests.get("http://wttr.in?format=\"%c\"")
        w = response.content.decode("utf-8")[1:-1].strip() if not weather_str else weather_str
        weather = [x for x in self.WEATHER_MAP if x.emoji == w]
        return weather[0]

    """
    Get random position on wunderland
    """
    def get_random_position(self, grounded: bool) -> Tuple:
        x = random.randint(0, self.BG_IMG.size[0] - 1)
        bg_img_ground_equ = 50 * math.sin(0.0021 * (x + 200)) - 624
        y_on_curve = abs(int(bg_img_ground_equ))
        y = 0
        if grounded:
            y = random.randint(y_on_curve, self.BG_IMG.size[1] - 1)
        else:
            y = random.randint(0, y_on_curve - 1)
        return (x, y)

    """
    Add a WunderlandEntity to this Wunderland instance 
    """
    def add_entity(self, image: Image, position: Tuple, facing_right: bool):
        entity = WunderlandEntity(image=image, position=position, facing_right=facing_right)
        self.wunderland_entities.append(entity)

    """
    Render frame of the Wunderland. delta_time is time since last frame.
    """
    def get_frame(self, delta_time: int = 0) -> Image:
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

    def get_image_from_name(self, img_name: str):
        return Image.open(f'{self.ROOT_DIR}/img/{img_name}.png')

    def __init__(self, weather_str = None):
        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.weather = self.get_weather(weather_str)
        self.BG_IMG = Image.open(f'{self.ROOT_DIR}/img/wallpaper_{self.weather.name}.png')
        self.wunderland_entities = []
