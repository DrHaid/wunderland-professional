import time
import cv2
import numpy as np
from wunderland import Wunderland


def place_images(wunderland: Wunderland, img_name: str, count: int):
    for x in range(0, count):
        img = wunderland.get_image_from_name(img_name)
        pos = wunderland.get_random_position(True)
        wunderland.add_entity(wunderland=wunderland, image=img, position=pos, facing_right=(x % 2 == 0))     


def main():
    wunderland = Wunderland()
    
    # place cows
    place_images(wunderland=wunderland, img_name="cow", count=6)

    last_time = time.time()
    while True:
        delta_time = time.time() - last_time
        wunderland.do_animation_step(delta_time=delta_time)
        last_time = time.time()
        frame = wunderland.get_frame()
        cv2_frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        cv2.imshow("Preview", cv2_frame)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()