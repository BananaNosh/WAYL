import msgpack
import zmq


class Subscriber:
    def __init__(self, ip, sub_port, subjects):
        """
        Creates a Subscriber wrapping a zmq.SUB socket listening to the given subjects
        Args:
            ip(str)): the ip to subscribe to
            sub_port(int): the port to subscribe on
            subjects(list(str)): the subject to subscribe on
        """
        self.ip = ip
        self.sub_port = sub_port
        self.subjects = subjects
        # noinspection PyUnresolvedReferences
        self.subscriber = zmq.Context().socket(zmq.SUB)

    def start(self):
        """
        Connects the subscriber to the given ip and port and subscribes to the given subjects
        Returns: (Subscriber) self
        """
        self.subscriber.connect("tcp://{}:{}".format(self.ip, self.sub_port))
        for s in self.subjects:
            # noinspection PyUnresolvedReferences
            # self.subscriber.set(zmq.SUBSCRIBE, s.encode())
            # noinspection PyUnresolvedReferences
            self.subscriber.setsockopt(zmq.SUBSCRIBE, s.encode())
        return self

    def recv(self, timeout=None):
        """
        Receives the next message from the subscriber
        Args:
            timeout(int|None): if not None the maximal timeout milliseconds are waited for a message
        Returns: (str|None) the received message or None if timed out
        """
        while True:
            try:
                if timeout is not None:
                    # self.subscriber.RCVTIMEO = timeout
                    # noinspection PyUnresolvedReferences
                    if self.subscriber.poll(timeout, zmq.POLLIN):
                        # noinspection PyUnresolvedReferences
                        topic, payload = self.subscriber.recv_multipart(zmq.NOBLOCK)
                    else:
                        print("timeout error")
                        return None
                else:
                    topic, payload = self.subscriber.recv_multipart()
                message = msgpack.loads(payload)
                topic = topic.decode()
                return topic, message
            except zmq.error.Again:
                continue


class Publisher:
    def __init__(self, pub_port):
        """
        Creates a Publisher wrapping a zmq.PUB socket which can broadcast messages
        Args:
            pub_port(int): the port to publish on
        """
        self.pub_port = pub_port
        # noinspection PyUnresolvedReferences
        self.publisher = zmq.Context().socket(zmq.PUB)

    def start(self):
        """
        Binds the publisjer to the given port
        Returns: (Subscriber) self
        """
        self.publisher.bind("tcp://*:%s" % self.pub_port)
        return self

    def send(self, topic, message):
        """
        Sends a message for a specific topic
        Args:
            topic(str): the topic
            message(str): the message
        """
        print("Pub sends {} {}".format(topic, message))
        payload = msgpack.dumps(message)
        self.publisher.send_multipart((topic.encode(), payload))
