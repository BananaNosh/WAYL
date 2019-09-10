import time
from threading import Thread

import msgpack
import zmq
from netifaces import interfaces, ifaddresses, AF_INET

ALIVE_TOPIC = "_alive"


class Subscriber:
    def __init__(self, ip, port, subjects):
        """
        Creates a Subscriber wrapping a zmq.SUB socket listening to the given subjects
        Args:
            ip(str|None): the ip to subscribe to (can be None if add_additional_ips is used)
            port(int|None): the port to subscribe on (can be None if add_additional_ips is used)
            subjects(list(str)): the subject to subscribe on
        """
        self.ip_and_ports = {}  # the ip-port-combinations with their last alive time
        if ip is not None and port is not None:
            self.ip_and_ports[(ip, port)] = 0.0
        self.subjects = subjects
        # noinspection PyUnresolvedReferences
        self.subscriber = zmq.Context().socket(zmq.SUB)
        self.check_alive_thread = None
        self.timeout = 0
        self.check_alive_subscriber = None

    def add_additional_ips(self, ip_and_ports):
        """
        Add additional ip-port-combinations on which the subscriber will listen to data
        Args:
            ip_and_ports(list(tuple(str, int))): the list of additional ips and ports
        Returns: (Subscriber) self
        """
        for ip, port in ip_and_ports:
            self.ip_and_ports[(ip, port)] = 0.0
        return self

    def set_connection_timeout(self, timeout):
        """
        Sets a connection timeout after which all connections which did not recently send an ALIVE_TOPIC message
        are disconnected
        Args:
            timeout(int): the timeout in milliseconds
        """
        self.check_alive_subscriber = Subscriber("", 0, []).add_additional_ips(self.ip_and_ports.keys())
        # noinspection PyUnresolvedReferences
        self.check_alive_subscriber.subscriber.setsockopt(zmq.SUBSCRIBE, ALIVE_TOPIC.encode())

        def check_alive():
            last_check_time = time.time()
            while True:
                received = self.check_alive_subscriber.recv(self.timeout)
                if received is None:  # did not get any alive signal -> disconnect from all ips
                    break
                if received[1] is None:
                    continue
                alive_ip, alive_port = received[1].split(":")
                alive_port = int(alive_port)
                current_time = time.time()
                if (alive_ip, alive_port) in self.ip_and_ports:
                    self.ip_and_ports[(alive_ip, alive_port)] = current_time  # update last alive time
                if current_time - last_check_time > self.timeout / 1000:  # check all ips for alive
                    last_check_time = current_time
                    remaining_ips = {}
                    for (ip, port), last_alive_time in self.ip_and_ports.items():
                        if current_time - last_alive_time < timeout:
                            remaining_ips[(ip, port)] = self.ip_and_ports[(ip, port)]
                        else:
                            try:
                                self.subscriber.disconnect("tcp://{}:{}".format(ip, port))
                                time.sleep(0.001)
                            except zmq.ZMQError as e:
                                print("error", e)
                                pass
                    self.ip_and_ports = remaining_ips
            self.ip_and_ports.clear()
            self.subscriber.close()

        self.timeout = timeout
        if self.check_alive_thread is None:
            self.check_alive_thread = Thread(target=check_alive, name="check_alive", args=())
            self.check_alive_thread.setDaemon(True)

    def start(self):
        """
        Connects the subscriber to the given ip and port and subscribes to the given subjects
        Returns: (Subscriber) self
        """
        for ip, port in self.ip_and_ports:
            self.subscriber.connect("tcp://{}:{}".format(ip, port))
        for s in self.subjects:
            if s == ALIVE_TOPIC:
                raise ValueError("topic {} is reserved".format(ALIVE_TOPIC))
            # noinspection PyUnresolvedReferences
            self.subscriber.setsockopt(zmq.SUBSCRIBE, s.encode())
        if self.check_alive_thread is not None:
            self.check_alive_subscriber.start()
            self.check_alive_thread.start()
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
                        received = self.subscriber.recv_multipart(zmq.NOBLOCK)
                    else:
                        print("timeout error")
                        return None
                else:
                    received = self.subscriber.recv_multipart()
                topic = received[0]
                message = msgpack.loads(received[1]) if len(received) > 1 else None
                if type(message) is bytes:
                    message = message.decode()
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

    def send_alive_signal(self, interval):
        """
        Start a thread which sends a ALIVE_TOPIC message every interval milliseconds
        with the publishers ips and port
        Args:
            interval(int): the interval in milliseconds
        """
        pub_ips = get_own_ips()

        def send_alive():
            while True:
                for ip in pub_ips:
                    self.send(ALIVE_TOPIC, "{}:{}".format(ip, self.pub_port))
                time.sleep(interval / 1000)

        send_alive_thread = Thread(target=send_alive, name="send_alive", args=())
        send_alive_thread.setDaemon(True)
        send_alive_thread.start()

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


def get_own_ips():
    """
    Returns the ips of this device for every interface
    Returns: (list(str)) the list of ips
    """
    own_ips = []
    for interface in interfaces():
        address_key = 'addr'
        addresses = [i[address_key] for i in ifaddresses(interface).setdefault(AF_INET, [{'addr': None}]) if
                     i[address_key] is not None]
        own_ips.extend(addresses)
    return own_ips
