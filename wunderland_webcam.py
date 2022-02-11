import os
import cv2
import numpy as np
import argparse
import pyvirtualcam
from cvzone.SelfiSegmentationModule import SelfiSegmentation


def threshold(img, thresh=128, maxval=255, type=cv2.THRESH_BINARY):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshed = cv2.threshold(img, thresh, maxval, type)[1]
    return threshed

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cam', type=int, dest='cam_index', default=0, help='Index of video capturing device')
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.cam_index)

    # configure camera for 720p @ 30 FPS
    width, height, fps = 1280, 720, 30
    cap.set(cv2.CAP_PROP_FRAME_WIDTH , width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    segmentor = SelfiSegmentation()

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    bg_img = cv2.imread(f'{ROOT_DIR}/img/wallpaper_partlycloudy.png')
    bg_img = cv2.resize(bg_img, (width, height))

    with pyvirtualcam.Camera(width=width, height=height, fps=fps) as cam:
        print(f'Using virtual camera: {cam.device}')
        while True:
            success, frame = cap.read()
            img_out = segmentor.removeBG(frame, imgBg=(0, 255, 0), threshold=0.73)  # replace background with green
            green = np.array([0, 255, 0])
            mask = cv2.inRange(img_out, green, green) # make mask using green background
            
            # # magic for mask smoothing and hole filling (rubbish)
            # mask = cv2.bitwise_not(mask)
            # kernel = np.ones((20, 20), 'uint8')
            # mask1 = cv2.dilate(mask, kernel=kernel, iterations=1)
            # mask1 = cv2.erode(mask1, kernel=kernel, iterations=1)
            # mask = cv2.bitwise_not(mask)
            # mask_blurred = cv2.GaussianBlur(mask, (27, 27), 0)
            
            # smooth mask outlines (needs work)
            mask  = cv2.GaussianBlur(mask, (27, 27), 0)
            mask = threshold(mask)

            # combine frame and bg_img
            res = cv2.bitwise_and(frame, frame, mask=mask)
            f = frame - res
            f = np.where(f == 0, bg_img, f)

            cam.send(f)
            cam.sleep_until_next_frame()

if __name__ == "__main__":
    main()