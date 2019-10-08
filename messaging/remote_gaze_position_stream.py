import abc
import json
import uuid
from threading import Thread
from pyre import Pyre, zhelper
import zmq

from config import *
from messaging.zmq_connection import setup_subscriber

TOPIC_GAZE_EXCHANGE = "gaze_exchange"
GROUP_GAZE_EXCHANGE = "GAZE_EXCHANGE"
STOP_MESSAGE = "$$STOP"


class AbstractRemoteGazePositionStream(abc.ABC):
    """Class for receiving the gaze positions of all other players"""
    def __init__(self, stream_name="RemoteGazePositionStream"):
        self.name = stream_name
        self.stopped = True
        self.received_gaze_positions = dict()
        self.subscriber = None

    @abc.abstractmethod
    def start(self):
        """
        Starts the stream
        Returns: (RemoteGazePositionStream) self
        """

    def stop(self):
        """
        Stops the stream
        """
        self.stopped = True

    def save_gaze_from_message(self, message):
        """
        Reads the gaze from the given message and the sender id and saves it to received_gaze_positions
        Args:
            message(str): the message
        """
        sender_id, pos_msg = message.split(":")
        positions = pos_msg.split(",")
        if len(positions) != 2:
            print("Wrong gaze received: ", message)
        gaze = float(positions[0]), float(positions[1])
        self.received_gaze_positions[sender_id] = gaze

    def read(self):
        """
        Reads the dictionary with the latest remote gaze positions
        Returns: (dict(str, tuple(float, float))) the gaze positions
        """
        if self.stopped:
            raise ValueError("Stream is not running")
        return self.received_gaze_positions

    def read_list(self):
        """
        Reads the latest remote gaze positions as list
        Returns: (list(tuple(float, float))) the gaze positions
        """
        return [pos for pos in self.read().values()]


class SubscriberRemoteGazePositionStream(AbstractRemoteGazePositionStream):

    def start(self):
        """
        Starts the stream
        Returns: (AbstractRemoteGazePositionStream) self
        """
        self.subscriber = setup_subscriber([TOPIC_GAZE_EXCHANGE], NETWORK_IPS)
        self.subscriber.start()
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        self.stopped = False
        t.start()
        return self

    def update(self):
        """
        Updates the received gaze positions with the latest message
        """
        while not self.stopped:
            _, message = self.subscriber.recv()
            self.save_gaze_from_message(message)


class PyreRemoteGazePositionStream(AbstractRemoteGazePositionStream):
    def __init__(self):
        super().__init__()
        self.publisher_id = None
        self.pyre_pipe = None

    def start(self):
        """
        Starts the stream
        Returns: (AbstractRemoteGazePositionStream) self
        """
        ctx = zmq.Context()
        self.stopped = False
        self.pyre_pipe = zhelper.zthread_fork(ctx, self.gaze_exchange_task)
        return self

    def stop(self):
        """
        Stops the stream
        """
        super().stop()
        self.pyre_pipe.send(STOP_MESSAGE.encode("utf-8"))

    def gaze_exchange_task(self, ctx, pipe):
        """
        Task for exchanging messages
        Args:
            ctx(zmq.Context): the zmq context
            pipe(zmq.PAIR pipe): the pipe for exchanging messages
        Returns: (zmq.PAIR pipe) the pipe
        """
        n = Pyre("GAZE_EXCHANGE")
        self.publisher_id = n.uuid()
        n.join(GROUP_GAZE_EXCHANGE)
        n.start()

        poller = zmq.Poller()
        # noinspection PyUnresolvedReferences
        poller.register(pipe, zmq.POLLIN)
        # noinspection PyUnresolvedReferences
        poller.register(n.socket(), zmq.POLLIN)
        while not self.stopped:
            items = dict(poller.poll())
            print(n.socket(), items)
            # noinspection PyUnresolvedReferences
            if pipe in items and items[pipe] == zmq.POLLIN:
                message = pipe.recv()
                # message to quit
                message = message.decode('utf-8')
                if message == STOP_MESSAGE:
                    break
                print("GAZE_EXCHANGE_TASK: {}".format(message))
                self.save_gaze_from_message(message)
                n.shouts(GROUP_GAZE_EXCHANGE, message)
            else:
                cmds = n.recv()
                msg_type = cmds.pop(0)
                print("NODE_MSG TYPE: %s" % msg_type)
                print("NODE_MSG PEER: %s" % uuid.UUID(bytes=cmds.pop(0)))
                print("NODE_MSG NAME: %s" % cmds.pop(0))
                if msg_type.decode('utf-8') == "SHOUT":
                    print("NODE_MSG GROUP: %s" % cmds.pop(0))
                    message = cmds.pop(0).decode("utf-8")
                    self.save_gaze_from_message(message)
                elif msg_type.decode('utf-8') == "ENTER":
                    headers = json.loads(cmds.pop(0).decode('utf-8'))
                    print("NODE_MSG HEADERS: %s" % headers)
                    for key in headers:
                        print("key = {0}, value = {1}".format(key, headers[key]))
                print("NODE_MSG CONT: %s" % cmds)
        n.stop()
