from enum import Enum
import logging
import os
import random
import math
import io
import json
import base64
from typing import Tuple
import requests
from PIL import Image, ImageOps


class WeatherData:
    def __init__(self, display_name, emoji, img_name, overlay):
        self.display_name = display_name
        self.emoji = emoji
        self.img_name = img_name
        self.overlay = overlay


class Weather(Enum):
    # Emojis seem to give autopep8 a stroke (understandably)
    # autopep8: off
    SUNNY = WeatherData('Sunny', '☀️', 'sunny', '') # sunny
    CLOUDY = WeatherData('Cloudy', '☁️', 'cloudy', '') # cloudy
    PARTLY_CLOUDY = WeatherData('Partly cloudy', '⛅️', 'partlycloudy', '') # partly cloudy
    THUNDERSTORM = WeatherData('Thunderstorm', '⛈', 'stormy', 'rainy') # thunder + rain
    LIGHT_RAIN = WeatherData('Light rain', '🌦', 'cloudy', 'rainy') # partly cloudy + rain
    RAINY = WeatherData('Rainy', '🌧', 'rainy', 'rainy') # rainy
    LIGHT_SNOW = WeatherData('Light snow', '🌨', 'cloudy', 'snowy') # light snow
    SNOWY = WeatherData('Snowy', '❄️', 'snowy', 'snowy') # snowy
    STORMY = WeatherData('Stormy', '🌩', 'stormy', '') # thunder
    FOGGY = WeatherData('Foggy', '🌫', 'cloudy', 'foggy') # foggy
    # autopep8: on

    def get_display_names():
        return [w.value.display_name for w in Weather]

    def get_by_attr(attr: str, value: str):
        return [w.value for w in Weather if getattr(w.value, attr) == value][0]


class Wunderland:
    def get_image_from_name(self, img_name: str):
        return Image.open(f'{self.ROOT_DIR}/img/{img_name}.png')

    def get_image_from_base64(self, img_base64: str):
        im_bytes = base64.b64decode(img_base64)
        im_file = io.BytesIO(im_bytes)
        img = Image.open(im_file)
        img = img.resize((164, 164))
        return img

    def get_online_images(self, count: int):
        '''
        Get custom drawn cows from API.
        '''
        try:
            logging.info('Requesting online drawings from server')
            response = requests.get(
                f'https://drhaid.com/api/cows/random/{count}')
            data = json.loads(response.content)
            return [self.get_image_from_base64(cow['image_data'].replace('data:image/png;base64,', '')) for cow in data]
        except Exception as e:
            logging.error(
                'An error occured while trying to fetch the online drawings')
            raise e

    def get_current_weather(self) -> Weather:
        '''
        Get weather for current IP using wttr.in (https://github.com/chubin/wttr.in)  
        '''
        try:
            logging.info('Requesting current weather from http://wttr.in/')
            response = requests.get(f'http://wttr.in/?format=%c')
            w = response.content.decode('utf-8').strip()
            weather = Weather.get_by_attr('emoji', w)
            return weather
        except Exception as e:
            logging.error(
                'An error occured while trying to fetch the current weather')
            raise e

    def get_random_position(self, grounded: bool, padding: Tuple = (0, 0, 0, 0), origin: Tuple = None, radius: int = None) -> Tuple:
        '''
        Get random position on wunderland.
        '''
        def max(a, b): return a if a >= b else b
        def min(a, b): return a if a < b else b

        if origin:
            x_min = int(max(origin[0] - radius, 0 + padding[0]))
            x_max = int(
                min(origin[0] + radius, self.BG_IMG.size[0] - 1 - padding[2]))
            x = random.randint(x_min, x_max)
        else:
            x = random.randint(
                0 + padding[0], self.BG_IMG.size[0] - 1 - padding[2])

        bg_img_ground_equ = 50 * \
            math.sin(0.0021 * (x + 200)) - 624     # basically magic
        y_on_curve = abs(int(bg_img_ground_equ))

        if origin:
            y_min = int(max(origin[1] - radius, y_on_curve +
                        padding[1] if grounded else 0 + padding[1]))
            y_max = int(min(origin[1] + radius, self.BG_IMG.size[1] -
                        1 - padding[3] if grounded else y_on_curve - padding[3]))
            y = random.randint(y_min, y_max)
        else:
            if grounded:
                y = random.randint(
                    y_on_curve + padding[1], self.BG_IMG.size[1] - 1 - padding[3])
            else:
                y = random.randint(0 + padding[1], y_on_curve - 1 - padding[3])

        return (x, y)

    def add_entity(self, wunderland, image: Image, position: Tuple, facing_right: bool, color: str = None):
        '''
        Add a WunderlandEntity to this Wunderland instance 
        '''
        entity = WunderlandEntity(
            wunderland=wunderland,
            image=image, position=position,
            facing_right=facing_right,
            color=color)
        self.wunderland_entities.append(entity)

    def get_frame(self) -> Image:
        '''
        Render frame of the Wunderland.
        '''
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
            overlay = Image.open(
                f'{self.ROOT_DIR}/img/overlay_wallpaper_{self.weather.overlay}.png')
            frame.paste(overlay, mask=overlay)

        return frame

    def do_animation_step(self, delta_time: float):
        '''
        Update all WunderlandEntity positions. delta_time is time since last update.
        '''
        for entity in self.wunderland_entities:
            entity.move(delta_time)

    def __init__(self, weather: str | None = None):
        if not weather:
            try:
                self.weather = self.get_current_weather()
            except Exception as e:
                logging.error(repr(e))
                logging.info('Falling back to using weather "Partly cloudy"')
                self.weather = Weather.PARTLY_CLOUDY.value
        else:
            self.weather = Weather.get_by_attr('display_name', weather)

        self.ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.BG_IMG = Image.open(
            f'{self.ROOT_DIR}/img/wallpaper_{self.weather.img_name}.png')
        self.wunderland_entities = []


class WunderlandEntity:
    def __init__(self, wunderland: Wunderland, image: Image, position: Tuple, facing_right: bool, color: str):
        self.wunderland = wunderland
        self.image = self.tint_image(image, color) if color else image
        self.position = position
        self.facing_right = False    # initially all images are facing left
        self.target_position = None
        self.timeout = 0

        self.flip_img(facing_right=facing_right)

    def tint_image(self, src: Image, color: str) -> Image:
        '''
        Tint input image using hex color.
        '''
        src.load()
        r, g, b, alpha = src.split()
        gray = ImageOps.grayscale(src)
        result = ImageOps.colorize(gray, (0, 0, 0, 0), color)
        result.putalpha(alpha)
        return result

    def flip_img(self, facing_right: bool):
        '''
        Change image facing direction.
        '''
        if self.facing_right != facing_right:
            self.image = ImageOps.mirror(self.image)
            self.facing_right = facing_right

    def move(self, delta_time: float):
        if not self.target_position:
            self.target_position = self.wunderland.get_random_position(
                True, origin=self.position, radius=200)

        dist = delta_time * 10
        if self.timeout <= 0:
            vec = (self.target_position[0] - self.position[0],
                   self.target_position[1] - self.position[1])
            len = math.sqrt(vec[0] * vec[0] + vec[1] * vec[1])
            unit = (vec[0] / len, vec[1] / len)
            self.position = (
                self.position[0] + unit[0] * dist, self.position[1] + unit[1] * dist)
            self.flip_img(unit[0] >= 0)

        else:
            self.timeout = self.timeout - delta_time

        if math.dist(self.position, self.target_position) < 10:
            self.timeout = random.random() * 15 + 5
            self.target_position = self.wunderland.get_random_position(
                True, origin=self.position, radius=200)
