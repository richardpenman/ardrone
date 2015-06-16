#!/usr/bin/env python

import os
import datetime
import cv2
import time
import threading

SLEEP_TIME = 0.1


class VideoRecord:
    """Save frames to AVI video in a background thread
    """
    def __init__(self, cam, output_dir='video'):
        w = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
        frame_rate = cv2.CAP_PROP_FPS # XXX why FPS so low?
        frame_rate = 15
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_file = datetime.datetime.now().strftime(os.path.join(output_dir, '%Y%m%d%H%M%S.avi'))
        self.video_writer = cv2.VideoWriter(output_file, fourcc, frame_rate, (w, h))
        self.frames = []
        self.running = True
        # process frames in a separate thread to avoid holding up camera
        threading.Thread(target=self.process).start()

    def __call__(self, frame):
        self.frames.append(frame)

    def process(self):
        while self.running or self.frames:
            if self.frames:
                self.video_writer.write(self.frames.pop(0))
            else:
                time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    main()
