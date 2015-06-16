import cv2


def main():
    # video feed is on a different port
    cam = cv2.VideoCapture('tcp://192.168.1.1:5555')
    running = True
    while running:
        # get current frame of video, which is provided as a numpy buffer
        running, frame = cam.read()
        if running:
            cv2.imshow('frame', frame)
            keycode = cv2.waitKey(1) & 0xFF
            if keycode == 27:
                # escape key pressed
                running = False
        else:
            # error reading frame
            print 'error reading video feed'
    cam.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
