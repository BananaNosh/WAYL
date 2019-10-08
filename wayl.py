import time

import cv2
import numpy as np
import pygame
from imutils import resize

from config import *
from eye_tracking.eye_tracking import start_gaze_stream_and_wait
from eye_tracking.pupil_labs.start_pupil_capture import start_pupil_capture
from fixation_layering.fixation_layering import filter_image_with_positions, calculate_gaussian_kernel, \
    map_position_to_np_pixel
from messaging.gaze_exchange import send_gaze, setup_gaze_exchange
from view.ui_handler import initialise_screen, show_markers, show_calibration, show_image, \
    map_position_between_screen_and_image, activate_total_fullscreen


def read_image():
    """
    Reads the image as configured in the config and converts it to RGB
    Returns: (ndarray) the read image
    """
    _image = cv2.imread(STIMULUS_PATH)
    _image = resize(_image, width=IMAGE_WIDTH)
    _image = cv2.cvtColor(_image, cv2.COLOR_BGR2RGB)
    _image = np.rot90(_image)
    return _image


def main_loop(_screen, _image, _gaze_stream):
    show_image(screen, image)

    filtered_image = _image.copy()
    gaussian_kernel = calculate_gaussian_kernel(FIXATION_OVERLAY_SIGMA)

    remote_positions_stream = setup_gaze_exchange().start()
    last_screen_update_time = 0
    last_send_time = 0
    while True:
        event = pygame.event.poll()
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            # finish on escape clicked
            remote_positions_stream.stop()
            if gaze_stream is not None:
                gaze_stream.stopped = True
            break
        # only update after a given interval
        current_time = time.time()
        if current_time - last_screen_update_time < SCREEN_UPDATE_INTERVAL:
            continue
        last_screen_update_time = current_time
        show_image(_screen, filtered_image)
        fixations_on_screen = remote_positions_stream.read_list()
        fixations_on_image = [
            map_position_to_np_pixel(
                map_position_between_screen_and_image(pos, _screen.get_size(), image.shape[:2], True),
                image
            ) for pos in fixations_on_screen
        ]
        fixations_on_image_not_none = [fix for fix in fixations_on_image if fix is not None]
        # print("fixation", fixations_on_image)
        filtered_image = filter_image_with_positions(image, fixations_on_image_not_none, gaussian_kernel)

        if current_time - last_send_time < SEND_INTERVAL:
            continue
        last_send_time = current_time
        # read position in pygame coordinates
        position = gaze_stream.read_position() if gaze_stream is not None else None
        print(position)
        if position is not None:
            send_gaze(position)


def prepare_gaze_reading():
    if TURN_OFF_EYE_TRACKING:
        return None
    show_markers(screen)
    return start_gaze_stream_and_wait(EYE_TRACKING_IP, EYE_TRACKING_PORT, EYE_TRACKING_SURFACE_NAME)


if __name__ == '__main__':
    if not TURN_OFF_EYE_TRACKING:
        start_pupil_capture()
    screen = initialise_screen()
    if not TURN_OFF_EYE_TRACKING:
        show_calibration()
    if FULLSCREEN:  # necessary here as calibration does not work with fullscreen
        activate_total_fullscreen(screen)
        pass
    image = read_image()
    gaze_stream = prepare_gaze_reading()
    main_loop(screen, image, gaze_stream)
    pygame.display.quit()
    pygame.quit()
