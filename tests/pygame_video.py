# -*- coding: utf-8 -*-

import pygame
import cv2


def show_video(cam):
    screen = None 
    running = True
    while running:
        # get current frame of video, which is provided as a numpy buffer
        running, frame = cam.read()
        if running:
            size = frame.shape[1::-1]
            if screen is None:
                # now know the size of the video feed can create pygame display
                screen = pygame.display.set_mode(size)
            # create pygame surface from this frame
            surface = pygame.image.fromstring(frame.tostring(), size, "RGB")
            # write surface to pygame screen and flip to render
            screen.blit(surface, (0, 0))
            pygame.display.flip()
        else:
            # error reading frame
            print 'error reading video feed'

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # escape key pressed
                    running = False
            # exit if close window
            if event.type == pygame.QUIT:
                running = False


def main():
    # video feed is on a different port
    cam = cv2.VideoCapture('tcp://192.168.1.1:5555')
    pygame.init()
    try:
        show_video(cam)
    except Exception as e:
        print e
    cam.release()
    pygame.quit()


if __name__ == '__main__':
    main()
