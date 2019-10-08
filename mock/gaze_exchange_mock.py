import abc

from numpy import clip
from numpy.random import rand

from config import *
from messaging.remote_gaze_position_stream import AbstractRemoteGazePositionStream, PyreRemoteGazePositionStream, \
    SubscriberRemoteGazePositionStream
from view.ui_handler import map_position_between_screen_and_image


class AbstractMockRemoteGazePositionStream(AbstractRemoteGazePositionStream, abc.ABC):
    """MockRemoteGazepositionStream adds mock positions to the received ones"""
    @abc.abstractmethod
    def read_super_positions(self):
        """
        Call read of the correct super class
        """
        pass

    def read(self):
        """
        Reads the dictionary with the latest remote gaze positions and adds the mock positions
        Returns: (dict(str, tuple(float, float))) the gaze positions
        """
        for i in range(MOCK_PLAYERS):
            if i < len(MOCK_POSITIONS):
                pos = MOCK_POSITIONS[i]
                pos = pos[0], pos[1]
            else:
                # noinspection PyTypeChecker
                pos = tuple(round(rand(), 2) for _ in range(2))
            print("before", pos)
            pos = clip(pos, 0.01, 0.99)
            pos = map_position_between_screen_and_image(pos, (SCREEN_WIDTH, SCREEN_HEIGHT),
                                                        (IMAGE_WIDTH, IMAGE_HEIGHT), False)
            print("after", pos)
            self.received_gaze_positions["Mock_{}".format(i)] = pos
        return super().read()


class MockPyreRemoteGazePositionStream(PyreRemoteGazePositionStream, AbstractMockRemoteGazePositionStream):
    def read_super_positions(self):
        return super(PyreRemoteGazePositionStream).read()


class MockSubscriberRemoteGazePositionStream(SubscriberRemoteGazePositionStream, AbstractMockRemoteGazePositionStream):
    def read_super_positions(self):
        return super(SubscriberRemoteGazePositionStream).read()
