import time
from threading import Thread

import zmq

from messaging.zmq_classes import Subscriber, Publisher, get_own_ips

CONNECTION_TIMEOUT = 10000
NUMBERS_PER_IP_OCTET = 255

PORT_RANGE = range(5010, 5020)


def subscribe_test():
    subscriber = setup_subscriber(["test"])
    subscriber.set_connection_timeout(CONNECTION_TIMEOUT)
    subscriber.start()
    while True:
        message = subscriber.recv()
        print("Got message {}".format(message))
        print(len(subscriber.ip_and_ports))


def setup_subscriber(topics):
    """
    Setups a subscriber on all possible ips in the local network for the given topics
    Args:
        topics(list(str)): the topics
    Returns: (Subscriber) the setup subscriber
    """
    subscriber = Subscriber(None, None, topics)
    ips = get_possible_network_ips()
    ips_and_ports = [(ip, p) for ip in ips for p in PORT_RANGE]
    subscriber.add_additional_ips(ips_and_ports)
    subscriber.set_connection_timeout(CONNECTION_TIMEOUT)
    return subscriber


def get_possible_network_ips():
    """
    Get all possible ips in the local network
    Returns: (list(str)) the ips
    """
    all_ips = []
    own_ips = get_own_ips()
    for own_ip in own_ips:
        ip_basis, last_octet = own_ip.rsplit('.', 1)
        is_localhost = ip_basis == "127.0.0"
        ip_range = range(NUMBERS_PER_IP_OCTET) if not is_localhost else range(1, 2)
        for i in ip_range:
            ip = ".".join([ip_basis, str(i)])
            if ip != own_ip or is_localhost:
                all_ips.append(ip)
    return all_ips


def setup_publisher():
    """
    Setups a publisher on the first unused port in PORT_RANGE
    Returns: (Publisher) the setup publisher
    """
    for p in PORT_RANGE:
        try:
            _publisher = Publisher(p)
            _publisher.start()
            print("Publisher started on port", p)
            _publisher.send_alive_signal(CONNECTION_TIMEOUT)
            return _publisher
        except zmq.error.ZMQError as e:
            if e.args[0] == 98:
                print("Port already used, trying next one!")
            else:
                raise e
    raise zmq.error.ZMQError(-1, "No unused port found in PORT_RANGE")


if __name__ == '__main__':
    t = Thread(target=subscribe_test, name="subscribe_test", args=())
    t.setDaemon(True)
    t.start()
    publisher = setup_publisher()
    # publisher2 = setup_publisher()
    # time.sleep(1)
    # publisher.send("test", "Hello World")
    while True:
        time.sleep(10)
        publisher.send("test", "Huhu")
        pass