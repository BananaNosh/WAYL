from config import *
from messaging.remote_gaze_position_stream import PyreRemoteGazePositionStream, SubscriberRemoteGazePositionStream, \
    TOPIC_GAZE_EXCHANGE
from messaging.zmq_classes import get_own_ips
from messaging.zmq_connection import setup_publisher
from mock.gaze_exchange_mock import MockPyreRemoteGazePositionStream, MockSubscriberRemoteGazePositionStream

publisher = None
publisher_id = None
remote_gaze_position_stream = None


def setup_gaze_exchange():
    """
    Setup the messaging with the other players
    Returns: (AbstractRemoteGazePositionStream) the stream returning the others' gaze positions
    """
    global remote_gaze_position_stream
    if USE_PYRE_NETWORKING:
        if MOCK_PLAYERS > 0:
            remote_gaze_position_stream = MockPyreRemoteGazePositionStream()
        else:
            remote_gaze_position_stream = PyreRemoteGazePositionStream()
    else:
        if MOCK_PLAYERS > 0:
            remote_gaze_position_stream = MockSubscriberRemoteGazePositionStream()
        else:
            remote_gaze_position_stream = SubscriberRemoteGazePositionStream()
    return remote_gaze_position_stream


def send_gaze(gaze):
    """
    Sends the gaze to all other players
    Args:
        gaze(tuple(float, float)): the gaze to be send
    """
    global publisher, publisher_id
    gaze_string = ",".join([str(pos) for pos in gaze])
    if not USE_PYRE_NETWORKING:
        if publisher is None:
            publisher = setup_publisher()
            publisher_id = get_own_ips()[1] + "_" + str(publisher.pub_port)
        publisher.send(TOPIC_GAZE_EXCHANGE, "{}:{}".format(publisher_id, gaze_string))
    else:
        if publisher_id is None:
            publisher_id = remote_gaze_position_stream.publisher_id
        msg = "{}:{}".format(publisher_id, gaze_string)
        print("try to send ", msg)
        remote_gaze_position_stream.pyre_pipe.send(msg.encode("utf-8"))
