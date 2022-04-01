from multiprocessing.connection import wait
import time
import cv2
import numpy as np
import argparse
import pyvirtualcam
from cvzone.SelfiSegmentationModule import SelfiSegmentation

from wunderland import Wunderland


def threshold(img, thresh=128, maxval=255, type=cv2.THRESH_BINARY):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshed = cv2.threshold(img, thresh, maxval, type)[1]
    return threshed

def get_mask(frame, segmentor):
    img_out = segmentor.removeBG(frame, imgBg=(0, 255, 0), threshold=0.73)  # replace background with green
    green = np.array([0, 255, 0])
    mask = cv2.inRange(img_out, green, green) # make mask using green background
    
    # smooth mask outlines (needs work)
    mask  = cv2.GaussianBlur(mask, (27, 27), 0)
    mask = threshold(mask)
    return mask

def place_images(wunderland: Wunderland, img_name: str, count: int):
    for x in range(0, count):
        img = wunderland.get_image_from_name(img_name)
        pos = wunderland.get_random_position(True)
        wunderland.add_entity(wunderland=wunderland, image=img, position=pos, facing_right=(x % 2 == 0))  

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cam', type=int, dest='cam_index', default=0, help='Index of video capturing device')
    parser.add_argument('-m', '--mock', action='store_true', dest='mock', help='Use "webcam.mp4" to mock webcam. Crashes when video over :(')
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.cam_index)

    # configure camera for 720p @ 30 FPS
    width, height, fps = 1280, 720, 30
    cap.set(cv2.CAP_PROP_FRAME_WIDTH , width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    segmentor = SelfiSegmentation()

    wunderland = Wunderland()
    # place cows
    place_images(wunderland=wunderland, img_name="cow", count=6)

    mock_cam = cv2.VideoCapture('webcam.mp4')
    with pyvirtualcam.Camera(width=width, height=height, fps=fps) as cam:
        print(f'Using virtual camera: {cam.device}')
        last_time = time.time()
        while True:
            success, frame = mock_cam.read() if args.mock else cam.read()

            # get next wunderland rendered frame
            delta_time = time.time() - last_time
            wunderland.do_animation_step(delta_time=delta_time)
            last_time = time.time()
            wunderland_frame = wunderland.get_frame()
            wunderland_frame = cv2.cvtColor(np.array(wunderland_frame), cv2.COLOR_RGB2BGR)
            wunderland_frame = cv2.resize(wunderland_frame, (width, height))

            # combine frame and wunderland_frame
            mask = get_mask(frame, segmentor)
            bg = cv2.bitwise_and(wunderland_frame, wunderland_frame, mask=mask)
            mask_inv = cv2.bitwise_not(mask)
            # mask_blur  = cv2.GaussianBlur(mask_inv, (27, 27), 0)
            f = cv2.bitwise_and(frame, frame, mask=mask_inv)
            res = cv2.add(bg, f)
            # f = np.where(f == 0, wunderland_frame, f)
            res = cv2.cvtColor(np.array(res), cv2.COLOR_RGB2BGR)

            cam.send(res)
            # cam.send(cv2.merge((mask,mask,mask)))
            cam.sleep_until_next_frame()

if __name__ == "__main__":
    main()