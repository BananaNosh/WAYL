import sys
from threading import Thread

import msgpack
import zmq

from helper import current_time_string
from messaging.zmq_classes import Subscriber


class SurfaceGazeStream:
    def __init__(self, ip, port, sub_port, surface_name="unnamed", stream_name="GazeStream", verbose=False):
        """
        Creates a stream which returns the gaze positions on a certain surface
        Args:
            ip(str): the ip of the pupil labs eye tracker (usually "localhost")
            port(int): the port of the pupil labs eye tracker
            sub_port(int): the SUB port of the ey
            surface_name(str): the name of the surface to be monitored
            stream_name(str): the name of the stream
            verbose(bool): if there should be printed more information
        """
        self.name = stream_name
        self.stopped = False
        # self.subscriber = zmq.Context().socket(zmq.SUB)
        self.subscriber = Subscriber(ip, sub_port, ["logging.error", "logging.warning", "gaze",
                                                    "surfaces.{}".format(surface_name)])
        self.ip = ip
        self.port = port
        self.sub_port = sub_port
        self.surface_gaze_datum = None
        self.frame = None
        self.started_plugin = False
        self.verbose = verbose

    def start(self):
        """
        Starts the subscriber listening to the surface data on a new Thread
        Returns: (SurfaceGazeStream) self
        """
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        self.start_surface_tracker_plugin()
        self.subscriber.start()
        self.stopped = False
        t.start()
        return self

    def update(self):
        """
        Updates its last received surface_gaze_datum if not stopped
        """
        while True:
            if self.stopped:
                return
            topic, message = self.subscriber.recv()
            if topic.startswith("gaze"):
                if self.verbose:
                    print("GazeStream-gaze: {}".format(message))
            elif topic.startswith("surfaces"):
                if self.verbose:
                    print("GazeStream-surfaces: {}".format(message))
                self.surface_gaze_datum = message
            else:
                if self.verbose:
                    print("GazeStream-{}:  {}".format(topic, message["msg".encode()]))

    def read(self):
        """
        Returns: (dict) the lates suface gaze datum
        """
        return self.surface_gaze_datum

    def read_position(self, use_pygame_coordinates=True):
        """
        Reads the latest gaze position from the surface gaze datum
        Args:
            use_pygame_coordinates(bool): if the coordinates should be mapped to pygame coordinate system
        Returns: (tuple(float, float)|None) the latest position or None
        """
        if self.surface_gaze_datum is None:
            return None
        gazes = self.surface_gaze_datum["gaze_on_srf".encode()]
        gazes_on_surface = [g for g in gazes if g["on_srf".encode()]]
        gazes_on_surface = sorted(gazes_on_surface, key=lambda g: g["confidence".encode()], reverse=True)
        if len(gazes_on_surface) == 0:
            return None
        norm_pos = gazes_on_surface[0]["norm_pos".encode()]
        confidence = gazes_on_surface[0]["confidence".encode()]
        if confidence < 0.5:
            print("confidence", confidence)
            return None
        return tuple(norm_pos) if not use_pygame_coordinates else norm_pos[0], 1 - norm_pos[1]

    def stop(self):
        """
        Stops the stream
        """
        self.stopped = True

    def start_surface_tracker_plugin(self):
        """
        Starts the surface tracker plugin used to communicate with the eye tracker
        """
        if not self.started_plugin:
            req = get_connected_requester(self.ip, self.port)
            send_recv_notification(req, {'subject': 'start_plugin', 'name': 'Surface_Tracker',
                                         'args': {'min_marker_perimeter': 50}})
            self.started_plugin = True


def get_connected_requester(ip, port):
    """
    Creates a requester to send commands to pupil labs for the given ip and port
    Args:
        ip(str): the ip of the eye tracker
        port(int): the port of the eye tracker
    Returns: (zmq.REQ socket) the requester
    """
    ctx = zmq.Context()
    # noinspection PyUnresolvedReferences
    requester = ctx.socket(zmq.REQ)
    push_url = "tcp://{}:{}".format(ip, port)
    requester.connect(push_url)
    return requester


def calibrate(ip, port, sub_port, subscriber=None, requester=None, retries=0):
    """
    Start the calibration of the eye tracker and retries it up to three times if failing
    Args:
        ip(str): the ip of the eye tracker
        port(int): the port of the eye tracker
        sub_port(int): the SUB port of the eye tracker
        subscriber(Subscriber|None): a Subscriber already created for the calibration or None
        requester(zmq.REQ socket): a requester socket to send commands
        retries(int): the number of already executed retries
    """
    def on_failed():
        """Called if the calibration fails several times"""
        sys.exit(1)

    n = {"subject": "calibration.should_start"}
    subscriber = Subscriber(ip, sub_port, ["notify.calibration"]) if subscriber is None else subscriber
    subscriber.start()
    requester = get_connected_requester(ip, port) if requester is None else requester
    notification_feedback = send_recv_notification(requester, n)
    print(current_time_string(), "Calibration start feedback: {}".format(notification_feedback))
    started = False

    while True:
        timeout = 5000 if not started else 90000
        message = subscriber.recv(timeout=timeout)
        if message is None:
            print(current_time_string(),
                  "Timed out waiting for calibration {}, retry...".format("start" if not started else "end"))
            notification_feedback = send_recv_notification(requester, {"subject": "calibration.should_stop"})
            print(current_time_string(), "Calibration stop feedback: {}".format(notification_feedback))
            if retries < 3 and not started:
                calibrate(ip, port, sub_port, subscriber, requester, retries+1)
            else:
                on_failed()
            return
        topic, message = message
        topic = topic[19:]
        print("Calibration: {}".format(topic))
        if topic == "should_start":
            continue
        if topic == "started":
            started = True
            continue
        if not started:
            print("Calibration did not start correctly")
            on_failed()
        elif topic == "failed":
            print("Calibration failed: {}".format(message["reason".encode()].decode()))
            on_failed()
        elif topic == "stopped":
            print("Finished calibration")
            break


def get_sub_port(ip, port):
    """
    Gets the SUB port according to the eye tracker ip and port
    Args:
        ip(str): the eye tracker ip
        port(int): the eye tracker port
    Returns: (int) the SUB port
    """
    requester = get_connected_requester(ip, port)
    requester.send_string('SUB_PORT')
    sub_port = requester.recv_string()
    return sub_port


def send_recv_notification(requester, notification):
    """
    Send a notification(a command e.g.) with the requester and wait for a confirmation
    Args:
        requester(zmq.REQ socket): the requester to use
        notification(dict): a dictionary containing the notification
    Returns: (str): the feedback for the request
    """
    requester.send_multipart(('notify.{}'.format(notification['subject']).encode(), msgpack.dumps(notification)))
    return requester.recv()


def start_gaze_stream_and_wait(ip, port, surface_name):
    """
    Starts a SurfaceGazeStream and waits until it sends data
    Args:
        ip(str): the eye tracker ip
        port(int): the eye tracker port
    Returns: (SurfaceGazeStream) the created GazeStream
    """
    gaze_stream = SurfaceGazeStream(ip, port, get_sub_port(ip, port),
                                    surface_name=surface_name)
    gaze_stream.start()
    while gaze_stream.read() is None:
        pass
    return gaze_stream
