import random
from PIL.Image import Image as PillowIMG

from wunderland import Wunderland

DELTA_TIME = 0.07


class WunderlandGIFGenerator():
    def __init__(self, wunderland: Wunderland):
        self.wunderland = wunderland
        self.frames = []

    def _init_animator(self, gif_length: int) -> None:
        for e in range(len(self.wunderland.wunderland_entities)):
            # set initial timeout for every other entity to delay their movement
            init_timeout = 0 if (
                e % 2 == 0) else random.random() * ((gif_length / 2) / 3)
            self.wunderland.wunderland_entities[e].timeout = init_timeout

    def generate_gif_frames(self, gif_length: int) -> None:
        self.frames = []
        self._init_animator(gif_length)

        for _ in range(int(gif_length / 2)):
            self.wunderland.do_animation_step(delta_time=DELTA_TIME)
            wunderland_frame = self.wunderland.get_frame()
            self.frames.append(wunderland_frame)

        # reverse and append generated frames to make the GIF loop seamlessly
        frames_reversed = self.frames.copy()
        frames_reversed.reverse()
        self.frames = self.frames + frames_reversed

    def get_frame(self, index: int = 0) -> PillowIMG:
        i = max(0, min(index, len(self.frames) - 1))
        return self.frames[i]

    def save_gif(self, path: str) -> None:
        self.frames[0].save(path, format='GIF', append_images=self.frames,
                            save_all=True, duration=50)  # TODO: pallete optimization
