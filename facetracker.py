#!/usr/bin/env python

import sys
import traceback
import cv2
from ardrone import libardrone

from facedetect import FaceDetect
from movement import Transform
from videorecord import VideoRecord


def run(camera_port, drone):
    """Process frames from camera
    """
    cam = cv2.VideoCapture(camera_port)
    face_detect = FaceDetect()
    transform = Transform()
    video_record = VideoRecord(cam)

    try:
        running = True
        while running:
            running, frame = cam.read()
            if running:
                center = face_detect(frame)
                if center is not None:
                    result = transform(frame, center)
                    print result
                    zap, phi, theta, gaz, yaw = result
                    #gaz = theta = phi = 0
                    if drone is not None:
                        drone.at(libardrone.at_pcmd, True, phi, theta, gaz, yaw)

                if drone is not None:
                    navdata = drone.navdata.get(0, {})
                    # check battery status
                    battery = navdata.get('battery')
                    if battery is not None and battery < 15:
                        print 'Low battery:', battery
                        running = False
                    print navdata
 
            else:
                # error reading frame
                print 'Error reading video feed'
                if drone is not None:
                    print 'Is WiFi connected to drone?'

            video_record(frame)
            if cv2.waitKey(1) & 0xFF == 27:
                # escape key pressed so exit
                running = False
    except:
        traceback.print_exc()

    print 'Shutting down'
    video_record.running = False
    cam.release()
    cv2.destroyAllWindows()


def main():
    """Use command flag '--local' to decide whether to use local camera or drone
    """
    if '--local' in sys.argv:
        run(0, None)
    else:
        camera_port = 'tcp://192.168.1.1:5555'
        drone = libardrone.ARDrone()
        #drone.reset()
        drone.takeoff()
        run(camera_port, drone)
        drone.land()
        drone.halt()


if __name__ == '__main__':
    main()
