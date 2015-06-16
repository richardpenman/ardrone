#!/usr/bin/env python

import cv2
from movement import MeanShift


class FaceDetect:
    """Detect face using Haar Cascades
    """
    def __init__(self):
        training_data = ['data/haarcascade_frontalface_alt.xml']#, 'haarcascade_profileface.xml'
        self.cascades = [cv2.CascadeClassifier(filename) for filename in training_data]
        assert(not any(cascade.empty() for cascade in self.cascades))
        self.frame = 0
        self.tracker = None

    def __call__(self, frame):
        face_frame_i = 10 # every nth frame try face detection
        self.frame += 1
        
        if self.tracker is not None and self.tracker.center is not None:
            self.tracker.update(frame)

        elif self.frame >= face_frame_i:
            self.frame = 0
            face = self.detect_faces(frame)
            if face:
                self.tracker = MeanShift(frame, face) 
            else:
                self.tracker = None
            
        cv2.imshow('frame', frame)
        if self.tracker:
            return self.tracker.center


    def detect_faces(self, frame, image_scale=0.5):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        small_img = cv2.resize(gray, (0,0), fx=image_scale, fy=image_scale)    
        small_img = cv2.equalizeHist(small_img)

        for cascade in self.cascades:
            faces = cascade.detectMultiScale(small_img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
            if len(faces) > 0:
                x0, y0, w, h = faces[0]
                x1, y1 = x0 + w, y0 + h
                return int(x0 / image_scale), int(y0 / image_scale),\
                       int(x1 / image_scale), int(y1 / image_scale)
