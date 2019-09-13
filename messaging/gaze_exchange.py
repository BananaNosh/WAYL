from threading import Thread

from messaging.zmq_classes import get_own_ips
from messaging.zmq_connection import setup_publisher, setup_subscriber

TOPIC_GAZE_EXCHANGE = "gaze_exchange"

publisher = None
publisher_id = None


def send_gaze(gaze):
    global publisher, publisher_id
    if publisher is None:
        publisher = setup_publisher()
        publisher_id = get_own_ips()[1] + "_" + str(publisher.pub_port)
        print("pub_id", publisher_id)
    publisher.send(TOPIC_GAZE_EXCHANGE, "{}:{}".format(publisher_id, ",".join([str(pos) for pos in gaze])))


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
