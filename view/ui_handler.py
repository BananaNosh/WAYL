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
    width, height = screen.get_size()
    x = (width - image.shape[0]) // 2
    y = (height - image.shape[1]) // 2
    screen.blit(pygame.surfarray.make_surface(image), (x, y))
    pygame.display.update()


def draw_point_at_positions(screen, positions):
    for position in positions:
        position = int(position[0] * screen.get_width()), int(position[1] * screen.get_height())
        circle = pygame.draw.circle(screen, (255, 0, 0), position, 4)
        pygame.display.update(circle)


def map_position_between_screen_and_image(position, screen_size, image_size, from_screen_to_image):
    screen_width, screen_height = screen_size
    image_width, image_height = image_size
    x_border = (screen_width - image_width) // 2
    y_border = (screen_height - image_height) // 2
    relative_x_border = x_border / screen_width
    relative_y_border = y_border / screen_height
    relative_image_width = image_width / screen_width
    relative_image_height = image_height / screen_height
    if from_screen_to_image:
        new_x = (position[0] - relative_x_border) / relative_image_width
        new_y = (position[1] - relative_y_border) / relative_image_height
    else:  # from_image_to_screen
        new_x = position[0] * relative_image_width + relative_x_border
        new_y = position[1] * relative_image_height + relative_y_border
    return new_x, new_y
