import time
from threading import Thread

import zmq

from messaging.zmq_classes import Subscriber, Publisher, get_own_ips

NUMBERS_PER_IP_OCTET = 255

PORT_RANGE = range(5010, 5020)


def subscribe_test():
    subscriber = setup_subscriber(["test"])
    subscriber.add_additional_ips([("192.168.178.38", PORT_RANGE.start)])
    subscriber.set_connection_timeout(5000)
    subscriber.start()
    while True:
        time.sleep(1)
        print(len(subscriber.ip_and_ports))
        # message = subscriber.recv()
        # print("Got message {}".format(message))


def setup_subscriber(topics):
    subscriber = Subscriber("localhost", PORT_RANGE.start, topics)
    ips = get_possible_network_ips()
    ips_and_ports = [(ip, p) for ip in ips for p in PORT_RANGE]
    subscriber.add_additional_ips(ips_and_ports)
    return subscriber


def get_possible_network_ips():
    all_ips = []
    own_ips = get_own_ips()
    for own_ip in own_ips:
        ip_basis, last_octet = own_ip.rsplit('.', 1)
        is_localhost = ip_basis != "127.0.0"
        ip_range = range(NUMBERS_PER_IP_OCTET) if is_localhost else range(1, 2)
        for i in ip_range:
            ip = ".".join([ip_basis, str(i)])
            all_ips.append(ip)
    return all_ips


def setup_publisher():
    for p in PORT_RANGE:
        try:
            _publisher = Publisher(p)
            _publisher.start()
            print("Publisher started on port", p)
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
    publisher.send_alive_signal(5000)
    publisher2 = setup_publisher()
    publisher2.send_alive_signal(5000)
    time.sleep(1)
    publisher.send("test", "Hello World")
    while True:
        pass
