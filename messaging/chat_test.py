"""Decentralized chat example"""

import argparse
import os
from threading import Thread

# dependency, not in stdlib
from netifaces import interfaces, ifaddresses, AF_INET

import zmq


PORT_RANGE=range(9000, 9010)


def listen(masked, last_octet):
    """listen for messages

    masked is the first three parts of an IP address:

        192.168.1

    The socket will connect to all of X.Y.Z.{1-254}.
    """
    ctx = zmq.Context.instance()
    listener = ctx.socket(zmq.SUB)
    for last in range(1, 255):
        # listener.connect("tcp://{0}.{1}:9000".format(masked, last))
        for port in PORT_RANGE:
            listener.connect("tcp://{0}.{1}:{2}".format(masked, last, port))

    listener.setsockopt(zmq.SUBSCRIBE, b'')
    while True:
        try:
            print(listener.recv_string())
        except (KeyboardInterrupt, zmq.ContextTerminated):
            break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("interface", type=str, help="the network interface",
                        choices=interfaces(),
                        )
    parser.add_argument("user", type=str, default=os.environ['USER'],
                        nargs='?',
                        help="Your username",
                        )
    args = parser.parse_args()
    inet = ifaddresses(args.interface)[AF_INET]
    addr = inet[0]['addr']
    masked, last_octet = addr.rsplit('.', 1)

    ctx = zmq.Context.instance()

    listen_thread = Thread(target=listen, args=(addr, last_octet))
    listen_thread.start()

    bcast = ctx.socket(zmq.PUB)
    # port = input("port:")
    not_found = True
    for port in PORT_RANGE:
        try:
            bcast.bind("tcp://{}:{}".format(args.interface, port))
            print("starting chat on {}:{} ({}.*)".format(args.interface, port, masked))
            not_found = False
            break
        except zmq.ZMQError as e:
            print(e)

    if not_found:
        ctx.term()
        exit(3)

    while True:
        try:
            msg = input()
            print("Sending:", msg)
            bcast.send_string("%s: %s" % (args.user, msg))
        except KeyboardInterrupt:
            break
    bcast.close(linger=0)
    ctx.term()


if __name__ == '__main__':
    main()