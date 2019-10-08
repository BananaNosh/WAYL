import numpy as np
import pygame

from config import *


def calculate_gaussian_kernel(_sigma=100):
    _radius = _sigma * 3
    _window_size = _radius * 2 + 1
    kernel_x = np.array([np.arange(_window_size) for _ in range(_window_size)]) - _radius
    kernel_y = kernel_x.T
    kernel = (np.power(kernel_x, 2) + np.power(kernel_y, 2)) / (2 * _sigma * _sigma)
    kernel = np.exp(-kernel)
    return kernel


def initialise_screen():
    pygame.init()
    if FULLSCREEN:
        os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
        info = pygame.display.Info()
        _screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
        pygame.mouse.set_visible(0)
    else:
        _screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    _screen.fill((255, 255, 255))
    pygame.display.update()
    return _screen


def gaze_filter_for_positions(_positions, image_size, _gaussian_kernel):
    """
    Creates an overlay of same size as the image with gaussians at the positions
    Args:
        _positions(list(tuple)): the fixation positions in pixel on the image
        image_size(tuple): the size of the image
        _gaussian_kernel(ndarray): the gaussian kernel
    Returns: (ndarray) the overlay for the image
    """
    kernel_window_size = _gaussian_kernel.shape[0]
    kernel_radius = kernel_window_size // 2
    _gaze_filter = np.ones(image_size)
    image_height, image_width = image_size
    for pos_x, pos_y in _positions:
        left = pos_x - kernel_radius  # left position of the kernel
        left_cut = -min(left, 0)  # number of pixels overhanging on the left of the image
        right = pos_x + kernel_radius  # right position of the kernel
        right_cut = max(right - (image_width - 1), 0)  # number of pixels overhanging on the right of the image
        top = pos_y - kernel_radius  # top position of the kernel
        top_cut = -min(top, 0)  # number of pixels overhanging on the top of the image
        bottom = pos_y + kernel_radius  # bottom position of the kernel
        bottom_cut = max(bottom - (image_height - 1), 0)  # number of pixels overhanging on the bottom of the image
        _gaze_filter[top + top_cut:bottom + 1 - bottom_cut, left + left_cut:right + 1 - right_cut] \
            += _gaussian_kernel[top_cut:kernel_window_size - bottom_cut, left_cut:kernel_window_size - right_cut]
    return _gaze_filter


def filter_image_with_positions(_image, _positions, _gaussian_kernel, _mapping_back_to_range_values=None):
    """
    Filters the image according to the given positions with the given gaussian kernel
    Args:
        _image(ndarray): the image to filter
        _positions(list(tuple)): the positions in pixel
        _gaussian_kernel(ndarray): the gaussian kernel
        _mapping_back_to_range_values(tuple(float, float)|None): possibly precalculated values
        used to map the filtered image back onto the 0-255 range
    Returns: (ndarray) the filtered image
    """
    if _mapping_back_to_range_values is None:
        _mapping_back_to_range_values = get_mapping_back_to_range_values(_gaussian_kernel, len(_positions))
    gaze_filter = gaze_filter_for_positions(_positions, _image.shape[:2], _gaussian_kernel)
    image_mean = np.array([128, 128, 128])  # np.mean(image, axis=(0,1))
    image_filtered_float = (gaze_filter[:, :, np.newaxis] * (_image - image_mean)) + image_mean
    image_filtered_norm = image_filtered_float * _mapping_back_to_range_values[0] + _mapping_back_to_range_values[1]
    _image_filtered = np.clip(image_filtered_norm, 0, 255).astype(np.uint8)
    return _image_filtered


def get_mapping_back_to_range_values(_gaussian_kernel, number_of_positions):
    """
    Precalculate values used to map the filtered image back onto the 0-255 range
    Args:
        _gaussian_kernel(ndarray): the gaussian kernel
        number_of_positions(int): the number of positions used in the filter process
    Returns: (float, float) the scale factor and the shift value
    """
    if number_of_positions <= 5:
        number_of_persons_looking_at_same_point = max(1, number_of_positions)
    elif number_of_positions <= 10:
        number_of_persons_looking_at_same_point = 5 + (number_of_positions - 5) // 2
    else:
        number_of_persons_looking_at_same_point = 8 + (number_of_positions - 10) // 3
    overlay_max = np.max(_gaussian_kernel) * number_of_persons_looking_at_same_point
    mapping_back_to_range_factor = 1 / overlay_max
    mapping_back_to_range_shift = 128 * (overlay_max - 1) / overlay_max
    return mapping_back_to_range_factor, mapping_back_to_range_shift


def map_position_to_np_pixel(position, _image):
    """
    Maps the positions from the image frame to the np pixels
    Args:
        position((float, float)): the position in the image frame in range 0.0-1.0
        _image(ndarray): the image the coordinates are mapped on
    Returns: (int, int) the np pixel position
    """
    if np.min(position) < 0 or np.max(position) > 1:
        return None  # position is not within image
    image_width, image_height = _image.shape[:2]
    return int(position[1] * image_height), int(position[0] * image_width)