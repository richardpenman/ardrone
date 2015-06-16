#!/usr/bin/env python

import cv2
import numpy as np



class Transform:
    """Return coordinates that drone needs to move/rotate to point to face
    """
    def __init__(self):
        # PID parameters
        self.Kpx = 0.25
        self.Kpy = 0.25
        self.Kdx = 0.25
        self.Kdy = 0.25
        self.Kix = 0
        self.Kiy = 0

        self.errx_1 = 0
        self.erry_1 = 0
        self.errz_1 = 0
        self.phi_1 = 0
        self.gaz_1 = 0
        self.yaw_1 = 0
        self.theta_1 = 0

    def __call__(self, frame, center):
        img_width, img_height = frame.shape[:2]
        zap = 0
        phi = 0
        theta = 0
        gaz = 0
        yaw = 0

        errx =  self.dst(center, 0, img_width)
        erry = -self.dst(center, 1, img_height)
        # use this if you want to make it come towards you
        errz = self.dst(center, 2, img_height)

        yaw = self.pid(self.yaw_1, errx, self.errx_1, self.Kpx, self.Kix, self.Kdx)
        gaz = self.pid(self.gaz_1, erry, self.erry_1, self.Kpy, self.Kiy, self.Kdy)
        # use this if you want to make it come towards you
        theta = self.pid(self.theta_1, errz, self.errz_1, self.Kpy, self.Kiy, self.Kdy)
        
        self.errx_1 = errx
        self.erry_1 = erry
        self.errz_1 = errz
        self.phi_1 = phi
        self.gaz_1 = gaz
        self.yaw_1 = yaw
        self.theta_1 = theta
        return zap, phi, theta, gaz, yaw

    # Simple PID controller from http://www.control.com/thread/1026159301
    def pid(self, out_1, err, err_1, Kp, Ki, Kd):
        return Kp*err + Ki*(err+err_1) + Kd*(err-err_1)

    # Returns proportional distance to image center along specified dimension.
    # Above center = -; Below = +
    # Right of center = +; Left = 1
    def dst(self, center, dim, siz):
        siz = siz/2
        return (center[dim] - siz) / float(siz)


class MeanShift:
    """Track face using meanshift
    """
    def __init__(self, frame, face):
        # set up the ROI for tracking
        x0, y0, x1, y1 = face
        cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 255, 0), 2)
        self.center = x0 + ((x1 - x0)/2), y0 + ((y1 - y0)/2), 3 * (y1 - y0)
        self.window = x0, y0, x1 - x0, y1 - y0

        roi = frame[y0:y1, x0:x1]
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_roi, np.array((0., 30.,32.)), np.array((180.,255.,255.)))
        roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
        cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
        self.roi_hist = roi_hist


    def update(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0], self.roi_hist, [0, 180], 1)
        term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
        # apply meanshift to get the new location
        ret, self.window = cv2.meanShift(dst, self.window, term_crit)
        if ret == 10:
            self.center = None
            print 'Lost track of face' 
        else:
            x, y, w, h = self.window
            self.center = (x + w/2, y + h/2, 3*h)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.circle(frame, self.center[:2], 1, (255, 0, 0), 2)


class CamShift:
    """Track face using camshift
    """
    def __init__(self, frame, face):
        # set up the ROI for tracking
        x0, y0, x1, y1 = face
        self.center = x0 + ((x1 - x0)/2), y0 + ((y1 - y0)/2), 3 * (y1 - y0)
        self.window = x0, y0, x1 - x0, y1 - y0

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv_roi = hsv[y0:y1, x0:x1]
        mask = cv2.inRange(hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
        mask_roi = mask[y0:y1, x0:x1]
        roi_hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
        cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX);
        self.roi_hist = roi_hist.reshape(-1)
        # draw rectangle for detected faces on frame
        cv2.rectangle(frame, (x0, y0), (x1, y1), (0, 255, 0), 2)

    def update(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
        prob = cv2.calcBackProject([hsv], [0], self.roi_hist, [0, 180], 1)
        #ret, self.window = cv2.meanShift(dst, self.window, self.term_crit)
        prob &= mask
        # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
        term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
        # apply camshift to get the new location
        track_box, self.window = cv2.CamShift(prob, self.window, term_crit)
        center = track_box[0]
        self.center = (int(center[0]), int(center[1]), 3*self.window[-1])
        x, y, w, h = self.window
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        #cv2.ellipse(frame, track_box, (0, 0, 255), 2)
        cv2.circle(frame, self.center[:2], 1, (255, 0, 0), 2)
        # XXX how to detect when lost connection, then do face detection again
