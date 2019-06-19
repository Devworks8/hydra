from multiprocessing import Process
from random import randint
import os
from time import sleep
import signal
import zmq

from Utils.configure import CfgManager
from MessageHeaders.msg_command import CommandMessage
from Shell.shell import CLIShell
from Utils.clireport import CLIReport


class HydraProxy(Process):
    def __init__(self, frontend_port=None, backend_port=None, reporter=None, settings=None):
        super().__init__()
        self.reporter = reporter
        self.settings = settings

        self.frontend_host = self.settings.get(header='service_proxy_frontend_host')[1]
        self.frontend_port = self.settings.get(header='service_proxy_frontend_port')[1]
        self.frontend_identities = {}

        self.backend_host = self.settings.get(header='service_proxy_backend_host')[1]
        self.backend_port = self.settings.get(header='service_proxy_backend_port')[1]
        self.backend_identities = {}

    def run(self):
        context = zmq.Context()

        try:
            # Socket facing clients
            frontend = context.socket(zmq.XREP)
            frontend.bind("tcp://{host}:{port}".format(host=self.frontend_host,
                                                       port=self.frontend_port))
        except:
            self.reporter.report('ERROR',
                                 'Frontend failed to bind to tcp://{host}:{port}'.format(host=self.frontend_host,
                                                                                         port=self.frontend_port))

        try:
            # Socket facing servers
            backend = context.socket(zmq.XREQ)
            backend.bind("tcp://{host}:{port}".format(host=self.backend_host,
                                                      port=self.backend_port))
        except:
            self.reporter.report('ERROR',
                                 'Backend failed to bind to tcp://{host}:{port}'.format(host=self.backend_host,
                                                                                        port=self.backend_port))

        try:
            zmq.proxy(frontend, backend)

        except:
            self.reporter.report('ERROR', 'Proxy failed to initialize.')


class HydraMessenger(Process):
    def __init__(self, server=None, backend_port=None, reporter=None, settings=None):
        super().__init__()
        self.reporter = reporter
        self.settings = settings
        self.command_message = CommandMessage()
        self.identity = "%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
        self.backend_host = self.settings.get('service_proxy_backend_host')[1]
        self.backend_port = self.settings.get('service_proxy_backend_port')[1]

    def validate_message(self, msg):
        headers = [b'COMMAND', b'REPLY']

        if msg[0] in headers:

            return [b'REPLY', b'yep']
        else:
            return [b'REPLY', b'nope']

    def run(self):
        context = zmq.Context()
        worker = context.socket(zmq.REP)

        try:
            self.reporter.report('INFO', 'Connecting to tcp://{host}:{port}.'.format(host=self.backend_host,
                                                                                    port=self.backend_port))
            worker.connect("tcp://{host}:{port}".format(host=self.backend_host, port=self.backend_port))
            self.reporter.report('INFO', 'Connected.')

        except:
            self.reporter.report('ERROR', 'Failed to connect to tcp://{host}:{port}.'.format(host=self.backend_host,
                                                                                             port=self.backend_port))

        while True:
            message = worker.recv_multipart()

            if message:
                self.validate_message(msg=message)

        results = MessengerWorker(reporter=self.reporter, msg=worker.recv_multipart())

        worker.send_multipart(results.validate_message(results.message))
        print("Worker %s sending results" % self.identity)
        print(results)

    class HydraMessageWorker(Process):
        def __init__(self, reporter, server=None, backend_port=None):
            super().__init__()
            self.settings = CfgManager()
            self.command_message = CommandMessage()
            self.identity = "%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
            self.backend_host = self.settings.get('service_proxy_backend_host')[1]
            self.backend_port = self.settings.get('service_proxy_backend_port')[1]
            self.crypto = self.settings.get('service_messenger_crypto')[1]
            self.reporter = reporter

        def run(self):
            context = zmq.Context()
            worker = context.socket(zmq.REP)

            try:
                worker.connect("tcp://{host}:{port}".format(host=self.backend_host, port=self.backend_port))

            except:


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

    # Args parsing
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

    # Load settings
    settings = CfgManager()

    # Load the reporter
    reporter = CLIReport(settings=settings)

    # Start the proxy
    proxy_proc = HydraProxy(reporter=reporter, settings=settings)
    proxy_proc.start()
    reporter.report('INFO', 'Proxy started.')
    processes.append(proxy_proc)

    # Start the messenger
    messenger_proc = HydraMessenger(reporter=reporter, settings=settings)
    messenger_proc.start()
    reporter.report('INFO', 'Messenger started.')
    processes.append(messenger_proc)

    sleep(2)
    # Start the shell
    CLIShell(settings).cmdloop()


if __name__ == '__main__':
    main()