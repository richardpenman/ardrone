# README #

The goal of this project was to test building a simple autonomous drone, however my AR Drone broke before I got far enough...

Be careful if you run this with the AR Drone because the movement tracking has not been debugged - make sure to try outside in a wide open space.


### Overview ###

* ardrone/ - *modified version of [python-ardrone](https://github.com/venthur/python-ardrone) with broken video support removed*
* facedetect.py - *implements face detection*
* facetracker.py - *interface to face tracker*
* movement.py  - *algorithms to track movement of face*
* videorecord.py - *save frames as a video in a background thread*
* data/
    * haarcascade_frontalface_alt.xml - *training data for frontal face detection*
    * haarcascade_profileface.xml - *training data for profile face detection*
* tests/
    * opencv_video.py - *stream drone video using opencv*
    * pygame_video - *display drone stream on a pygame canvas*


### Running ###

    $ # Run face tracker using local webcam
    $ python facetracker.py --local

    $ # Run face tracker using AR Drone connected via WiFi
    $ python facetracker.py