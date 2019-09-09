import time
from threading import Thread

from messaging.zmq_classes import Subscriber, Publisher

PORT = 5010


def subscribe_test():
    subscriber = Subscriber("localhost", PORT, ["test"])
    subscriber.start()
    while True:
        message = subscriber.recv()
        print("Got message {}".format(message))


if __name__ == '__main__':
    t = Thread(target=subscribe_test, name="subscribe_test", args=())
    t.start()
    publisher = Publisher(PORT)
    publisher.start()
    publisher2 = Publisher(PORT)
    publisher2.start()
    time.sleep(1)
    while True:
        publisher.send("test", "Hello World")
