import time
import cv2
import mediapipe as mp
import numpy as np
import argparse
import pyvirtualcam
mp_selfie_segmentation = mp.solutions.selfie_segmentation

from wunderland import Wunderland


def threshold(img, thresh=128, maxval=255, type=cv2.THRESH_BINARY):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    threshed = cv2.threshold(img, thresh, maxval, type)[1]
    return threshed

def get_mask(frame, segmentation):
    results = segmentation.process(frame)
    # convert mask to int8
    mask = results.segmentation_mask
    mask = cv2.convertScaleAbs(mask, alpha=(255.0))
    
    # blur mask
    mask = cv2.GaussianBlur(mask, (61, 61), 0, 0)
    i, mask = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY)
    mask = cv2.GaussianBlur(mask, (21, 21), 0, 0)
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

    wunderland = Wunderland()
    # place cows
    place_images(wunderland=wunderland, img_name="cow", count=6)

    with mp_selfie_segmentation.SelfieSegmentation(
        model_selection=1) as selfie_segmentation:
        mock_cam = cv2.VideoCapture('webcam_capture.mp4')
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
                mask = get_mask(frame, selfie_segmentation)
                mask_3chan = np.stack([mask.astype('float') / 255.]*3, axis=2)
                frame = frame.astype('float') / 255.
                wunderland_frame = wunderland_frame.astype('float') / 255.
                out  = wunderland_frame * (1 - mask_3chan) + frame * mask_3chan

                # convert back to uint8
                out = out / out.max()
                out = 255 * out
                img = out.astype(np.uint8)

                cv2.imshow('MediaPipe Selfie Segmentation', img)
                if cv2.waitKey(5) & 0xFF == 27:
                    break

                cam.send(img)
                cam.sleep_until_next_frame()

if __name__ == "__main__":
    main()