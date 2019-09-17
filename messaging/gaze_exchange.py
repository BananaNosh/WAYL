try:
    from zyre_pyzmq import Zyre as Pyre
except Exception as e:
    print("using Python native module", e)
    from pyre import Pyre

from pyre import zhelper
import zmq
import uuid
import logging
import json
from threading import Thread

from messaging.zmq_classes import get_own_ips
from messaging.zmq_connection import setup_publisher, setup_subscriber

STOP_MESSAGE = "$$STOP"
TOPIC_GAZE_EXCHANGE = "gaze_exchange"

publisher = None
publisher_id = None
gaze_exchange_pipe = None


def gaze_exchange_task(ctx, pipe):
    n = Pyre("GAZE_EXCHANGE")
    publisher_id = n.uuid()
    n.join("GAZE_EXCHANGE")
    n.start()

    poller = zmq.Poller()
    # noinspection PyUnresolvedReferences
    poller.register(pipe, zmq.POLLIN)
    # noinspection PyUnresolvedReferences
    poller.register(n.socket(), zmq.POLLIN)
    while True:
        items = dict(poller.poll())
        print(n.socket(), items)
        # noinspection PyUnresolvedReferences
        if pipe in items and items[pipe] == zmq.POLLIN:
            message = pipe.recv()
            # message to quit
            if message.decode('utf-8') == STOP_MESSAGE:
                break
            print("GAZE_EXCHANGE_TASK: {}".format(message))
            n.shouts(TOPIC_GAZE_EXCHANGE, message.decode('utf-8'))
        else:
            cmds = n.recv()
            msg_type = cmds.pop(0)
            print("NODE_MSG TYPE: %s" % msg_type)
            print("NODE_MSG PEER: %s" % uuid.UUID(bytes=cmds.pop(0)))
            print("NODE_MSG NAME: %s" % cmds.pop(0))
            if msg_type.decode('utf-8') == "SHOUT":
                print("NODE_MSG GROUP: %s" % cmds.pop(0))
            elif msg_type.decode('utf-8') == "ENTER":
                headers = json.loads(cmds.pop(0).decode('utf-8'))
                print("NODE_MSG HEADERS: %s" % headers)
                for key in headers:
                    print("key = {0}, value = {1}".format(key, headers[key]))
            print("NODE_MSG CONT: %s" % cmds)
    n.stop()


def setup_pyre_messaging():
    global gaze_exchange_pipe
    ctx = zmq.Context()
    gaze_exchange_pipe = zhelper.zthread_fork(ctx, gaze_exchange_task)


def send_gaze(gaze):
    global publisher, publisher_id, gaze_exchange_pipe
    gaze_string = ",".join([str(pos) for pos in gaze])
    if gaze_exchange_pipe is not None:
        gaze_exchange_pipe.send("{}:{}".format(publisher_id, gaze_string).encode("utf-8"))
    else:
        if publisher is None:
            publisher = setup_publisher()
            publisher_id = get_own_ips()[1] + "_" + str(publisher.pub_port)
            print("pub_id", publisher_id)
        publisher.send(TOPIC_GAZE_EXCHANGE, "{}:{}".format(publisher_id, gaze_string))


class RemoteGazePositionStream:
    def __init__(self, stream_name="RemoteGazePositionStream"):
        self.name = stream_name
        self.stopped = True
        self.received_gaze_positions = dict()
        self.subscriber = None

    def start(self):
        self.subscriber = setup_subscriber([TOPIC_GAZE_EXCHANGE])
        self.subscriber.start()
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        self.stopped = False
        t.start()
        return self

    def update(self):
        while not self.stopped:
            _, message = self.subscriber.recv()
            sender_id, pos_msg = message.split(":")
            positions = pos_msg.split(",")
            if len(positions) != 2:
                print("Wrong gaze received: ", message)
            gaze = float(positions[0]), float(positions[1])
            self.received_gaze_positions[sender_id] = gaze
            # self.received_gaze_positions = {
            #     "pl1": (0.5, 0.5),
            #     "pl2": (0.25, 0.75),
            #     "pl3": (0.26, 0.75),
            #     "pl4": (0.9, 0.2),
            #     "pl5": (0.9, 0)
            # }  # TODO update positions via ZMQ or similar

    def read(self):
        if self.stopped:
            raise ValueError("Stream is not running")
        return self.received_gaze_positions

    def read_list(self):
        return [pos for pos in self.read().values()]
