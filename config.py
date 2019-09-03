import os

# paths
STIMULUS_PATH = os.path.join("./data", "stimuli", "stimulus1.jpg")

# ui:
FULLSCREEN = False
SCREEN_WIDTH = 1200     # only used if not FULLSCREEN
SCREEN_HEIGHT = 675    # only used if not FULLSCREEN
IMAGE_WIDTH = 1000


# texts

# network:
# ALLOWED_IPS = ""  # "" == allow all ips
# MASTER_PORT = 5005
# MASTER_HOST_NAME = "NoshsUbuntu"  # TODO change
# THIS_COMPUTER_NAME = "CLIENT1"

# eyetracking
EYE_TRACKING_IP = "localhost"  # usually connected to PC via usb
EYE_TRACKING_PORT = 50020
EYE_TRACKING_MARKERS = [11, 13, 15, 17, 19, 21, 23, 25]  # the shown surface markers
EYE_TRACKING_SURFACE_NAME = "WAYL_Screen"

# general
SCREEN_UPDATE_INTERVAL = 0.1  # the time after which the screen is updated in seconds
SEND_INTERVAL = 0.5
