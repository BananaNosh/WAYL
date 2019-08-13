import os

import cv2
import numpy as np
from imutils import resize
import math
import pygame

from mock import get_random_gaze_positions


def calculate_gaussian_kernel(sigma=100):
    radius = sigma * 3
    window_size = radius * 2 + 1
    kernel_x = np.array([np.arange(window_size) for _ in range(window_size)]) - radius
    kernel_y = kernel_x.T
    kernel = (np.power(kernel_x, 2) + np.power(kernel_y, 2)) / (2 * sigma * sigma)
    # kernel = np.exp(-kernel) * 1 / (np.pi*sigma*sigma)
    kernel = np.exp(-kernel)
    return kernel
    # for x in range(-radius, radius+1):
    #     for y in range(-radius, radius+1):
    #         kernel = x*x + y*y


def initialise_screen():
    pygame.init()
    if True:
        os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
        info = pygame.display.Info()
        _screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
        pygame.mouse.set_visible(0)
    else:
        _screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    _screen.fill((255, 255, 255))
    pygame.display.update()
    return _screen


if __name__ == '__main__':
    width, height = 1200, 675
    screen = initialise_screen()
    sigma = 240
    n = 10
    deg_per_px = math.degrees(math.atan2(.5 * 18.2, 70)) / (.5 * 675)
    print(deg_per_px)
    original_image = cv2.imread(os.path.join("./data", "stimuli", "stimulus1.jpg"))
    original_image = resize(original_image, width=width)
    image = np.copy(original_image)
    gaussian_kernel = calculate_gaussian_kernel(sigma)
    alpha = 1 / (np.mean(gaussian_kernel) * n)
    gaussian_kernel *= alpha
    # gaussian_kernel = np.full_like(gaussian_kernel, np.max(gaussian_kernel))
    window_size = gaussian_kernel.shape[0]
    radius = window_size // 2
    for i in range(100):
        positions = get_random_gaze_positions(n, range(width), range(height))
        # print(positions)
        gaze_filter = np.ones(image.shape[:2])
        for pos_x, pos_y in positions:
            left = pos_x-radius
            left_cut = -min(left, 0)
            right = pos_x+radius
            right_cut = max(right-(width-1), 0)
            top = pos_y-radius
            top_cut = -min(top, 0)
            bottom = pos_y+radius
            bottom_cut = max(bottom-(height-1), 0)  # TODO handle to big kernel
            gaze_filter[top+top_cut:bottom+1-bottom_cut, left+left_cut:right+1-right_cut] \
                += gaussian_kernel[top_cut:window_size-bottom_cut, left_cut:window_size-right_cut]
            # gaze_filter[left+left_cut:right+1-right_cut, top+top_cut:bottom+1-bottom_cut] = 2

        image_mean = np.array([128,128,128])#np.mean(image, axis=(0,1))
        # gaze_filter = np.ones_like(gaze_filter)
        # image_norm = (image - image_mean) / (np.max(image, axis=(0, 1)) - np.min(image, axis=(0, 1)))
        # image_filtered_norm = (gaze_filter[:, :, np.newaxis] * image_norm)
        # image_filtered = ((image_filtered_norm - np.min(image_filtered_norm, axis=(0, 1))) / (np.max(image_filtered_norm, axis=(0, 1)) - np.min(image_filtered_norm, axis=(0, 1))) * 255).astype(np.uint8)
        image_filtered_float = (gaze_filter[:, :, np.newaxis] * (image-image_mean)) + image_mean
        image_filtered_float -= np.min(image_filtered_float, axis=(0, 1))
        image_filtered = (image_filtered_float / np.max(image_filtered_float, axis=(0, 1)) * 255).astype(np.uint8)
        # image = image_filtered
        # image_filtered = ((image_filtered_float + 127.5) / 2).astype(np.uint8)
        # image_filtered = image_filtered / np.max(image_filtered, axis=(0, 1))

        # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # changed_positions = partial_convolve(gray, np.ones((5, 5)), np.array(positions))
        # image[positions] = changed_positions
        # image_with_circles = np.copy(original_image)
        # for pos in positions:
        #     cv2.circle(image_with_circles, pos, 5, (255, 255, 255), thickness=-1)
        # cv2.imshow("im1", image)
        # cv2.imshow("filtered", image_filtered)
        # key = cv2.waitKey(200)
        pygame_image = np.rot90(image_filtered)
        pygame_image = cv2.cvtColor(pygame_image, cv2.COLOR_BGR2RGB)
        screen.blit(pygame.surfarray.make_surface(pygame_image), (0, 0))
        pygame.display.update()
        # if key == ord("q"):
        #     break
    # cv2.destroyAllWindows()
