import os

# paths
STIMULUS_PATH = os.path.join("./data", "stimuli", "stimulus1.jpg")

# ui:
FULLSCREEN = False
SCREEN_WIDTH = 1400  # only used if not FULLSCREEN
SCREEN_HEIGHT = 788  # only used if not FULLSCREEN
IMAGE_WIDTH = 1000
IMAGE_HEIGHT = 563

# texts

# network:
# use the Pyre framework for connecting to local network (turn off if you get "group GAZE_EXCHANGE not found" error)
USE_PYRE_NETWORKING = True
# the ip addresses of all connecting computers in local network (only used if not USE_PYRE_NETWORKING)
NETWORK_IPS = ["localhost"]

# eyetracking
EYE_TRACKING_IP = "localhost"  # usually connected to PC via usb
EYE_TRACKING_PORT = 50020
EYE_TRACKING_MARKERS = [11, 13, 15, 17, 19, 21, 23, 25]  # the shown surface markers
EYE_TRACKING_SURFACE_NAME = "WAYL_Screen"

# general
SCREEN_UPDATE_INTERVAL = 1  # the time after which the screen is updated in seconds
SEND_INTERVAL = 0.5

# Fixations
FIXATION_OVERLAY_SIGMA = 120  #240  # in pixel

# testing
TURN_OFF_EYE_TRACKING = False
MOCK_PLAYERS = 2  # number of fake player for which a fake position is shown only in this client
MOCK_POSITIONS = []  # the fake positions shown e.g.[(0.5, 0.5), (0.2, 0,3)] (in relative image coordinates)
# if len(MOCK_POSITIONS) is smaller than MOCK_PLAYERS, the other positions are dynamically randomly changed
