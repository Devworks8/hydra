from argparse import ArgumentParser
from multiprocessing import Process
from random import randint
import os
from datetime import datetime, timedelta
import signal
import zmq
from zmq.auth.asyncio import AsyncioAuthenticator
from zmq.eventloop.zmqstream import ZMQStream


from hydra.HydraMessenger.configure import CfgManager
from hydra.HydraMessenger.MessageHeaders.msg_command import *
from hydra.HydraMessenger.Utils.key_monkey import *


class HydraProxy(Process):
    def __init__(self, frontend_port=None, backend_port=None):
        super().__init__()
        self.settings = CfgManager()

        self.frontend_host = self.settings.get(header='service_proxy_frontend_host')[1]
        self.backend_host = self.settings.get(header='service_proxy_backend_host')[1]

        self.frontend_port = self.settings.get(header='service_proxy_frontend_port')[1]
        self.backend_port = self.settings.get(header='service_proxy_backend_port')[1]

        # crypto = True means 'use CurveZMQ'. False means don't.
        self.frontend_crypto = self.settings.get('service_proxy_frontend_crypto')[1]
        self.backend_crypto = self.settings.get('service_proxy_backend_crypto')[1]

        # zap_auth = True means 'use ZAP'. This will restrict connections to clients whose public keys are in
        # the ~/.curve/authorized-clients/ directory. Set this to false to allow any client with the server's
        # public key to connect, without requiring the server to possess each client's public key.
        self.frontend_zap_auth = self.settings.get('service_proxy_frontend_zap')[1]
        self.backend_zap_auth = self.settings.get('service_proxy_backend_zap')[1]

        self.frontend_identities = {}
        self.backend_identities = {}

    def run(self):
        context = zmq.Context()
        # Socket facing clients
        frontend = context.socket(zmq.XREP)

        # Setup crypto:
        if self.frontend_crypto:
            keymonkey = KeyMonkey("HydraProxyFrontend")
            frontend = keymonkey.setupServer(frontend, "tcp://{host}:{port}".format(host=self.frontend_host,
                                                                                    port=self.frontend_port))

        # Setup ZAP:
        """
        if self.zap_auth:
            if not self.crypto:
                print("ZAP requires CurveZMQ (crypto) to be enabled. Exiting.")
                sys.exit(1)

            auth = AsyncioAuthenticator(context)
            # FIXME: Need to supply a list of address' to deny.
            auth.deny([''])
            print("ZAP enabled.\nAuthorizing clients in %s." % keymonkey.authorized_clients_dir)
            auth.configure_curve(domain='*', location=keymonkey.authorized_clients_dir)
            auth.start()
        """

        frontend.bind("tcp://{host}:{port}".format(host=self.frontend_host,
                                                   port=self.frontend_port))
        frontend_stream = ZMQStream(frontend)
        frontend_stream.on_recv(self.frontend_on_recv)

        # Socket facing servers
        backend = context.socket(zmq.XREQ)

        # Setup crypto:
        if self.backend_crypto:
            keymonkey = KeyMonkey("HydraProxyBackend")
            backend = keymonkey.setupServer(backend, "tcp://{host}:{port}".format(host=self.backend_host,
                                                                                  port=self.backend_port))

        backend.bind("tcp://{host}:{port}".format(host=self.backend_host,
                                                  port=self.backend_port))
        backend_stream = ZMQStream(backend)
        backend_stream.on_recv(self.backend_on_recv)

        print("Proxy starting up\n")

        try:
            zmq.proxy(frontend, backend)
            print("Proxy started")

        except Exception as e:
            print("ERROR: Proxy failed to start. : {}".format(e))
            exit(1)

    def frontend_on_recv(self, msg):
        message = msg
        identity = message[0]

        # self.parse_message(message=message)

        self.frontend_identities[identity] = datetime.utcnow()

        msg_type = msg[1]

        # direct reader.
        print("Received message of type %s from client ID %s!" % (msg_type, identity))
        print("%s" % msg)

    def backend_on_recv(self, msg):
        message = msg
        identity = message[0]

        # self.parse_message(message=message)

        self.backend_identities[identity] = datetime.utcnow()

        msg_type = msg[1]

        # direct reader.
        print("Received message of type %s from client ID %s!" % (msg_type, identity))
        print("%s" % msg)

    def close_stale_connections(self, stale_clients):
        for client_id, last_seen in self.client_identities.items():
            if last_seen + timedelta(seconds=10) < datetime.utcnow():
                stale_clients.append(client_id)
            else:
                pass
                # msg = CommandMessage()
                # msg.send(self.server, client_id)

        for client_id in stale_clients:
            print(
                "Client %s has gone quiet. Dropping from list of connected clients." % client_id)
            del self.client_identities[client_id]


class HydraMessageWorker(Process):
    def __init__(self, server=None, backend_port=None):
        super().__init__()
        self.settings = CfgManager()
        self.command_message = CommandMessage()
        self.identity = "%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
        self.backend_host = self.settings.get('service_proxy_backend_host')[1]
        self.backend_port = self.settings.get('service_proxy_backend_port')[1]
        self.crypto = self.settings.get('service_messenger_crypto')[1]

    def run(self):
        context = zmq.Context()
        worker = context.socket(zmq.REP)

        # setup crypto
        if self.crypto:
            keymonkey = KeyMonkey("HydraMessenger")
            worker = keymonkey.setupClient(worker, "tcp://{host}:{port}".format(host=self.backend_host,
                                                                                port=self.backend_port),
                                           "HydraProxyBackend")

        worker.connect("tcp://{host}:{port}".format(host=self.backend_host, port=self.backend_port))

        while True:
            message = worker.recv_multipart()
            worker.send_multipart(message)
            print("Worker %s sending results" % self.identity)
            print(message)


processes = []


def signal_handler(_signum, _frame):
    for process in processes:
        if process.is_alive():
            os.kill(process.pid, signal.SIGKILL)

    for process in processes:
        process.join()


def main():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    """
    parser = ArgumentParser(description='Hydra Proxy and Messenger services.')
    parser.add_argument('procs', type=int,
                        help='Number of message workers to use.')
    parser.add_argument('proxy',
                        help='Proxy server address.')
    parser.add_argument('frontend_port',
                        help='Frontend proxy port for clients to connect to.')
    parser.add_argument('backend_port',
                        help='Backend proxy port for workers to connect to.')

    args = parser.parse_args()

    if args:
        frontend_port = args.frontend_port
        backend_port = args.backend_port
    else:
        frontend_port = None
        backend_port = None

    """

    proxy_proc = HydraProxy()
    proxy_proc.start()
    processes.append(proxy_proc)

    worker_proc = HydraMessageWorker()
    worker_proc.start()
    processes.append(worker_proc)


if __name__ == '__main__':
    main()
