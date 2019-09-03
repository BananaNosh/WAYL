from threading import Thread


def send_gaze(gaze):
    pass


class RemoteGazePositionStream:
    def __init__(self, stream_name="RemoteGazePositionStream"):
        self.name = stream_name
        self.stopped = True
        self.received_gaze_positions = dict()

    def start(self):
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        self.stopped = False
        t.start()
        return self

    def update(self):
        while not self.stopped:
            self.received_gaze_positions = {
               "pl1": (0.5, 0.5),
               "pl2": (0.25, 0.75) ,
               "pl3": (0.26, 0.75) ,
               "pl4": (0.9, 0.2),
               "pl5": (0.9, 0)
            }  # TODO update positions via ZMQ or similar

    def read(self):
        if self.stopped:
            raise ValueError("Stream is not running")
        return self.received_gaze_positions

    def read_list(self):
        return [pos for pos in self.read().values()]