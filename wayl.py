import pygame
import cv2
import os
from imutils import resize
import time

from eye_tracking.eye_tracking import SurfaceGazeStream, get_sub_port, start_gaze_stream_and_wait
from eye_tracking.pupil_labs.start_pupil_capture import start_pupil_capture
from fixation_layering import filter_image_with_positions, calculate_gaussian_kernel, get_mapping_back_to_range_values
from messaging.gaze_exchange import send_gaze, RemoteGazePositionStream
from view.ui_handler import initialise_screen, show_markers, show_calibration, show_image, activate_total_fullscreen, \
    draw_point_at_positions
from config import *


def read_image():
    """
    Reads the image as configured in the config and converts it to RGB
    Returns: (ndarray) the read image
    """
    _image = cv2.imread(STIMULUS_PATH)
    _image = resize(_image, width=IMAGE_WIDTH)
    _image = cv2.cvtColor(_image, cv2.COLOR_BGR2RGB)
    return _image


def map_position_between_screen_and_image(position, _screen, _image, from_screen_to_image):
    width, height = _screen.get_size()
    image_height, image_width = _image.shape[:2]
    x_border = (width - image_width) // 2
    y_border = (height - image_height) // 2
    relative_x_border = x_border / width
    relative_y_border = y_border / height
    relative_image_width = image_width / width
    relative_image_height = image_height / height
    if from_screen_to_image:
        new_x = (position[0] - relative_x_border) / relative_image_width
        new_y = (position[1] - relative_y_border) / relative_image_height
    else:  # from_image_to_screen
        new_x = position[0] * relative_image_width + relative_x_border
        new_y = position[1] * relative_image_height + relative_y_border
    return new_x, new_y


def map_position_to_pixel(position, _image):
    image_height, image_width = _image.shape[:2]
    return int(position[0] * image_width), int(position[1] * image_height)


def main_loop(_screen, _image, _gaze_stream):
    show_image(screen, image)

    filtered_image = _image.copy()
    gaussian_kernel = calculate_gaussian_kernel(FIXATION_OVERLAY_SIGMA)

    remote_positions_stream = RemoteGazePositionStream()
    remote_positions_stream.start()
    last_screen_update_time = 0
    last_send_time = 0
    while True:
        event = pygame.event.poll()
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            # finish on escape clicked
            break
        # only update after a given interval
        current_time = time.time()
        if current_time - last_screen_update_time < SCREEN_UPDATE_INTERVAL:
            continue
        last_screen_update_time = current_time
        show_image(_screen, filtered_image)
        show_markers(_screen)

        if current_time - last_send_time < SEND_INTERVAL:
            continue
        last_send_time = current_time
        # position = _gaze_stream.read_position()
        # send_gaze(map_position_between_screen_and_image(position, _screen, _image, True))

        # fixations = [map_position_between_screen_and_image(fix, _screen, _image, False)
        #              for fix in remote_positions_stream.read_list()]
        # draw_point_at_positions(_screen, fixations)
        fixations_on_image = [map_position_to_pixel(pos, image) for pos in remote_positions_stream.read_list()]
        filtered_image = filter_image_with_positions(image, fixations_on_image, gaussian_kernel)


def prepare_gaze_reading():
    show_markers(screen)
    return start_gaze_stream_and_wait(EYE_TRACKING_IP, EYE_TRACKING_PORT, EYE_TRACKING_SURFACE_NAME)


if __name__ == '__main__':
    # start_pupil_capture()
    screen = initialise_screen()
    # show_calibration()
    if FULLSCREEN:  # necessary here as calibration does not work with fullscreen
        # activate_total_fullscreen(screen)
        pass
    image = read_image()
    gaze_stream = None # prepare_gaze_reading()
    main_loop(screen, image, gaze_stream)
