from messaging.gaze_exchange import RemoteGazePositionStream as RealRemoteGazePositionStream
from config import *
from numpy.random import rand


class RemoteGazePositionStream(RealRemoteGazePositionStream):
    def read(self, use_pygame_coordinates=True):
        for i in range(MOCK_PLAYERS):
            if i < len(MOCK_POSITIONS):
                pos = MOCK_POSITIONS[i]
                pos = pos[0], 1-pos[1]
            else:
                # noinspection PyTypeChecker
                pos = tuple(round(rand(), 2) for _ in range(2))
            self.received_gaze_positions["Mock_{}".format(i)] = pos
        return super().read(use_pygame_coordinates)