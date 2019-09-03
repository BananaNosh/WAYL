import numpy as np
import pygame

from config import *
from eye_tracking.eye_tracking import calibrate, get_sub_port
from eye_tracking.surface_markers import SurfaceMarkerCreator


def initialise_screen():
    pygame.init()
    if FULLSCREEN:
        os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
        info = pygame.display.Info()
        _screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
        pygame.mouse.set_visible(0)
    else:
        _screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        _width, _height = _screen.get_size()
    _screen.fill((255, 255, 255))
    pygame.display.update()
    return _screen


def show_markers(screen):
    SurfaceMarkerCreator(EYE_TRACKING_MARKERS).draw(screen)
    pygame.display.update()


def show_calibration():
    sub_port = get_sub_port(EYE_TRACKING_IP, EYE_TRACKING_PORT)
    calibrate(EYE_TRACKING_IP, EYE_TRACKING_PORT, sub_port)


def activate_total_fullscreen(_screen):
    """
    Change the screen to fullscreeen mode
    Args:
        _screen(Screen): the pygame screen
    """
    old_screen = _screen.copy()
    _screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    _screen.blit(old_screen, (0, 0))
    pygame.display.update()


def show_image(screen, image):
    """
    Shows the image on the screen
    Args:
        screen(Screen): the pygame screen
        image(ndarray): the image as numpy array in RGB
    """
    pygame_image = np.rot90(image)  # TODO maybe move
    width, height = screen.get_size()
    x = (width - image.shape[1]) // 2
    y = (height - image.shape[0]) // 2
    screen.blit(pygame.surfarray.make_surface(pygame_image), (x, y))
    pygame.display.update()


def draw_point_at_positions(screen, positions):
    for position in positions:
        position = int(position[0] * screen.get_width()), int(position[1] * screen.get_height())
        pygame.draw.circle(screen, (255, 0, 0), position, 4)
    pygame.display.update()