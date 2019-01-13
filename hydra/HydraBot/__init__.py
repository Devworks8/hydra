from argparse import ArgumentParser
import sys
import zmq

from hydra.HydraBot.configure import CfgManager
from hydra.HydraMessenger.Utils.key_monkey import *


def main():
    """
    parser = ArgumentParser(description='Hydra Client')
    parser.add_argument('proxy',
                        help='Proxy server address')
    parser.add_argument('frontend_port',
                        help='Frontend proxy port for clients to connect to.')
    args = parser.parse_args()
    """

    settings = CfgManager()

    crypto = settings.get('service_client_crypto')[1]

    frontend = "tcp://{}:{}".format(settings.get('service_proxy_host')[1],
                                    settings.get('service_proxy_port')[1])

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.LINGER, 0)

    # setup crypto
    if crypto:
        keymonkey = KeyMonkey("Moonbase")
        socket = keymonkey.setupClient(socket, frontend, "HydraProxyFrontend")

    print("Connecting to {}".format(frontend))
    socket.connect(frontend)

    msgs = [b'1', b'2', b'3', b'4']
    while True:
        for msg in msgs:
            socket.send_multipart(msgs)
            poller = zmq.Poller()
            poller.register(socket, zmq.POLLIN)
            if poller.poll(10 * 1000):
                response = socket.recv_multipart()
                print(response)


if __name__ == "__main__":
    main()
